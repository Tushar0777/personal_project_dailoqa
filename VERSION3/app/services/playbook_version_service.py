from boto3.dynamodb.conditions import Key, Attr
from .base import BaseService
from datetime import datetime


class PlaybookVersionService(BaseService):

    def list_versions(self,playbook_id:str):
        response=self.table.query(
            KeyConditionExpression=Key("primary_id").eq(f"PLAYBOOK#{playbook_id}")&
            Key("secondary_id").begins_with("VERSION#"),
            FilterExpression=Attr("is_deleted").ne(True),
            ReturnConsumedCapacity="TOTAL"
        )

        return{
            "versions":response.get("Items",[]),
            "rcu":self._extract_capacity(response)
        }
    
    def get_version(self,playbook_id,version:int):
        response=self.table.get_item(
            key={
                "primary_id":f"PLAYBOOK#{playbook_id}",
                "secondary_id":f"VERSION#{version}"
            },
            ReturnConsumedCapacity="TOTAL"
        )

        return{
            "version":response.get("Item"),
            "rcu":self._extract_capacity(response)
        }
    
    def add_version(self,playbook_id:str,version:int,content:str):
        now=datetime.utcnow().isoformat()

        response=self.table.put_item(
            Item={
                "primary_id":f"PLAYBOOK#{playbook_id}",
                "secondary_id":f"VERSION#{version}",
                "entity_type":"PLAYBOOK_VERSION",
                "version":version,
                "content":content,
                "created_at":now
            },
            ReturnConsumedCapacity="TOTAL"
        )

        return{
            "status":"VERSION_CREATED",
            "wcu":self._extract_capacity(response)
        }
    
    def soft_delete_version(self, playbook_id: str, version: int):
        response = self.table.update_item(
            Key={
                "primary_id": f"PLAYBOOK#{playbook_id}",
                "secondary_id": f"VERSION#{version}"
            },
            UpdateExpression="SET is_deleted = :d, deleted_at = :t",
            ExpressionAttributeValues={
                ":d": True,
                ":t": datetime.utcnow().isoformat()
            },
            ReturnConsumedCapacity="TOTAL"
        )
        return {
            "status": "VERSION_SOFT_DELETED",
            "wcu": self._extract_capacity(response)
        }
    
    def hard_delete_version(self, playbook_id: str, version: int):
        response = self.table.delete_item(
            Key={
                "primary_id": f"PLAYBOOK#{playbook_id}",
                "secondary_id": f"VERSION#{version}"
            },
            ReturnConsumedCapacity="TOTAL"
        )
        return {
            "status": "VERSION_HARD_DELETED",
            "wcu": self._extract_capacity(response)
        }
    
    def update_version(self, playbook_id: str, version: int, new_content: str):
        # First, get the current version to save previous content
        current = self.table.get_item(
            Key={
                "primary_id": f"PLAYBOOK#{playbook_id}",
                "secondary_id": f"VERSION#{version}"
            }
        )
        item = current.get("Item")
        if not item:
            return {"status": "VERSION_NOT_FOUND"}
        
        previous_content = item.get("content")
        
        response = self.table.update_item(
            Key={
                "primary_id": f"PLAYBOOK#{playbook_id}",
                "secondary_id": f"VERSION#{version}"
            },
            UpdateExpression="SET content = :c, previous_content = :pc, updated_at = :t",
            ExpressionAttributeValues={
                ":c": new_content,
                ":pc": previous_content,
                ":t": datetime.utcnow().isoformat()
            },
            ReturnConsumedCapacity="TOTAL"
        )
        return {
            "status": "VERSION_UPDATED",
            "wcu": self._extract_capacity(response)
        }
    
    def rollback_version(self, playbook_id: str, version: int):
        # Get the current version
        current = self.table.get_item(
            Key={
                "primary_id": f"PLAYBOOK#{playbook_id}",
                "secondary_id": f"VERSION#{version}"
            }
        )
        item = current.get("Item")
        if not item:
            return {"status": "VERSION_NOT_FOUND"}
        
        previous_content = item.get("previous_content")
        if not previous_content:
            return {"status": "NO_PREVIOUS_CONTENT"}
        
        current_content = item.get("content")
        
        response = self.table.update_item(
            Key={
                "primary_id": f"PLAYBOOK#{playbook_id}",
                "secondary_id": f"VERSION#{version}"
            },
            UpdateExpression="SET content = :c, previous_content = :pc, rolled_back_at = :t",
            ExpressionAttributeValues={
                ":c": previous_content,
                ":pc": current_content,
                ":t": datetime.utcnow().isoformat()
            },
            ReturnConsumedCapacity="TOTAL"
        )
        return {
            "status": "VERSION_ROLLED_BACK",
            "wcu": self._extract_capacity(response)
        }

# Optional: Method to clear previous_content after rollback or manually
# def clear_previous_content(self, playbook_id: str, version: int):
#     response = self.table.update_item(
#         Key={
#             "primary_id": f"PLAYBOOK#{playbook_id}",
#             "secondary_id": f"VERSION#{version}"
#         },
#         UpdateExpression="REMOVE previous_content",
#         ReturnConsumedCapacity="TOTAL"
#     )
#     return {
#         "status": "PREVIOUS_CONTENT_CLEARED",
#         "wcu": self._extract_capacity(response)
#     }