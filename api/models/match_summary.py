from pydantic import BaseModel


class MatchSummaryModel(BaseModel):
    match_id: int
    match_info: str


class LLMModel(BaseModel):
    message: str


class LLMResponse(BaseModel):
    assistant: str
