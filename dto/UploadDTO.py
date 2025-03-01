from pydantic import BaseModel


class UploadDTO(BaseModel):
    request_id: str
    file_contents: list
