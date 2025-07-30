import enum
from datetime import datetime
from typing import Annotated, Any, Generic, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from smartspace.enums import (
    BlockClass,
    BlockScope,
    ChannelEvent,
    ChannelState,
    FlowVariableAccess,
)
from smartspace.utils.utils import _get_type_adapter


class File(BaseModel):
    model_config = ConfigDict(populate_by_name=True, title="File")
    id: str
    name: str

    def as_info(self, length: int):
        return FileWithInfoNew(id=self.id, name=self.name, length=length)


class FileWithContent(File):
    model_config = ConfigDict(populate_by_name=True, title="FileWithContent")
    content: str

    def as_info(self, length: int | None = None):
        return FileWithInfoNew(
            id=self.id,
            name=self.name,
            length=length if length is not None else len(self.content),
        )

    def get_content(self) -> str:
        return self.content


class FileWithInfoNew(File):
    model_config = ConfigDict(populate_by_name=True, title="FileInfo")
    length: int


class WebDataInfoBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, title="WebDataInfo")
    id: str
    url: str
    title: str


class WebDataInfoWithSnippet(WebDataInfoBaseModel):
    model_config = ConfigDict(populate_by_name=True, title="WebDataInfo")
    snippet: str


class WebDataInfoWithSummary(WebDataInfoBaseModel):
    model_config = ConfigDict(populate_by_name=True, title="WebDataInfo")
    summary: str


class WebDataInfoComplete(WebDataInfoBaseModel):
    model_config = ConfigDict(populate_by_name=True, title="WebDataInfo")
    snippet: str
    summary: str
    metadata: dict[str, Any]


class WebDataBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, title="WebData")
    content: str
    url: str
    title: str
    id: str | None = None

    def get_content(self) -> str:
        return self.content

    def as_info(self):
        return WebDataInfoBaseModel(
                    id=self.id ,
                    title=self.title,
                    url=self.url,
                )

class WebSiteDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True, title="WebData")
    content: str
    url: str
    title: str

    def get_content(self) -> str:
        return self.content


class WebDataWithSnippet(WebDataBaseModel):
    model_config = ConfigDict(populate_by_name=True, title="WebData")
    snippet: str

    def as_info(self):
        return WebDataInfoWithSnippet(
            id=self.id or str(UUID()),
            title=self.title,
            url=self.url,
            snippet=self.snippet,
        )


class WebDataWithSummary(WebDataBaseModel):
    model_config = ConfigDict(populate_by_name=True, title="WebData")
    summary: str

    def as_info(self):
        return WebDataInfoWithSummary(
            id=self.id or str(UUID()),
            title=self.title,
            url=self.url,
            summary=self.summary,
        )


class WebDataComplete(WebDataBaseModel):
    model_config = ConfigDict(populate_by_name=True, title="WebData")
    snippet: str
    summary: str
    id: str = Field(default=...)
    metadata: dict[str, Any]

    def as_info(self):
        return WebDataInfoComplete(
            id=self.id or str(UUID()),
            title=self.title,
            url=self.url,
            snippet=self.snippet,
            summary=self.summary,
            metadata=self.metadata,
        )


class GoogleSearchResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    items: list[WebDataWithSnippet]
    metadata: dict[str, Any] = Field(default_factory=dict)


class Chunk_v2(BaseModel):
    model_config = ConfigDict(populate_by_name=True, title="Chunk")
    index: int
    position: int
    content: str
    name: str


class GenericParentInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str
    object_structure: dict[str, Any]


class GenericParent(BaseModel):
    @staticmethod
    def get_schema(value):
        if isinstance(value, dict):
            return {k: GenericParent.get_schema(v) for k, v in value.items()}
        elif isinstance(value, list):
            if value:
                return {"__list__": GenericParent.get_schema(value[0])}
            else:
                return {"__list__": "unknown"}
        else:
            return {"__type__": type(value).__name__}

    model_config = ConfigDict(extra="allow", title="MiscParent")
    id: str
    content: Any

    def get_content(self) -> Any:
        return self.content

    def as_info(self):
        return GenericParentInfo(
            id=self.id, object_structure=self.get_schema(self.content)
        )


