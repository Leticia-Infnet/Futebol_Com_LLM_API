from pydantic import BaseModel


class PlayerProfileModel(BaseModel):
    match_id: int
    player_name: str


class LLMModel(BaseModel):
    message: str


class LLMResponse(BaseModel):
    assistant: str
