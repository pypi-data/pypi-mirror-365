import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.datastructures import UploadFile

from flowscale import FlowscaleAPI

load_dotenv()

app = FastAPI(
    title="Flowscale SDK FastAPI Example",
    description="FastAPI server demonstrating all Flowscale SDK functions",
    version="1.0.0",
)

# Initialize Flowscale API client
api_key = os.getenv("FLOWSCALE_API_KEY")
api_url = os.getenv("FLOWSCALE_API_URL")

if not api_key or not api_url:
    raise ValueError(
        "FLOWSCALE_API_KEY and FLOWSCALE_API_URL environment variables are required"
    )

flowscale_client = FlowscaleAPI(api_key=api_key, base_url=api_url)


# Pydantic models for request/response
class ExecuteWorkflowRequest(BaseModel):
    workflow_id: str
    data: dict[str, Any]
    group_id: str | None = None


class ExecuteWorkflowAsyncRequest(BaseModel):
    workflow_id: str
    data: dict[str, Any]
    group_id: str | None = None
    timeout_ms: int = 600000  # 10 minutes in milliseconds
    poll_interval_ms: int = 2000  # 2 seconds in milliseconds


class CancelRunRequest(BaseModel):
    run_id: str


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Flowscale SDK FastAPI Example",
        "endpoints": {
            "health": "/health - Check ComfyUI health status",
            "queue": "/queue - Get workflow queue status",
            "execute": "/execute - Execute workflow immediately",
            "execute_async": "/execute_async - Execute workflow and wait for completion",
            "execute_with_image": "/execute_with_image - Execute workflow with image upload",
            "output": "/output/{filename} - Get workflow output by filename",
            "cancel": "/cancel - Cancel a running workflow",
            "run": "/run/{run_id} - Get run details",
            "runs": "/runs - List runs with pagination, sorting, and optional group filtering",
        },
    }


@app.get("/health")
async def check_health():
    """Check the health status of all ComfyUI instances"""
    try:
        health_status = flowscale_client.check_health()
        return JSONResponse(content=health_status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/queue")
async def get_queue():
    """Get the queue data for all ComfyUI instances"""
    try:
        queue_data = flowscale_client.get_queue()
        return JSONResponse(content=queue_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/execute")
async def execute_workflow(request: ExecuteWorkflowRequest):
    """Execute a workflow immediately"""
    try:
        result = flowscale_client.execute_workflow(
            workflow_id=request.workflow_id,
            data=request.data,
            group_id=request.group_id,
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/execute_async")
async def execute_workflow_async(request: ExecuteWorkflowAsyncRequest):
    """Execute a workflow and wait for completion"""
    try:
        result = flowscale_client.execute_workflow_async(
            workflow_id=request.workflow_id,
            data=request.data,
            group_id=request.group_id,
            timeout_ms=request.timeout_ms,
            poll_interval_ms=request.poll_interval_ms,
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/execute_with_image")
async def execute_workflow_with_image(
    request: Request,
    workflow_id: str = Form(...),
    group_id: str | None = Form(None),
    timeout_ms: int = Form(600000),  # 10 minutes in milliseconds
    poll_interval_ms: int = Form(2000),  # 2 seconds in milliseconds
    additional_data: str | None = Form("{}"),
):
    """Execute a workflow with image upload and wait for completion.
    Supports dynamic image parameter names (e.g., image_35728) and multiple images."""
    try:
        # Parse additional data if provided
        import json

        extra_data = json.loads(additional_data) if additional_data else {}

        # Get form data to extract dynamic image parameters
        form_data = await request.form()

        # Create data dictionary starting with extra data
        data = {**extra_data}

        # Process all form fields to find image uploads
        for field_name, field_value in form_data.items():
            # Skip non-image fields that are already handled
            if field_name in [
                "workflow_id",
                "group_id",
                "timeout_ms",
                "poll_interval_ms",
                "additional_data",
            ]:
                continue

            # Check if this is an image upload (UploadFile object)
            if isinstance(field_value, UploadFile):
                try:
                    # Use the file object directly - FlowscaleAPI should handle it
                    # First, ensure we're at the beginning of the file
                    await field_value.seek(0)
                    # Use the file object directly - it should have a read method
                    data[field_name] = field_value.file
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Error processing file upload for field '{field_name}': {str(e)}",
                    ) from e
            else:
                # This is a regular form field - add it to data
                data[field_name] = field_value

        for key, value in data.items():
            print(f"  {key}: {type(value)}")
            if hasattr(value, "read"):
                print(f"    - has read method: {callable(value.read)}")

        result = flowscale_client.execute_workflow_async(
            workflow_id=workflow_id,
            data=data,
            group_id=group_id,
            timeout_ms=timeout_ms,
            poll_interval_ms=poll_interval_ms,
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/output/{filename}")
async def get_output(filename: str):
    """Get workflow output by filename"""
    try:
        output = flowscale_client.get_output(filename)
        if output is None:
            raise HTTPException(status_code=204, detail="No output found")
        return JSONResponse(content=output)
    except Exception as e:
        if "No output found" in str(e):
            raise HTTPException(status_code=204, detail=str(e)) from e
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/cancel")
async def cancel_run(request: CancelRunRequest):
    """Cancel a running workflow"""
    try:
        result = flowscale_client.cancel_run(request.run_id)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/run/{run_id}")
async def get_run(run_id: str):
    """Get detailed information about a specific run"""
    try:
        run_details = flowscale_client.get_run(run_id)
        return JSONResponse(content=run_details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/runs")
async def get_runs(
    group_id: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 10,
):
    """Get list of runs with pagination, sorting, and optional group filtering"""
    try:
        runs = flowscale_client.get_runs(
            group_id=group_id,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )
        return JSONResponse(content=runs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8989)
