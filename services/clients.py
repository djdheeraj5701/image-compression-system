from pymongo import MongoClient
import boto3

mongo_client = MongoClient("mongodb://localhost:27017")
s3_client = boto3.client("s3")
