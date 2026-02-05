from .base import BaseService
from boto3.dynamodb.conditions import Key
from datetime import datetime
import uuid
from botocore.exceptions import ClientError

class UserService(BaseService):

    def get_user(self,user_id):
        response=self.table.get_item(
            Key={
                "primary_id":f"USER#{user_id}",
                "secondary_id":"PROFILE"
            },
            ReturnConsumedCapacity="TOTAL"
        )
        return {
            "user":response.get("Item"),
            "rcu":self._extract_capacity(response)
        }
    
    def get_user_roles(self,user_id:str):
        response=self.table.query(
            KeyConditionExpression=Key("primary_id").eq(f"USER#{user_id}") & Key("secondary_id").begins_with("ROLE#"),
            ReturnConsumedCapacity="TOTAL"
        )

        roles=[
            item["secondary_id"].replace("ROLE#","")
            for item in response.get("Items",[])
        ]

        return{
            "roles":roles,
            "rcu":self._extract_capacity(response)
        }
    
    def create_user(self,user_name:str,password:str):
        user_id=str(uuid.uuid4())
        now=datetime.utcnow().isoformat()
        response1=self.table.put_item(
            Item={
                "primary_id": f"USERNAME#{user_name}",
                "secondary_id": "USER",
                "user_id": user_id
            },
            ConditionExpression="attribute_not_exists(primary_id)"
        )
        response2=self.table.put_item(
            Item={
                "primary_id":f"USER#{user_id}",
                "secondary_id":"PROFILE",
                "entity_type":"USER",
                "username":user_name,
                "password":password,
                "created_at":now
            },
            ReturnConsumedCapacity="TOTAL"
        )
        return {
            "user_id": user_id,
            "username": user_name,
            "capacity": {
                "username_write": self._extract_capacity(response1),
                "profile_write": self._extract_capacity(response2)
            }
        }
    
    def assign_role(self,user_id:str,role:str):
        try:
            response=self.table.put_item(
                Item={
                    "primary_id":f"USER#{user_id}",
                    "secondary_id":f"ROLE#{role}",
                    "entity_type":"USER_ROLE"
                },
                ConditionExpression="attribute_not_exists(secondary_id)",
                ReturnConsumedCapacity="TOTAL"
            )
            return{
                "response":response,
                "assigned":True,
                "wcu":self._extract_capacity(response)
            }
        except ClientError as e:
            if e.response["Error"]["Code"]=="ConditionalCheckFailedException":
                return{
                    "assigned": False,
                    "reason": "ROLE_ALREADY_ASSIGNED"
                }
            raise
    
    def remove_role(self,user_id:str,role:str):
        try:
            response=self.table.delete_item(
                Key={
                    "primary_id": f"USER#{user_id}",
                    "secondary_id": f"ROLE#{role}"
                },
                ConditionExpression="attribute_exists(secondary_id)",
                ReturnConsumedCapacity="TOTAL"
            )
            return{
                "removed":True,
                "response":response,
                "wcu":self._extract_capacity(response)
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {
                    "removed": False,
                    "reason": "ROLE_NOT_ASSIGNED",
                    "wcu": 0
                }
            raise

    
    def get_user_by_username(self,username:str):
        response=self.table.get_item(
            Key={
                "primary_id":f"USERNAME#{username}",
                "secondary_id":"USER"
            },
            ReturnConsumedCapacity="TOTAL"
        )
        if "Item" not in response:
            return {"user": None}

        user_id = response["Item"]["user_id"]

        profile = self.table.get_item(
            Key={
                "primary_id": f"USER#{user_id}",
                "secondary_id": "PROFILE"
            },
            ReturnConsumedCapacity="TOTAL"
        )

        user = profile.get("Item")
        if user:
            user["user_id"] = user_id

        return {
            "user": user,
            "capacity": {
                "username_read": self._extract_capacity(response),
                "profile_read": self._extract_capacity(profile)
            }
        }


