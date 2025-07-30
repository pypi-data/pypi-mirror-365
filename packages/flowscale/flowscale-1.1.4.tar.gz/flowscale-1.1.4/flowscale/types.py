from typing import Any, TypedDict


class ContainerStatus(TypedDict):
    container: str
    status: str


class HealthCheckResponse(TypedDict):
    status: str
    data: list[ContainerStatus]


class QueueItem(TypedDict):
    container: str
    queue: dict[str, Any]


class QueueResponse(TypedDict):
    status: str
    data: list[QueueItem]


class ExecuteWorkflowResponseData(TypedDict):
    run_id: str
    workflow_id: str


class ExecuteWorkflowResponse(TypedDict):
    status: str
    data: ExecuteWorkflowResponseData


class GetOutputResponseData(TypedDict):
    download_url: str
    generation_status: str


class GetOutputResponse(TypedDict):
    status: str
    data: GetOutputResponseData


class InputItem(TypedDict):
    path: str
    value: str
    s3_key: str | None
    url: str | None


class OutputItem(TypedDict):
    filename: str
    s3_key: str | None
    url: str | None


class RunDetail(TypedDict):
    _id: str
    team_id: str
    workflow_id: str
    group_id: str | None
    status: str
    inputs: list[InputItem]
    outputs: list[OutputItem]
    created_at: str
    started_at: str | None
    completed_at: str | None


class RunDetailResponse(TypedDict):
    status: str
    data: RunDetail


class RunListResponseMeta(TypedDict):
    sort_by: str
    sort_order: str
    page: int
    group_id: str | None
    page_size: int
    total_count: int
    total_pages: int


class RunListResponseData(TypedDict):
    runs: list[RunDetail]


class RunListResponse(TypedDict):
    status: str
    meta: RunListResponseMeta
    data: RunListResponseData


class CancelRunResponse(TypedDict):
    status: str
    data: str


class ErrorResponse(TypedDict):
    status: str
    errors: str


class ExecuteWorkflowAsyncOutput(TypedDict):
    run_id: str
    workflow_id: str
    outputs: dict[str, GetOutputResponse]
    total_outputs: int
    status: str
