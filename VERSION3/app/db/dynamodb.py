from dotenv import load_dotenv
load_dotenv()
import os
import boto3
from functools import lru_cache

aws_region=os.getenv("AWS_REGION")
@lru_cache
def get_dynamodb_resource():
    return boto3.resource(
        "dynamodb",
        region_name=aws_region
    )