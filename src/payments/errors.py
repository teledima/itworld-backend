from pydantic import BaseModel


class HttpError(BaseModel):
    type: str
    code: str
    message: str