class GenericChunk(Chunk_v2):
    model_config = ConfigDict(populate_by_name=True, title="MiscChunk")
    parentInfo: GenericParentInfo


class WebDataChunk(Chunk_v2):
    model_config = ConfigDict(populate_by_name=True, title="WebDataChunk")
    parentInfo: (
        WebDataInfoComplete
        | WebDataInfoWithSnippet
        | WebDataInfoWithSummary
        | WebDataInfoBaseModel
    )


class FileChunk(Chunk_v2):
    model_config = ConfigDict(populate_by_name=True, title="FileChunk")
    parentInfo: FileWithInfoNew


class WebChunks(BaseModel):
    model_config = ConfigDict(populate_by_name=True, title="WebChunks")
    parent: WebDataComplete | WebDataWithSummary | WebDataWithSnippet | WebDataBaseModel
    chunks: list[WebDataChunk]


class FileChunks(BaseModel):
    model_config = ConfigDict(populate_by_name=True, title="FileChunks")
    parent: FileWithContent
    chunks: list[FileChunk]


class GenericChunks(BaseModel):
    model_config = ConfigDict(populate_by_name=True, title="GenericChunks")
    parent: GenericParent
    chunks: list[GenericChunk]


# === Chunks Union Type ===
Chunks = Union[WebChunks,FileChunks,  GenericChunks]


class PinType(enum.Enum):
    SINGLE = "Single"
    LIST = "List"
    DICTIONARY = "Dictionary"


class PortType(enum.Enum):
    SINGLE = "Single"
    LIST = "List"
    DICTIONARY = "Dictionary"


class BlockPinRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    port: str
    pin: str


class InputPinInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    metadata: dict[str, Any] = {}
    sticky: bool
    json_schema: Annotated[dict[str, Any], Field(alias="schema")]
    generics: dict[
        str, BlockPinRef
    ]  # Name of the generic, like OutputT, and then a reference to the input on this block that defines the schema
    type: PinType
    required: bool
    default: Any
    channel: bool
    virtual: bool


class OutputPinInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    metadata: dict[str, Any] = {}
    json_schema: Annotated[dict[str, Any], Field(alias="schema")]
    generics: dict[
        str, BlockPinRef
    ]  # Name of the generic, like OutputT, and then a reference to the input on this block that defines the schema
    type: PinType
    channel: bool
    channel_group_id: Annotated[str | None, Field(alias="channelGroupId")]


class PortInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    metadata: dict[str, Any] = {}
    inputs: dict[str, InputPinInterface]
    outputs: dict[str, OutputPinInterface]
    type: PortType
    is_function: Annotated[bool, Field(alias="isFunction")]


class StateInterface(BaseModel):
    """
    scope_pins is a list of pins that set the scope of the state.
    When any function runs, state is set on the component.
    And for each run that the scope_pins have the same values, that state will be reused
    """

    model_config = ConfigDict(populate_by_name=True)

    metadata: dict[str, Any] = {}
    scope: list[BlockPinRef]
    default: Any


class FunctionInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class BlockInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    block_class: Annotated[BlockClass | None, Field(alias="class")] = None
    metadata: dict[str, Any] = {}
    scopes: list[BlockScope] | None = None
    ports: dict[str, PortInterface]
    state: dict[str, StateInterface]


