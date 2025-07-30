import asyncio
import logging
import tempfile
from collections.abc import Callable
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from pydantic import ValidationError

from meshwork.automation.adapters import NatsAdapter, RestAdapter
from meshwork.automation.automations import get_default_automations
from meshwork.automation.models import (
    AutomationModel,
    AutomationRequest,
    AutomationRequestResult,
    AutomationsResponse,
    BulkAutomationRequest,
    EventAutomationResponse,
)
from meshwork.automation.publishers import ResultPublisher, SlimPublisher
from meshwork.automation.utils import error_handler, format_exception
from meshwork.config import meshwork_config, update_headers_from_context
from meshwork.models.params import ParameterSet
from meshwork.models.streaming import Error, ProcessStreamItem, Progress
from meshwork.runtime.alerts import AlertSeverity, send_alert
from meshwork.runtime.params import resolve_params

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

tracer = trace.get_tracer(__name__)

process_guid = str(uuid4())


class CoordinatorException(Exception):
    pass


class Worker:
    def __init__(self) -> None:
        self.subject = None
        self.automations: dict[str, AutomationModel] = {}
        self.nats = NatsAdapter()
        self.rest = RestAdapter()

        catalog_provider = AutomationModel(
            path="/mythica/automations",
            provider=self._get_catalog_provider(),
            inputModel=ParameterSet,
            outputModel=AutomationsResponse,
            hidden=True,
        )

        autos = get_default_automations()
        autos.append(catalog_provider)
        self._load_automations(autos)

    def _get_catalog_provider(
            self,
    ) -> Callable[[ParameterSet, ResultPublisher], AutomationsResponse]:
        doer = self

        def impl(
                request: ParameterSet = None, responder: ResultPublisher = None
        ) -> AutomationsResponse:
            ret = {}
            for path, wk in doer.automations.items():
                params_by_name = {}
                for param in wk.inputModel.get_parameter_specs():
                    params_by_name[param.name] = param

                # read a script Interface model if one exists:
                if wk.interfaceModel:
                    for param in wk.interfaceModel():
                        params_by_name[param.name] = param

                # Get the parameter spec
                inputs = [param for param in params_by_name.values()]

                ret.update(
                    {
                        path: {
                            "input": inputs,
                            "output": wk.outputModel.model_json_schema(),
                            "hidden": wk.hidden,
                        }
                    }
                )

            return AutomationsResponse(automations=ret)

        return impl

    def start(self, subject: str, automations: list[AutomationModel]) -> None:
        self._load_automations(automations)
        self.subject = subject
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.nats.listen(subject, self._get_executor()))
        task.add_done_callback(error_handler(log))

        # Run loop until canceled or an exception escapes
        loop.run_forever()

    def start_web(self, automations: list[AutomationModel]) -> FastAPI:
        self._load_automations(automations)
        return self._get_web_executor()

    def _load_automations(self, automations: list[AutomationModel]):
        """Function to dynamically discover and register workers in a container"""
        try:
            log.debug("Start Registering automations")
            for automation in automations:
                if type(automation) is not AutomationModel:
                    automation = AutomationModel(**automation)
                self.automations[automation.path] = automation
                log.debug(f"Registered automations for '{automation.path}'")
            log.debug("End Registering automations")
        except Exception as e:
            log.error(f"Failed to register automations: {format_exception(e)}")

    def _get_executor(self):
        """
        Execute an automation by trying to find a route that maps
        to the path defined in the payload. If a route is defined,
        data is sent to the route provider, along with a callback for
        reporting status
        """
        doer = self

        async def implementation(json_payload: dict) -> tuple[bool, ProcessStreamItem]:
            with tracer.start_as_current_span("worker.execution") as span:
                ret_data = None
                span.set_attribute(
                    "worker.started", datetime.now(timezone.utc).isoformat()
                )
                try:
                    auto_request = AutomationRequest(**json_payload)

                    trace_data = {
                        "correlation": auto_request.correlation,
                        "job_id": auto_request.job_id if auto_request.job_id else "",
                    }
                    span.set_attributes(trace_data)
                    if len(auto_request.data) == 1 and "params" in auto_request.data:
                        # If it only contains "params", replace payload.data with its content
                        auto_request.data = auto_request.data["params"]

                    log_str = f"correlation: {auto_request.correlation}, work:{auto_request.path}, job_id: {auto_request.job_id}, data: {auto_request.data}"

                except Exception as e:
                    msg = f"Validation error - {json_payload} - {format_exception(e)}"
                    log.error(msg)
                    await doer.nats.post("result", Error(error=msg).model_dump())
                    return False, Error(error=msg)

                # Run the worker
                publisher = None
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        publisher = ResultPublisher(
                            auto_request, self.nats, self.rest, tmpdir
                        )
                        publisher.result(Progress(progress=0))

                        worker = doer.automations[auto_request.path]
                        inputs = worker.inputModel(**auto_request.data)
                        inputs.worker = self.subject
                        api_url = meshwork_config().api_base_uri
                        resolve_params(
                            api_url,
                            tmpdir,
                            inputs,
                            headers=update_headers_from_context(),
                        )
                        with tracer.start_as_current_span("job.execution") as job_span:
                            job_span.set_attribute(
                                "job.started", datetime.now(timezone.utc).isoformat()
                            )
                            ret_data: ProcessStreamItem = worker.provider(
                                inputs, publisher
                            )
                            job_span.set_attribute(
                                "job.completed", datetime.now(timezone.utc).isoformat()
                            )

                        publisher.result(ret_data)
                    publisher.result(Progress(progress=100), complete=True)
                    return True, ret_data
                except Exception as e:
                    msg = f"Executor error - {log_str} - {format_exception(e)}"
                    if publisher:
                        publisher.result(Error(error=msg), complete=True)
                    log.error(msg)
                    span.record_exception(e)
                    return False, Error(error=msg)
                finally:
                    span.set_attribute(
                        "worker.completed", datetime.now(timezone.utc).isoformat()
                    )
                    if ret_data and ret_data.job_id:
                        span.set_attribute("job_id", ret_data.job_id)
                    log.info("Job finished %s", auto_request.correlation)

        async def coordinator(json_payload: dict):
            headers: dict = json_payload.get("telemetry_context", {})
            # Init telemetry_context before root trace
            telemetry_context = TraceContextTextMapPropagator().extract(carrier=headers)
            api_url = meshwork_config().api_base_uri
            auth_token = None
            event_id = json_payload.get("event_id", None)

            with tracer.start_as_current_span(
                    "coordinator", context=telemetry_context
            ) as span:
                job_res = EventAutomationResponse()
                try:
                    if json_payload.get("is_bulk_processing", False):
                        requests: list[dict] = json_payload["requests"]
                        job_res.is_bulk_processing = True
                    else:
                        requests: list[dict] = [json_payload]

                    if job_res.is_bulk_processing:
                        # validate request for the bulk processing
                        BulkAutomationRequest(**json_payload)

                    auth_token = requests[0].get("auth_token", None)

                    for job_request in requests:
                        processed, result = await implementation(job_request)
                        job_res.request_result.append(
                            AutomationRequestResult(
                                processed=processed,
                                request=AutomationRequest(**job_request),
                                result=result.model_dump() if result else None,
                            )
                        )
                    log.info(
                        "All jobs processed for event_id: %s, job.request_result: %s",
                        event_id,
                        [
                            f"correlation: {i.request.correlation}, is_processed: {i.processed}"
                            for i in job_res.request_result
                        ],
                    )
                except (CoordinatorException, ValidationError) as ex:
                    job_res.request_result.append(
                        AutomationRequestResult(
                            processed=False,
                            result=Error(error=ex.__str__()).model_dump(),
                        )
                    )
                    log.exception(ex)
                    span.record_exception(ex)
                    send_alert(
                        f"Event automation failed for event_id: {event_id}",
                        AlertSeverity.CRITICAL,
                    )
                    return
                finally:
                    await self.process_items_result(
                        job_res=job_res,
                        api_url=api_url,
                        auth_token=auth_token,
                        event_id=event_id,
                    )

        return coordinator

    async def process_items_result(
            self,
            job_res: EventAutomationResponse,
            api_url: str,
            auth_token: str,
            event_id: str | None = None,
    ) -> None:
        updated_headers = update_headers_from_context()

        success = True
        if event_id:
            for res in job_res.request_result:
                log.info("Item type: %s", res.result.get("item_type", ""))
                item = res.result
                if not res.processed:
                    success = False
                elif item.get("item_type", "") == "error":
                    success = False
                elif (
                        item.get("item_type", "") == "job_def"
                        and item.get("job_def_id") is None
                ):
                    success = False
                elif item.get("item_type", "") == "job_defs":
                    if item.get("job_definitions") is None:
                        success = False
                    for job_definition in item.get("job_definitions", []):
                        if job_definition.get("job_def_id") is None:
                            success = False
                elif (
                        item.get("item_type", "") == "cropped_image"
                        and item.get("file_id") is None
                ):
                    success = False

                if not success:
                    log.error("The event status request failed: item_data-%s", item)
                    break

            job_res.processed = success
            response = self.rest.post(
                f"{api_url}/events/processed/{event_id}/",
                job_res.model_dump(by_alias=True, exclude_none=False),
                auth_token,
                headers=updated_headers,
            )
            if not response:
                log.error(
                    "The event status request failed: item_data-%s", item.model_dump()
                )

    def _get_web_executor(self):
        """
        Start a FastAPI app dynamically based on the workers list.
        """
        app = FastAPI(title="Automation API", description="Mythica Automation API")

        @app.options("/")
        async def preflight():
            """
            Handles CORS preflight requests.
            """
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "3600",
            }
            return JSONResponse(content=None, status_code=204, headers=headers)

        @app.post("/")
        async def automation_request(request: Request):
            """
            Handles automation requests and dispatches to appropriate automation function.
            """
            # Set CORS headers
            headers = {"Access-Control-Allow-Origin": "*"}

            # Parse request data
            request_data = await request.json()
            request_data["process_guid"] = process_guid
            auto_request = AutomationRequest(**request_data)

            # Find the appropriate worker by path
            automation = self.automations[auto_request.path]

            if not automation:
                return JSONResponse(
                    content={
                        "correlation": auto_request.correlation,
                        "result": {
                            "error": f"No automation found for path '{auto_request.path}'"
                        },
                    },
                    status_code=404,
                    headers=headers,
                )

            # Convert request data to the input model
            input_model_class = automation.inputModel
            try:
                input_data = input_model_class(
                    **auto_request.data
                )  # Validate and parse the input
            except Exception as e:
                log.error(f"Automation failed: {format_exception(e)}")
                return JSONResponse(
                    content={
                        "correlation": auto_request.correlation,
                        "result": {"error": auto_request.data},
                    },
                    status_code=422,
                    headers=headers,
                )

            # Execute the worker's provider function
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    api_url = meshwork_config().api_base_uri
                    resolve_params(api_url, tmpdir, input_data)
                    publisher = SlimPublisher(
                        request=auto_request, rest=self.rest, directory=tmpdir
                    )
                    result = automation.provider(input_data, publisher)
                    publisher.result(result)

            except Exception as e:
                log.error(f"Automation failed: {format_exception(e)}")
                return JSONResponse(
                    content={
                        "correlation": auto_request.correlation,
                        "result": {
                            "error": f"Automation failed: {str(e)}"
                        },
                    },
                    status_code=500,
                    headers=headers,
                )

            # Return result
            return JSONResponse(
                content={
                    "correlation": auto_request.correlation,
                    "result": result.model_dump(),
                },
                status_code=200,
                headers=headers,
            )

        return app
