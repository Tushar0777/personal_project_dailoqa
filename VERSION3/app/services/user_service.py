from .base import BaseService
from boto3.dynamodb.conditions import Key
from datetime import datetime

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
    
    def create_user(self,user_id,user_name:str):
        return self.table.put_item(
            Item={
                "primary_id":f"USER#{user_id}",
                "secondary_id":"PROFILE",
                "entity_type":"USER",
                "name":user_name,
                "created_at":datetime.utcnow().isoformat()
            },
            ConditionExpression="attribute_not_exists(primary_id)",
            ReturnConsumedCapacity="TOTAL"
        )
    
    def assign_role(self,user_id:str,role:str):
        return self.table.put_item(
            Item={
                "primary_id":f"USER#{user_id}",
                "secondary_id":f"ROLE#{role}",
                "entity_type":"USER_ROLE"
            },
            ConditionExpression="attribute_not_exists(secondary_id)",
            ReturnConsumedCapacity="TOTAL"
        )
    
    def remove_role(self,user_id:str,role:str):
        return self.table.delete_item(
             Key={
                "primary_id": f"USER#{user_id}",
                "secondary_id": f"ROLE#{role}"
            },
            ReturnConsumedCapacity="TOTAL"
        )

