from fastapi import HTTPException

from dto.UploadDTO import UploadDTO
from dto.StatusDTO import StatusDTO
from services.clients import mongo_client, redis_client


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
    collection.find_one_and_update({"request_id": request_id}, {"$set": content})


def push_to_redis(request_id):
    redis_client.rpush("uploads", request_id)


def pull_from_redis():
    return redis_client.blpop("uploads")
