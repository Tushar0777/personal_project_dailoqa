from boto3.dynamodb.conditions import Key, Attr
from .base import BaseService
from datetime import datetime

class PlaybookService(BaseService):
    def list_all_playbooks(self):
        response=self.table.scan(
            FilterExpression=Attr("primary_id").begins_with("PLAYBOOK#"),
            ReturnConsumedCapacity="TOTAL"
        )

        return{
            "playbooks":response.get("Items",[]),
            "rcu":self._extract_capacity(response)
        }
    

    def create_playbook(self,playbook_id:str,title:str,description:str,editor_id:str):
        now=datetime.utcnow().isoformat()

        response=self.table.put_item(
            Item={
                "primary_id":"PLAYBOOK",
                "secondary_id":"PLAYBOOK#{playbook_id}",
                "entity_type":"PLAYBOOK_META",
                "title":title,
                "description":description,
                "created_by":f"USER#{editor_id}",
                "created_at":now
            },
            ConditionExpression="attribute_not_exists(secondary_id)",
            ReturnConsumedCapacity="TOTAL"
        )
        return{
            "status":"created",
            "wcu":self._extract_capacity(response)
        }
