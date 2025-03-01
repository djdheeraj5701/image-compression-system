from pymongo import MongoClient
from redis import StrictRedis
import boto3

mongo_client = MongoClient("mongodb://localhost:27017")
redis_client = StrictRedis(host="localhost", port=6379, db=0)
s3_client = boto3.client("s3")
