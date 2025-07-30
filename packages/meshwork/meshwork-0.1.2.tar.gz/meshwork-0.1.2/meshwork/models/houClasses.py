import re
import uuid

from meshwork.compile.rpsc import (
    parse_index_menu_parameter,
    parse_string_menu_parameter,
)
from meshwork.models.houTypes import (
    fileType,
    folderType,
    parmCondType,
    parmTemplateType,
    rampBasis,
    rampParmType,
    scriptLanguage,
    stringParmType,
)
from meshwork.models.params import (
    BoolParameterSpec,
    ButtonParmTemplateSpec,
    DataParmTemplateSpec,
    EnumParameterSpec,
    FileParameterSpec,
    FloatParameterSpec,
    FloatParmTemplateSpec,
    FolderParmTemplateSpec,
    FolderSetParmTemplateSpec,
    HoudiniParmTemplateSpecType,
    IntParameterSpec,
    IntParmTemplateSpec,
    LabelParmTemplateSpec,
    MenuParmTemplateSpec,
    ParameterSpec,
    ParameterSpecType,
    ParmTemplateSpec,
    RampParameterSpec,
    RampParmTemplateSpec,
    RampPointSpec,
    SeparatorParmTemplateSpec,
    StringParameterSpec,
    StringParmTemplateSpec,
    ToggleParmTemplateSpec,
)


class ParmTemplate:
    id: str = str(uuid.uuid4())
    type: parmTemplateType = parmTemplateType.NoneType
    name: str = "_parm_template_"
    label: str = ""
    category_label: str = ""
    conditionals: dict[parmCondType, str] = {}
    tab_conditionals: dict[parmCondType, str] = {}
    tags: dict[str, str] = {}
    default_expression: list[str] = []
    default_expression_language: list[scriptLanguage] = []
    is_hidden: bool = False
    is_label_hidden: bool = False

    def __init__(
        self, name: str, label: str = "", num_components: int | None = None, **kwargs
    ):
        self.name = name
        self.label = label
        self.num_components = num_components
        for key, value in kwargs.items():
            setattr(self, key, value)

    def hide(self, on: bool) -> None:
        self.is_hidden = on

    def hideLabel(self, on: bool) -> None:
        self.is_label_hidden = on

    def setConditional(self, condType: parmCondType, condition: str) -> None:
        self.conditionals[condType] = condition

    def setHelp(self, help: str) -> None:
        self.help = help

    def setJoinWithNext(self, on: bool) -> None:
        self.join_with_next = on

    def setScriptCallback(self, script: str) -> None:
        self.script_callback = script

    def setScriptCallbackLanguage(self, language: scriptLanguage) -> None:
        self.script_callback_language = language

    def setTabConditional(self, condType: parmCondType, condition: str) -> None:
        self.tab_conditionals[condType] = condition

    def setTags(self, tags: dict[str, str]) -> None:
        self.tags = tags

    def getParmTemplateSpec(self) -> ParmTemplateSpec:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement getParmTemplateSpec()"
        )

    def getParameterSpec(self) -> list[ParameterSpecType]:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement getParmTemplateSpec()"
        )


class SeparatorParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.Separator

    def __init__(self, name: str):
        super().__init__(name, "")

    def getParmTemplateSpec(self) -> SeparatorParmTemplateSpec:
        return SeparatorParmTemplateSpec(**self.__dict__)

    def getParameterSpec(self) -> list[ParameterSpecType]:
        return []


class ButtonParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.Button

    def getParmTemplateSpec(self) -> ButtonParmTemplateSpec:
        return ButtonParmTemplateSpec(**self.__dict__)

    def getParameterSpec(self) -> list[ParameterSpecType]:
        return []


class IntParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.Int

    def getParmTemplateSpec(self) -> IntParmTemplateSpec:
        return IntParmTemplateSpec(**self.__dict__)

    def getParameterSpec(self) -> list[IntParameterSpec]:
        if self.is_hidden:
            return []

        default_value = self.default_value
        if isinstance(default_value, list) and self.num_components == 1:
            default_value = default_value[
                0
            ]  # Convert list to scalar if num_components == 1

        return [IntParameterSpec(default=default_value, **self.__dict__)]


class FloatParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.Float

    def getParmTemplateSpec(self) -> FloatParmTemplateSpec:
        return FloatParmTemplateSpec(**self.__dict__)

    def getParameterSpec(self) -> list[FloatParameterSpec]:
        if self.is_hidden:
            return []

        default_value = self.default_value
        if isinstance(default_value, list) and self.num_components == 1:
            default_value = default_value[
                0
            ]  # Convert list to scalar if num_components == 1

        return [FloatParameterSpec(default=default_value, **self.__dict__)]


class StringParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.String
    menu_items: list[str] = []
    menu_labels: list[str] = []
    menu_use_token: bool = False
    string_type: stringParmType = stringParmType.Regular
    file_type: fileType = fileType.Any

    def setStringType(self, string_type: stringParmType) -> None:
        self.string_type = string_type

    def setFileType(self, file_type: fileType) -> None:
        self.file_type = file_type

    def getParmTemplateSpec(self) -> StringParmTemplateSpec:
        return StringParmTemplateSpec(**self.__dict__)

    def getParameterSpec(self) -> list[StringParameterSpec | FileParameterSpec]:
        if self.is_hidden:
            return []

        if self.menu_items and len(self.menu_items) > 0:
            value = {
                "menu_items": self.menu_items,
                "menu_labels": self.menu_labels,
                "default": self.default_value[0],
                "label": self.label,
                "menu_use_tokens": self.menu_use_token,
            }
            return [parse_string_menu_parameter(value)]
        elif self.string_type == stringParmType.FileReference:
            return [FileParameterSpec(default="", **self.__dict__)]
        else:
            default_value = self.default_value
            if isinstance(default_value, list) and self.num_components == 1:
                default_value = default_value[0]

            return [StringParameterSpec(default=default_value, **self.__dict__)]


class ToggleParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.Toggle

    def getParmTemplateSpec(self) -> ToggleParmTemplateSpec:
        return ToggleParmTemplateSpec(**self.__dict__)

    def getParameterSpec(self) -> list[BoolParameterSpec]:
        if self.is_hidden:
            return []

        return [BoolParameterSpec(default=self.default_value, **self.__dict__)]


class MenuParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.Menu
    menu_items: list[str] = []
    menu_labels: list[str] = []
    menu_use_token: bool = False
    default_value: int = 0

    def getParmTemplateSpec(self) -> MenuParmTemplateSpec:
        return MenuParmTemplateSpec(**self.__dict__)

    def getParameterSpec(self) -> list[EnumParameterSpec]:
        if self.is_hidden:
            return []

        value = {
            "menu_items": self.menu_items,
            "menu_labels": self.menu_labels,
            "default": self.default_value,
            "label": self.label,
            "menu_use_tokens": self.menu_use_token,
        }
        return [parse_index_menu_parameter(value)]


class LabelParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.Label

    def getParmTemplateSpec(self) -> LabelParmTemplateSpec:
        return LabelParmTemplateSpec(**self.__dict__)

    def getParameterSpec(self) -> list[ParameterSpecType]:
        return []


class DataParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.Data

    def getParmTemplateSpec(self) -> DataParmTemplateSpec:
        return DataParmTemplateSpec(**self.__dict__)

    def getParameterSpec(self) -> list[ParameterSpecType]:
        return []


class RampParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.Ramp
    default_points: list[RampPointSpec]
    ramp_parm_type: rampParmType

    def __init__(self, name, label, ramp_part_type, **kwargs):
        self.ramp_parm_type = ramp_part_type
        self.default_points = []
        super().__init__(name, label, None, **kwargs)

    def getParmTemplateSpec(self) -> RampParmTemplateSpec:
        ret = RampParmTemplateSpec(**self.__dict__)
        return ret

    def getParameterSpec(self) -> list[RampParameterSpec]:
        if self.is_hidden:
            return []

        default = self.default_points

        return [RampParameterSpec(default=default, **self.__dict__)]

    def setTags(self, tags: dict[str, str]):
        self.tags = tags
        self.default_points = self.fillRampDefaults()

    def fillRampDefaults(self) -> list[RampPointSpec]:
        is_color_ramp = self.ramp_parm_type == rampParmType.Color
        value_key = "c" if is_color_ramp else "value"
        ramp_str = self.tags.get(
            "rampcolordefault" if is_color_ramp else "rampfloatdefault", ""
        )

        """
        We look for sequences of:
        Npos ( number ) NvalueOrC ( number(s) ) Ninterp ( string )
        For color ramps (c), we expect three floats inside the parentheses for 'c'.
        For float ramps (value), we expect one float.
        (\\d+)pos\\s*\\(\\s*([^)]+)\\)   -> Captures the index (N) and the position (x)
        \1value|c\\s*\\(\\s*([^)]+)\\) -> Using a backreference \1 ensures we match the same index for value/c
        \1interp\\s*\\(\\s*([^)]+)\\)  -> Matches the same index followed by interp
        
        Using a slightly more flexible approach:
        """
        pattern = re.compile(
            r"(\d+)pos\s*\(\s*([^)]*)\)\s*\1"
            + value_key
            + r"\s*\(\s*([^)]*)\)\s*\1interp\s*\(\s*([^)]*)\)"
        )

        points = []
        for match in pattern.finditer(ramp_str):
            pos = float(match.group(2).strip())
            interp_str = (
                match.group(4).strip().lower().replace("-", "").replace(" ", "")
            )
            interp = rampBasis.Constant
            for b in rampBasis:
                # b.value is the string value in the enum, e.g. "MonotoneCubic"
                if b.value.lower() == interp_str:
                    interp = b
                    break

            if is_color_ramp:
                color_vals = list(map(float, match.group(3).strip().split()))
                if len(color_vals) != 3:
                    raise ValueError("Color ramp point must have exactly 3 values")
                points.append(RampPointSpec(pos=pos, c=color_vals, interp=interp))
            else:
                value = float(match.group(3).strip())
                points.append(RampPointSpec(pos=pos, value=value, interp=interp))

        return points


class FolderParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.Folder
    level: int
    parm_templates: list[ParmTemplate]
    folder_type: folderType = folderType.Tabs
    default_value: int = 0
    ends_tab_group: bool = False

    def __init__(self, name, label, num_components=None, **kwargs):
        self.parm_templates = []
        self.level = 1
        super().__init__(name, label, num_components, **kwargs)

    def getParmTemplateSpec(self) -> FolderParmTemplateSpec:
        parmTemplateSpecs: list[ParmTemplateSpec] = []

        for pt in self.parm_templates:
            if isinstance(
                pt,
                (
                    FolderSetParmTemplate,
                    FolderParmTemplate,
                    RampParmTemplate,
                    SeparatorParmTemplate,
                    ButtonParmTemplate,
                    FloatParmTemplate,
                    IntParmTemplate,
                    StringParmTemplate,
                    ToggleParmTemplate,
                    MenuParmTemplate,
                    LabelParmTemplate,
                    DataParmTemplate,
                ),
            ):
                spec: ParmTemplateSpec = (
                    pt.getParmTemplateSpec()
                )  # Explicit type casting
                parmTemplateSpecs.append(spec)

        return FolderParmTemplateSpec(
            name=self.name,
            label=self.label,
            level=self.level,
            folder_type=self.folder_type,
            default_value=self.default_value,
            ends_tab_group=self.ends_tab_group,
            parm_templates=parmTemplateSpecs,
        )

    def getParameterSpec(self) -> list[ParameterSpecType]:
        if self.is_hidden:
            return None

        parameterSpecs: list[ParameterSpecType] = []

        for pt in self.parm_templates:
            if isinstance(
                pt,
                (
                    FolderSetParmTemplate,
                    FolderParmTemplate,
                    RampParmTemplate,
                    SeparatorParmTemplate,
                    ButtonParmTemplate,
                    FloatParmTemplate,
                    IntParmTemplate,
                    StringParmTemplate,
                    ToggleParmTemplate,
                    MenuParmTemplate,
                    LabelParmTemplate,
                    DataParmTemplate,
                ),
            ):
                spec: list[ParameterSpecType] = (
                    pt.getParameterSpec()
                )  # Explicit type casting
                if spec is not None:
                    parameterSpecs.extend(spec)

        return parameterSpecs

    def addParmTemplate(self, parm_template: ParmTemplate):
        parm_template.category_label = self.label
        if isinstance(parm_template, FolderParmTemplate):
            prev = self.parm_templates[-1] if self.parm_templates else None

            def wrapFolderset(pt: FolderParmTemplate):
                fs = FolderSetParmTemplate()
                fs.name = f"FolderSet {self.id}"

                self.parm_templates.append(fs)
                fs.addFolderParmTemplate(pt, self.level + 1)

            if isinstance(prev, FolderSetParmTemplate):
                lastFolder = prev.parm_templates[-1] if prev.parm_templates else None
                if not lastFolder or not lastFolder.ends_tab_group:
                    prev.addFolderParmTemplate(parm_template, self.level + 1)
                else:
                    wrapFolderset(parm_template)
            else:
                wrapFolderset(parm_template)
        else:
            self.parm_templates.append(parm_template)

    def isActualFolder(self) -> bool:
        return self.folder_type not in {
            folderType.ImportBlock,
            folderType.MultiparmBlock,
        }


