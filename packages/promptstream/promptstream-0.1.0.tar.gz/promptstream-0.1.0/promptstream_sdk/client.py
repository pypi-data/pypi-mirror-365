import httpx
from .models import (
    RunPromptRequest, RunPromptResponse,
    TrackOutcomeRequest, GetPromptResponse
)
from .exceptions import APIError

BASE_URL = "https://api.promptstream.ai"

class PromptStreamClient:
    def __init__(self, api_key: str, timeout: float = 10.0):
        self.base_url = BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        }
        self._client = httpx.Client(timeout=timeout, headers=self.headers)

    def run_prompt(self, prompt_id, inputs, external_user_id=None) -> RunPromptResponse:
        req = RunPromptRequest(
            prompt_id=prompt_id, inputs=inputs, external_user_id=external_user_id
        )
        resp = self._client.post(f"{self.base_url}/run_prompt", json=req.dict())
        if resp.status_code != 200:
            raise APIError.from_httpx(resp)
        return RunPromptResponse.parse_obj(resp.json())

    def get_prompt(self, prompt_id, inputs, external_user_id=None) -> GetPromptResponse:
        req = RunPromptRequest(
            prompt_id=prompt_id, inputs=inputs, external_user_id=external_user_id
        )
        resp = self._client.post(f"{self.base_url}/get_prompt", json=req.dict())
        if resp.status_code != 200:
            raise APIError.from_httpx(resp)
        return GetPromptResponse.parse_obj(resp.json())

    def track_outcome(
        self, prompt_run_id, experiment_id,
        event_type, label, value,
        external_user_id=None
    ) -> None:
        req = TrackOutcomeRequest(
            prompt_run_id=prompt_run_id,
            experiment_id=experiment_id,
            external_user_id=external_user_id,
            event_type=event_type,
            label=label,
            value=value,
        )
        resp = self._client.post(f"{self.base_url}/track_outcome", json=req.dict())
        if resp.status_code != 201:
            raise APIError.from_httpx(resp)
        return
