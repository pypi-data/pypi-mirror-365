from pydantic import BaseModel, Field


class Config(BaseModel):
    model_config = {"extra": "ignore"}
    # 必填
    gd_api_key: str = Field(...)
    gd_api_base_url: str = Field(...)
    gd_default_model: str = Field(...)

    # 选填
    gd_default_tmp: float = 0.7
    gd_ask_tmp: float | None = None
    gd_ask_model: str | None = None
    gd_report_tmp: float | None = None
    gd_report_model: str | None = None
    gd_check_tmp: float | None = None
    gd_check_model: str | None = None
    gd_allowed_groups: set[int] = Field(default_factory=set)
