import asyncio
import os

import requests
from PIL import Image

from dto.StatusDTO import StatusEnum
from services.utils import get_from_mongo, update_in_mongo, upload_to_s3, send_webhook_notification


async def process_request(request_id, webhook_url):
    record = get_from_mongo(request_id, "uploads")
    update_in_mongo(request_id, {"status": StatusEnum.IN_PROGRESS.value}, "requests")

    updated_contents = await process_record(record)
    updated_record = update_in_mongo(request_id, {"file_contents": updated_contents}, "uploads")
    update_in_mongo(request_id, {"status": StatusEnum.COMPLETED.value}, "requests")

    send_webhook_notification(webhook_url, updated_record)


async def process_record(record):
    updated_contents = []
    for row_id, row in enumerate(record["file_contents"]):
        output_urls = await process_images(row["Input Image Urls"].split(","), record["request_id"], row_id)
        row["Output Image Urls"] = ",".join(output_urls)
        updated_contents.append(row)
    return updated_contents


async def process_images(image_urls, request_id, row_id):
    tasks = [process_image(url, f"{request_id}/{row_id}") for url in image_urls]
    output_urls = await asyncio.gather(*tasks)
    return output_urls


async def process_image(url, folder):
    bucket_name = "image_compression_bucket"
    response = requests.get(url)

    image_name = os.path.basename(url)
    if not os.path.exists(folder):
        os.makedirs(folder)
    input_path = f"{folder}/input-{image_name}"
    output_path = f"{folder}/{image_name}"

    with open(input_path, "wb+") as file:
        file.write(response.content)

    with Image.open(input_path) as image:
        image.resize((int(image.size[0] / 2), int(image.size[1] / 2))).save(output_path)
        return upload_to_s3(output_path, bucket_name)
