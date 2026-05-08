from pydantic import BaseModel


class OverviewStatsResponse(BaseModel):
    food_count: int
    history_count: int
