import csv

import codecs
import uuid

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile

from dto.StatusDTO import StatusDTO, StatusEnum
from services.utils import validate_csv, save_to_mongo, push_to_redis, get_from_mongo, generate_csv_response

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

    push_to_redis(request_id)

    return current_status


@app.get("/api/v1/status/{request_id}")
async def get_status(request_id: str) -> StatusDTO:
    record = get_from_mongo(request_id, "requests")
    if record:
        return record
    raise HTTPException(status_code=404, detail="Request ID not found.")


@app.get("/api/v1/output/{request_id}")
async def get_output(request_id: str) -> UploadFile:
    status_record = await get_status(request_id)
    if status_record["status"] == "COMPLETED":
        record = get_from_mongo(request_id, "uploads")
        return generate_csv_response(record)
    raise HTTPException(status_code=400, detail="Process not completed.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
