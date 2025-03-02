from pymongo import MongoClient
from redis import Redis
import boto3

mongo_client = MongoClient("mongodb://localhost:27017")
redis_client = Redis(host="localhost", port=6379, db=0)
s3_client = boto3.client("s3")
