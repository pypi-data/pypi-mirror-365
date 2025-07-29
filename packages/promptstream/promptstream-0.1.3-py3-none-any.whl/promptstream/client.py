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
        self,
        prompt_run_id,
        prompt_id,
        event_type,
        label,
        value,
        *,
        source,
        is_success=True,
        metadata=None,
        external_user_id=None,
    ) -> None:
        req = TrackOutcomeRequest(
            prompt_run_id=prompt_run_id,
            prompt_id=prompt_id,
            external_user_id=external_user_id,
            event_type=event_type,
            label=label,
            source=source,
            value=str(value),
            is_success=is_success,
            metadata=metadata,
        )
        resp = self._client.post(f"{self.base_url}/track_outcome", json=req.dict())
        if resp.status_code != 201:
            raise APIError.from_httpx(resp)
        return

    def track_click(
        self,
        prompt_run_id,
        prompt_id,
        label,
        *,
        source,
        metadata=None,
        external_user_id=None,
    ) -> None:
        return self.track_outcome(
            prompt_run_id,
            prompt_id,
            "click",
            label,
            label,
            source=source,
            metadata=metadata,
            external_user_id=external_user_id,
            is_success=True,
        )

    def track_conversion(
        self,
        prompt_run_id,
        prompt_id,
        label,
        *,
        source,
        metadata=None,
        external_user_id=None,
    ) -> None:
        return self.track_outcome(
            prompt_run_id,
            prompt_id,
            "conversion",
            label,
            label,
            source=source,
            metadata=metadata,
            external_user_id=external_user_id,
            is_success=True,
        )

    def track_engagement(
        self,
        prompt_run_id,
        prompt_id,
        label,
        score,
        *,
        source,
        metadata=None,
        external_user_id=None,
    ) -> None:
        return self.track_outcome(
            prompt_run_id,
            prompt_id,
            "engagement",
            label,
            score,
            source=source,
            metadata=metadata,
            external_user_id=external_user_id,
            is_success=True,
        )

    def track_feedback(
        self,
        prompt_run_id,
        prompt_id,
        label,
        thumbs_up,
        *,
        source,
        metadata=None,
        external_user_id=None,
    ) -> None:
        return self.track_outcome(
            prompt_run_id,
            prompt_id,
            "feedback",
            label,
            "1" if thumbs_up else "0",
            source=source,
            metadata=metadata,
            external_user_id=external_user_id,
            is_success=bool(thumbs_up),
        )

    def track_rating(
        self,
        prompt_run_id,
        prompt_id,
        label,
        rating,
        *,
        source,
        metadata=None,
        external_user_id=None,
    ) -> None:
        return self.track_outcome(
            prompt_run_id,
            prompt_id,
            "rating",
            label,
            rating,
            source=source,
            metadata=metadata,
            external_user_id=external_user_id,
            is_success=True,
        )
