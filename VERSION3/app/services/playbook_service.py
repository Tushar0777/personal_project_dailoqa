from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from .base import BaseService
from datetime import datetime
import time
import uuid
import hashlib
import json

class PlaybookService(BaseService):
    # isme scan remove krna hai 
    # def list_all_playbooks(self):
    #     response=self.table.scan(
    #         FilterExpression=Attr("primary_id").begins_with("PLAYBOOK#"),
    #         ReturnConsumedCapacity="TOTAL"
    #     )
    #     return{
    #         "playbooks":response.get("Items",[]),
    #         "rcu":self._extract_capacity(response)
    #     }
    def _generate_idempotency_key(self, name: str) -> str:
        normalized_name = name.strip().lower()
        return hashlib.sha256(
            json.dumps({"name": normalized_name}, sort_keys=True).encode()
        ).hexdigest()
    
    def get_playbook_by_name(self, name: str):
        response = self.table.scan(
            FilterExpression=
                Attr("entity_type").eq("PLAYBOOK_META") &
                Attr("name").eq(name) &
                Attr("is_deleted").ne(True),
            ReturnConsumedCapacity="TOTAL"
        )

        items = response.get("Items", [])

        if not items:
            return {
                "playbook": None,
                "rcu": self._extract_capacity(response)
            }

        return {
            "playbook": items[0],   # assuming name unique
            "rcu": self._extract_capacity(response)
        }
    
    def list_all_playbooks(self):
        response = self.table.scan(
            FilterExpression=
                Attr("entity_type").eq("PLAYBOOK_META") &
                Attr("is_deleted").ne(True),
            ReturnConsumedCapacity="TOTAL"
        )

        return {
            "playbooks": response.get("Items", []),
            "rcu": self._extract_capacity(response)
        }
    

    def create_playbook(self,name:str,title:str,description:str,editor_id:str):
        
        idempotency_key = self._generate_idempotency_key(name)

        pk = f"IDEMPOTENCY#{idempotency_key}"

        now=datetime.utcnow().isoformat()

        existing = self.table.get_item(
            Key={"primary_id": pk, "secondary_id": "REQUEST"}
        )
        if "Item" in existing:
            item = existing["Item"]

            if item["status"] == "DONE":
                return json.loads(item["response_body"])
            if item["status"] == "LOCKED":
                return {"status": "Request already in progress"}
            
               # 🔒 Step 2 — Acquire Lock
        try:
            self.table.put_item(
                Item={
                    "primary_id": pk,
                    "secondary_id": "REQUEST",
                    "status": "LOCKED",
                    "created_at": now,
                    "ttl": int(datetime.utcnow().timestamp()) + 86400
                    # ek din ka ttl
                },
                ConditionExpression="attribute_not_exists(primary_id)"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {"status": "Request already in progress"}
            raise

        playbook_id=str(uuid.uuid4())


        response=self.table.put_item(
            Item={
                "primary_id":f"PLAYBOOK#{playbook_id}",
                "secondary_id":"METADATA",
                "entity_type":"PLAYBOOK_META",
                "name":name,
                "title":title,
                "description":description,
                "created_by":f"USER#{editor_id}",
                "created_at":now,
                "is_deleted":False
            },
            ReturnConsumedCapacity="TOTAL"
        )
        response_body={
            "status":"playbook created",
            "playbook_id":playbook_id,
            "wcu":self._extract_capacity(response)
        }
        self.table.update_item(
            Key={"primary_id": pk, "secondary_id": "REQUEST"},
            UpdateExpression="SET #s = :done, response_body = :r",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":done": "DONE",
                ":r": json.dumps(response_body)
            }
        )
        return response_body
    
    def delete_playbook(self, playbook_id: str):
        try:
            ttl_days = 7
            expire_at = int(time.time()) + (ttl_days * 24 * 60 * 60)
            response=self.table.update_item(
                Key={
                    "primary_id": f"PLAYBOOK#{playbook_id}",
                    "secondary_id": "METADATA"
                },
                UpdateExpression="SET is_deleted = :d, expire_at = :ttl",
                ExpressionAttributeValues={
                    ":d": True,
                    ":ttl":expire_at
                    },
                ReturnConsumedCapacity="TOTAL"
            )
            return{
                "deleted":True,
                "response":response,
                "wcu":self._extract_capacity(response)
            }
        except ClientError as e:
            if e.response["Error"]["Code"]=="ConditionalCheckFailedException":
                return {
                    "deleted": False,
                    "reason": "PLAYBOOK_ALREADY_DELETED",
                    "wcu": 0
                }
            raise
