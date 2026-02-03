from .dynamodb import get_dynamodb_resource

def get_table(table_name:str="playbook_core"):

    dynamodb=get_dynamodb_resource()
    return dynamodb.Table(table_name)