class FolderSetParmTemplate(ParmTemplate):
    type: parmTemplateType = parmTemplateType.FolderSet
    parm_templates: list[FolderParmTemplate]

    def __init__(self):
        self.parm_templates = []
        super().__init__("")

    def getParmTemplateSpec(self) -> FolderSetParmTemplateSpec:
        parmTemplateSpecs: list[FolderParmTemplateSpec] = []
        for pt in self.parm_templates:
            parmTemplateSpecs.append(pt.getParmTemplateSpec())

        return FolderSetParmTemplateSpec(
            name="", label="", parm_templates=parmTemplateSpecs
        )

    def getParameterSpec(self) -> list[ParameterSpecType]:
        parameterSpecs: list[ParameterSpecType] = []

        for pt in self.parm_templates:
            if isinstance(
                pt,
                (
                    FolderSetParmTemplate,
                    FolderParmTemplate,
                    RampParmTemplate,
                    SeparatorParmTemplate,
                    ButtonParmTemplate,
                    FloatParmTemplate,
                    IntParmTemplate,
                    StringParmTemplate,
                    ToggleParmTemplate,
                    MenuParmTemplate,
                    LabelParmTemplate,
                    DataParmTemplate,
                ),
            ):
                spec: list[ParameterSpecType] = (
                    pt.getParameterSpec()
                )  # Explicit type casting
                if spec is not None:
                    for s in spec:
                        s.category_label = self.label
                        parameterSpecs.append(s)

        return parameterSpecs

    def addFolderParmTemplate(self, parm_template: FolderParmTemplate, level: int = 1):
        parm_template.level = level
        self.parm_templates.append(parm_template)


class ParmTemplateGroup:
    parm_templates: list[ParmTemplate]

    def __init__(self):
        self.parm_templates = []

    def parmTemplates(self):
        return self.parm_templates

    def entries(self):
        return self.parm_templates

    def getParmTemplateSpec(self) -> ParameterSpec:
        params: dict[str, ParameterSpecType] = {}
        params_v2: list[HoudiniParmTemplateSpecType] = []

        for tmpl in self.parm_templates:
            if isinstance(
                tmpl,
                (
                    FolderSetParmTemplate,
                    FolderParmTemplate,
                    RampParmTemplate,
                    SeparatorParmTemplate,
                    ButtonParmTemplate,
                    FloatParmTemplate,
                    IntParmTemplate,
                    StringParmTemplate,
                    ToggleParmTemplate,
                    MenuParmTemplate,
                    LabelParmTemplate,
                    DataParmTemplate,
                ),
            ):
                spec: list[ParameterSpecType] = (
                    tmpl.getParameterSpec()
                )  # Explicit type casting
                if spec is not None:
                    for s in spec:
                        params[s.label] = s

                specv2: HoudiniParmTemplateSpecType = (
                    tmpl.getParmTemplateSpec()
                )  # Explicit type hinting
                params_v2.append(specv2)

        return ParameterSpec(params=params, params_v2=params_v2)

    def append(self, parm_template: ParmTemplate):
        self.addParmTemplate(parm_template)

    def addParmTemplate(self, parm_template: ParmTemplate):
        if parm_template.type == parmTemplateType.Folder:
            prev = self.parm_templates[-1] if self.parm_templates else None

            def wrapFolderset(pt: FolderParmTemplate):
                fs = FolderSetParmTemplate()
                fs.name = f"FolderSet {fs.id}"
                self.parm_templates.append(fs)
                fs.addFolderParmTemplate(pt)

            if isinstance(prev, FolderSetParmTemplate):
                lastFolder = prev.parm_templates[-1] if prev.parm_templates else None
                if not lastFolder or not lastFolder.ends_tab_group:
                    prev.addFolderParmTemplate(parm_template)
                else:
                    wrapFolderset(parm_template)
            else:
                wrapFolderset(parm_template)
        else:
            self.parm_templates.append(parm_template)
