from pydantic import BaseModel

class RequestDTO(BaseModel):
    from_currency: str
    to_currency: str
    period: str