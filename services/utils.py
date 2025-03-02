import csv
import os
from io import StringIO

import requests
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from dto.UploadDTO import UploadDTO
from dto.StatusDTO import StatusDTO
from services.clients import mongo_client, s3_client


def validate_csv(csv_contents: list):
    expected_headers = ["S. No.", "Product Name", "Input Image Urls"]
    for record in csv_contents:
        for header in expected_headers:
            if header not in record or record[header] is None:
                raise HTTPException(status_code=400, detail="Invalid CSV format.")


def save_to_mongo(request_id, content, collection_name):
    collection = mongo_client["image_compression"][collection_name]
    if collection_name == "uploads":
        dto = UploadDTO(request_id=request_id, file_contents=content)
    elif collection_name == "requests":
        dto = StatusDTO(request_id=request_id, status=content)
    collection.insert_one(dto.model_dump())
    return dto.model_dump()


def get_from_mongo(request_id, collection_name):
    collection = mongo_client["image_compression"][collection_name]
    return collection.find_one({"request_id": request_id})


def update_in_mongo(request_id, content, collection_name):
    collection = mongo_client["image_compression"][collection_name]
    return collection.find_one_and_update({"request_id": request_id}, {"$set": content})


def upload_to_s3(file_path, bucket_name):
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as file:
        s3_client.upload_file(file, bucket_name, file_name, extra_args={"ACL": "public-read"})
        uploaded_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        return uploaded_url


def generate_csv_response(record):
    fields = ["S. No.", "Product Name", "Input Image Urls", "Output Image Urls"]
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(record["file_contents"])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={record['request_id']}.csv"})


def send_webhook_notification(url, record):
    try:
        requests.post(url, generate_csv_response(record))
    except requests.exceptions.RequestException as e:
        print(f"Webhook failed: {e}")
