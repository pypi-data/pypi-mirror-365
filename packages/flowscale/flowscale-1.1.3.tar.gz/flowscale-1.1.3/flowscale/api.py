import logging
import mimetypes
import os
import time
from typing import Any, NoReturn

import requests

from .types import (
    CancelRunResponse,
    ExecuteWorkflowAsyncOutput,
    ExecuteWorkflowResponse,
    GetOutputResponse,
    HealthCheckResponse,
    QueueResponse,
    RunDetailResponse,
    RunListResponse,
)

# Configure logging
logging.basicConfig(level=logging.INFO)


class FlowscaleAPI:
    def __init__(self, api_key: str, base_url: str):
        """
        Initialize the Flowscale API client.

        Args:
            api_key: The API key for authentication
            base_url: The base URL for the API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"X-API-KEY": api_key}

    def check_health(self) -> HealthCheckResponse:
        """
        Checks the health status of all ComfyUI instances within the specified cluster.

        Returns:
            The health status response
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/comfy/health", headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)

    def get_queue(self) -> QueueResponse:
        """
        Retrieves the queue data for all ComfyUI instances in the cluster.

        Returns:
            The queue status response
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/comfy/queue", headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)

    def execute_workflow(
        self, workflow_id: str, data: dict[str, Any], group_id: str | None = None
    ) -> ExecuteWorkflowResponse:
        """
        Executes a specified workflow by processing dynamic form data.

        Args:
            workflow_id: The ID of the workflow to execute
            data: Form data including text fields and file uploads
            group_id: Optional group ID

        Returns:
            The workflow execution response
        """
        files = {}
        form_data = {}
        opened_files = []

        try:
            # Process the data into files and form fields
            for key, value in data.items():
                if hasattr(value, "read") and callable(value.read):
                    # It's a file-like object
                    files[key] = value
                elif isinstance(value, list | tuple):
                    # Handle arrays (for multiple files)
                    for i, item in enumerate(value):
                        if hasattr(item, "read") and callable(item.read):
                            files[f"{key}_{i}"] = item
                        else:
                            form_data[f"{key}_{i}"] = item
                elif isinstance(value, str) and os.path.isfile(value):
                    # It's a file path
                    file_name = os.path.basename(value)
                    file_obj = open(value, "rb")
                    opened_files.append(file_obj)
                    files[key] = (
                        file_name,
                        file_obj,
                        mimetypes.guess_type(value)[0] or "application/octet-stream",
                    )
                else:
                    # It's a regular value
                    form_data[key] = value

            # Construct the URL with query parameters
            url = f"{self.base_url}/api/v1/runs?workflow_id={workflow_id}"
            if group_id:
                url += f"&group_id={group_id}"

            response = requests.post(
                url, headers=self.headers, data=form_data, files=files
            )
            response.raise_for_status()

            return response.json()

        except Exception as error:
            self._handle_error(error)
        finally:
            # Always close opened files
            for file_obj in opened_files:
                try:
                    file_obj.close()
                except Exception as e:
                    logging.error(f"Failed to close file: {file_obj}: {e}")

    def execute_workflow_async(
        self,
        workflow_id: str,
        data: dict[str, Any],
        group_id: str | None = None,
        timeout_ms: int = 600000,
        poll_interval_ms: int = 2000,
    ) -> ExecuteWorkflowAsyncOutput | None:
        """
        Executes a workflow and polls for its output until completion or timeout.

        Args:
            workflow_id: The ID of the workflow to execute
            data: Form data including text fields and file uploads
            group_id: Optional group ID
            timeout_ms: Maximum time to wait for results in milliseconds (default: 600000 = 10 minutes)
            poll_interval_ms: Time between polling attempts in milliseconds (default: 2000 = 2 seconds)

        Returns:
            ExecuteWorkflowAsyncOutput containing all output data or None if no outputs are found within timeout

        Raises:
            Exception: If the execution times out or encounters an error
        """
        # Convert milliseconds to seconds for internal use
        timeout_seconds = timeout_ms / 1000
        poll_interval_seconds = poll_interval_ms / 1000

        # Execute the workflow
        execution_response = self.execute_workflow(workflow_id, data, group_id)

        # Get the run_id from the response
        if not execution_response or "data" not in execution_response:
            raise Exception("No data in execution response")

        response_data = execution_response["data"]
        if "run_id" not in response_data:
            raise Exception("No run_id in execution response")

        run_id = response_data["run_id"]
        start_time = time.time()

        logging.info(f"Starting polling for run {run_id}")

        # Track completed outputs
        completed_outputs = {}
        output_names = []

        # Poll until all outputs are ready or timeout
        while True:
            current_time = time.time()
            if current_time - start_time > timeout_seconds:
                raise Exception(
                    f"Workflow execution timed out after {timeout_ms}ms ({timeout_seconds}s)"
                )

            # Get current run status and outputs
            try:
                run_details = self.get_run(run_id)
                if not run_details or "data" not in run_details:
                    logging.warning(f"No data in run details for run {run_id}")
                    time.sleep(poll_interval_seconds)
                    continue

                run_data = run_details["data"]
                run_status = run_data.get("status", "unknown")

                # Check for run failure
                if run_status in ["failed", "error", "cancelled"]:
                    raise Exception(f"Run {run_id} failed with status: {run_status}")

                # Get output names from run details
                current_output_names = run_data.get("output_names", [])

                # Update our list of expected outputs
                if current_output_names and not output_names:
                    output_names = current_output_names
                    logging.info(f"Found output names for run {run_id}: {output_names}")
                elif current_output_names != output_names and current_output_names:
                    # Output names list has been updated
                    output_names = current_output_names
                    logging.info(
                        f"Updated output names for run {run_id}: {output_names}"
                    )

                if not output_names:
                    # No output names available yet, continue polling
                    logging.debug(
                        f"No output names available yet for run {run_id}, status: {run_status}"
                    )
                    time.sleep(poll_interval_seconds)
                    continue

                # Check each output that hasn't completed yet
                pending_outputs = [
                    name for name in output_names if name not in completed_outputs
                ]

                if not pending_outputs:
                    # All outputs are complete
                    logging.info(f"All outputs completed for run {run_id}")
                    return {
                        "run_id": run_id,
                        "outputs": completed_outputs,
                        "total_outputs": len(output_names),
                        "status": "completed",
                    }

                # Try to get each pending output
                for output_name in pending_outputs:
                    try:
                        output_response = self.get_output(output_name)
                        if output_response is not None:
                            completed_outputs[output_name] = output_response
                            logging.info(
                                f"Output {output_name} completed ({len(completed_outputs)}/{len(output_names)})"
                            )
                    except Exception as e:
                        logging.error(f"Error getting output {output_name}: {e}")

            except Exception as e:
                logging.error(f"Error polling run {run_id}: {e}")
                # Don't break on polling errors, continue trying
                time.sleep(poll_interval_seconds)
                continue

            time.sleep(poll_interval_seconds)

    def get_output(self, filename: str) -> GetOutputResponse | None:
        """
        Retrieves the output of a specific run by providing the filename.

        Args:
            filename: The filename of the output to retrieve

        Returns:
            The output response or None if no output is found
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/runs/output",
                headers=self.headers,
                params={"filename": filename},
            )

            if response.status_code == 204:
                return None

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 204:
                return None
            elif error.response.status_code == 408:
                raise Exception("Run Timeout") from error
            else:
                self._handle_error(error)
        except Exception as error:
            self._handle_error(error)

    def cancel_run(self, run_id: str) -> CancelRunResponse:
        """
        Cancels a specific run using its unique run ID.

        Args:
            run_id: The ID of the run to cancel

        Returns:
            The cancellation response
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/runs/{run_id}/cancel", headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)

    def get_run(self, run_id: str) -> RunDetailResponse:
        """
        Retrieves detailed information about a specific run using its unique run ID.

        Args:
            run_id: The ID of the run to retrieve

        Returns:
            The run details response
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/runs/{run_id}", headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)

    def get_runs(
        self,
        group_id: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 10,
    ) -> RunListResponse:
        """
        Retrieves a list of all runs with pagination, sorting, and optional filtering.

        Args:
            group_id: Optional group ID to filter runs
            sort_by: Field to sort by (created_at, started_at, completed_at)
            sort_order: Sort order (asc, desc)
            page: Page number (starting from 1)
            page_size: Number of items per page (1-100)

        Returns:
            The paginated list of runs response
        """
        try:
            params = {
                "sort_by": sort_by,
                "sort_order": sort_order,
                "page": page,
                "page_size": page_size,
            }
            if group_id:
                params["group_id"] = group_id

            response = requests.get(
                f"{self.base_url}/api/v1/runs", headers=self.headers, params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)

    def _handle_error(self, error: Exception) -> NoReturn:
        """
        Error handling helper with enhanced logging.

        Args:
            error: The exception to handle
        """
        if isinstance(error, requests.exceptions.HTTPError):
            response = error.response
            error_msg = f"HTTP Error {response.status_code} {response.reason}"
            try:
                error_detail = response.json()
                if isinstance(error_detail, dict) and "errors" in error_detail:
                    error_msg += f" - {error_detail['errors']}"
                else:
                    error_msg += f" - {response.text}"
            except (ValueError, KeyError):
                error_msg += f" - {response.text}"

            logging.error(error_msg)
            raise Exception(error_msg)
        elif isinstance(error, requests.exceptions.RequestException):
            error_msg = f"Request error: {str(error)}"
            logging.error(error_msg)
            raise Exception(error_msg)
        else:
            error_msg = f"Unexpected error in FlowscaleAPI: {error}"
            logging.error(error_msg)
            raise Exception(f"Error: {str(error)}")
