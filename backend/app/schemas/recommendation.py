from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    prompt: str = Field(
        min_length=3,
        max_length=1000,
        description="Preferensi atau permintaan rekomendasi film dari pengguna."
    )


class RecommendationResponse(BaseModel):
    movie_id: int
    reasoning: str