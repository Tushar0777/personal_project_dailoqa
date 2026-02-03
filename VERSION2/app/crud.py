from datetime import datetime 
# from app.dbconnect import table
from botocore.exceptions import ClientError


def create_playbook(table,playbook_id:str):
    now=datetime.now().isoformat()
    table.put_item(
        Item={
            "PK":playbook_id,
            "SK":"META",
            "latestVersion":0,
            "totalVersions":0,
            "createdAt":now,
            "updatedAt":now
        },
        ConditionExpression="attribute_not_exists(PK)"
        # c capital hota hai 
    )



def create_new_version(table, playbook_id: str, content: str):
    now = datetime.utcnow().isoformat()

    try:
        response = table.update_item(
            Key={
                "PK": playbook_id,
                "SK": "META"
            },
            UpdateExpression="""
                ADD latestVersion :inc,
                    totalVersions :inc
                SET updatedAt = :ut
            """,
            # dhiyan se dekh isme agar value exist nhi krti to add use bana deta hai 
            ExpressionAttributeValues={
                ":inc": 1,
                ":ut": now
            },
            ConditionExpression="attribute_exists(PK)",
            ReturnValues="UPDATED_NEW"
        )

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise ValueError("Playbook does not exist")
        else:
            raise

    new_version = response["Attributes"]["latestVersion"]

    table.put_item(
        Item={
            "PK": playbook_id,
            "SK": f"VERSION#{new_version}",
            "version": new_version,
            "content": content,
            "createdAt": now
        },
        ConditionExpression="attribute_not_exists(PK)"
    )



# -> todo isme walrus operator se try krna hai krne ki 
def get_latest_version(table,playbook_id:str):
    meta=table.get_item(
        Key={
            "PK":playbook_id,
            "SK":"META"
        }
    )["Item"]

    latest=int(meta["latestVersion"])

    response=table.get_item(
        Key={
            "PK":playbook_id,
            "SK":f"VERSION#{latest}"
        }
    )

    return response['Item']


def update_version_content(table,playbook_id: str, version: int, content: str):
    table.update_item(
        Key={
            "PK": playbook_id,
            "SK": f"VERSION#{version}"
        },
        # SET change karega ADD atomicity karega 
        UpdateExpression="SET content = :c",
        ExpressionAttributeValues={
            ":c": content
        }
    )


# naye naye 
def list_all_playbooks(table):
    response=table.scan(
        FilterExpression="SK = :meta",
        ExpressionAttributeValues={
            ":meta":"META"
        }
    )
    return response['Items']
# isme humare pass pk nhi hai to scan must ho jata hai 

def list_all_versions(table,playbook_id:str):
    response=table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK,:v)",
        ExpressionAttributeValues={
            ":pk":playbook_id,
            ":v":"VERSION#"
        },
        ScanIndexForward=False
    )
    return response['Items']

# | Operation | Why                            |
# | --------- | ------------------------------ |
# | GetItem   | ❌ Single exact key only        |
# | Query     | ✅ Multiple items under same PK |
# | Scan      | ❌ Last resort                  |





# def create_new_version(table,playbook_id:str,content:str):
#     response=table.get_item(
#         Key={
#             "PK":playbook_id,
#             "SK":"META"
#         }
#     )
#     if "Item" not in response:
#         raise ValueError("Playbook does not exist")
    
#     meta=response['Item']

#     current_version=meta['latestVersion']
#     new_version=current_version+1
#     now =datetime.utcnow().isoformat()

#     table.put_item(
#         Item={
#             "PK":playbook_id,
#             "SK": f"VERSION#{new_version}",
#             "version":new_version,
#             "content":content,
#             "createdAt":now
#         }
#     )


#     table.update_item(
#         Key={
#             "PK":playbook_id,
#             "SK":"META"
#         },
#         UpdateExpression="""
#         SET latestVersion = :lv,
#             totalVersions = :tv,
#             updatedAt = :ut
# """,
#         ExpressionAttributeValues={
#             ":lv":new_version,
#             ":tv":meta['totalVersions']+1,
#             ":ut":now
#         }
#     )
