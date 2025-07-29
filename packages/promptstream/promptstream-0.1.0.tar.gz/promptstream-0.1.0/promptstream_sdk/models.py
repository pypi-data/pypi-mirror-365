from uuid import UUID
from typing import Dict, Optional
from pydantic import BaseModel, Field

class RunPromptRequest(BaseModel):
    prompt_id: str
    inputs: Dict[str, str]
    external_user_id: Optional[str]

class RunPromptResponse(BaseModel):
    run_id: UUID
    output: str
    model_used: str
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    token_cost_usd: float
    variant_assigned: Optional[str]

class TrackOutcomeRequest(BaseModel):
    prompt_run_id: UUID
    experiment_id: UUID
    external_user_id: Optional[str]
    event_type: str
    label: str
    value: str


class GetPromptResponse(BaseModel):
    """Response model for returning the rendered prompt text."""

    prompt_text: str
    variant_assigned: Optional[str] = None
    experiment_id: Optional[str] = None