class FlowContext(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    workspace: "SmartSpaceWorkspace | None"
    message_history: "list[ThreadMessage] | None"


class BlockErrorModel(BaseModel):
    message: str
    data: Any


class InputValue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    target: BlockPinRef
    value: Any


class OutputValue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: BlockPinRef
    value: Any


class StateValue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    state: str
    value: Any


class PinRedirect(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: BlockPinRef
    target: BlockPinRef


class ThreadMessageResponseSource(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    index: int = 0
    uri: str = ""


class ThreadMessageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    content: str = ""
    sources: list[ThreadMessageResponseSource] | None = None


class ContentItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    image: File | None = None
    text: str | None = None


class ThreadMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    content: str | None = None
    content_list: Annotated[list[ContentItem] | None, Field(alias="contentList")] = None
    response: ThreadMessageResponse
    created_at: Annotated[datetime, Field(..., alias="createdAt")]
    created_by: Annotated[str, Field(..., alias="createdBy")]


class SmartSpaceDataSetProperty(BaseModel):
    name: str
    description: str | None = None


class SmartSpaceDataSet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    properties: list[SmartSpaceDataSetProperty]


class SmartSpaceDataSpace(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    datasets: list[SmartSpaceDataSet] = []


class SmartSpaceWorkspace(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    data_spaces: Annotated[list[SmartSpaceDataSpace], Field(alias="dataSpaces")] = []
    flow_definition: Annotated[
        "FlowDefinition | None", Field(alias="flowDefinition")
    ] = None

    @property
    def dataspace_ids(self) -> list[UUID]:
        return [dataspace.id for dataspace in self.data_spaces]

    @property
    def datasets(self) -> list[SmartSpaceDataSet]:
        all_datasets = [
            dataset for dataspace in self.data_spaces for dataset in dataspace.datasets
        ]
        result: list[SmartSpaceDataSet] = []

        for dataset in all_datasets:
            if not any([d.id == dataset.id for d in result]):
                result.append(dataset)

        return result


class FlowPinRef(BaseModel):
    """
    When referencing block pins, block, port, and pin must be set
    When referencing a constant, only block must be set
    """

    model_config = ConfigDict(populate_by_name=True)

    node: str
    port: str | None = None
    pin: str | None = None


class Connection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: FlowPinRef
    target: FlowPinRef


class FlowBlockConstant(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    target: BlockPinRef
    value: Any


class FlowBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    version: str
    description: str | None = None
    constants: list[FlowBlockConstant] = []
    dynamic_ports: Annotated[list[str], Field(alias="dynamicPorts")] = []
    dynamic_output_pins: Annotated[
        list[BlockPinRef], Field(alias="dynamicOutputPins")
    ] = []
    dynamic_input_pins: Annotated[
        list[BlockPinRef], Field(alias="dynamicInputPins")
    ] = []


class FlowConstant(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: Any


class FlowInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    json_schema: Annotated[dict[str, Any], Field(alias="schema")]

    @classmethod
    def from_type(cls, t: type) -> "FlowInput":
        return FlowInput(json_schema=_get_type_adapter(t).json_schema())


class FlowOutput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    json_schema: Annotated[dict[str, Any], Field(alias="schema")]

    @classmethod
    def from_type(cls, t: type) -> "FlowOutput":
        return FlowOutput(json_schema=_get_type_adapter(t).json_schema())


class FlowVariable(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    json_schema: Annotated[dict[str, Any], Field(alias="schema")]
    access: FlowVariableAccess = FlowVariableAccess.NONE


class FlowDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    inputs: dict[str, FlowInput]
    outputs: dict[str, FlowOutput]
    variables: dict[str, FlowVariable]
    constants: dict[str, FlowConstant]
    blocks: dict[str, FlowBlock]

    connections: list[Connection]

    def get_source_node(
        self, node: str
    ) -> FlowBlock | FlowInput | FlowConstant | FlowVariable | None:
        return (
            self.inputs.get(node, None)
            or self.constants.get(node, None)
            or self.blocks.get(node, None)
            or self.variables.get(node, None)
        )

    def get_target_node(
        self, node: str
    ) -> FlowBlock | FlowOutput | FlowVariable | None:
        return (
            self.outputs.get(node, None)
            or self.blocks.get(node, None)
            or self.variables.get(node, None)
        )


class BlockRunData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    version: str
    function: str
    context: FlowContext | None
    state: list[StateValue] | None
    inputs: list[InputValue] | None
    dynamic_ports: list[str] | None
    dynamic_output_pins: list[BlockPinRef] | None
    dynamic_input_pins: list[BlockPinRef] | None


class BlockRunMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    outputs: list[OutputValue] = []
    inputs: list[InputValue] = []
    redirects: list[PinRedirect] = []
    states: list[StateValue] = []


ChannelT = TypeVar("ChannelT")


class InputChannel(BaseModel, Generic[ChannelT]):
    model_config = ConfigDict(populate_by_name=True)

    state: ChannelState
    event: ChannelEvent | None
    data: ChannelT | None


class OutputChannelMessage(BaseModel, Generic[ChannelT]):
    model_config = ConfigDict(populate_by_name=True)

    event: ChannelEvent | None
    data: ChannelT | None
