from boto3.dynamodb.conditions import Key
from .base import BaseService
from datetime import datetime


class PlaybookVersionService(BaseService):

    def list_versions(self,playbook_id:str):
        response=self.table.query(
            KeyConditionExpression=Key("primary_id").eq(f"PLAYBOOK#{playbook_id}")&
            Key("secondary_id").begins_with("VERSION#"),
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