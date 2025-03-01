import csv

import codecs
import uuid

from fastapi import FastAPI, HTTPException, UploadFile

from dto.StatusDTO import StatusDTO, StatusEnum
from services.utils import validate_csv, save_to_mongo, publish_to_redis, get_from_mongo

app = FastAPI()


@app.post("/api/v1/upload")
async def upload_csv_file(file: UploadFile) -> StatusDTO:
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are accepted.")

    csv_contents = list(csv.DictReader(codecs.iterdecode(file.file, 'utf-8')))
    validate_csv(csv_contents)

    request_id = str(uuid.uuid4())

    save_to_mongo(request_id, csv_contents, "uploads")
    current_status = save_to_mongo(request_id, StatusEnum.PENDING.value, "requests")

    publish_to_redis(request_id)

    return current_status


@app.get("/api/v1/status/{request_id}")
async def get_status(request_id: str) -> StatusDTO:
    record = get_from_mongo(request_id, "requests")
    if record:
        return record
    raise HTTPException(status_code=404, detail="Request ID not found.")