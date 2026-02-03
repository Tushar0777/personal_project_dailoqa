# (.venv) PS D:\Local Disk (D)\Dailoqa(Intern)\30jan_project\version1> 
# uvicorn VERSION2.app.main:app --reload --env-file VERSION2/.env
from dotenv import load_dotenv

load_dotenv()
import os
import boto3

aws_region=os.getenv("AWS_REGION")

dynamodb=boto3.resource(
    'dynamodb',
    # aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    # aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=aws_region
)

table =dynamodb.Table('playbooks')


if __name__=='__main__':
    try:
        table.load()
        print("connected sucessfully")
        print("Table name:", table.table_name)
        print("Table status:", table.table_status)
        print("Item count:", table.item_count)

    except Exception as e:
        print("connection failed ",e)





