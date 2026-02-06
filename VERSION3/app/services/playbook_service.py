from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from .base import BaseService
from datetime import datetime
import time
import uuid
import hashlib
import json

class PlaybookService(BaseService):

    def _generate_idempotency_key(self, name: str) -> str:
        normalized_name = name.strip().lower()
        return hashlib.sha256(
            json.dumps({"name": normalized_name}, sort_keys=True).encode()
        ).hexdigest()
    
    # def get_playbook_by_name(self, name: str):
    #     response = self.table.scan(
    #         FilterExpression=
    #             Attr("entity_type").eq("PLAYBOOK_META") &
    #             Attr("name").eq(name) &
    #             Attr("is_deleted").ne(True),
    #         ReturnConsumedCapacity="TOTAL"
    #     )

    #     items = response.get("Items", [])

    #     if not items:
    #         return {
    #             "playbook": None,
    #             "rcu": self._extract_capacity(response)
    #         }

    #     return {
    #         "playbook": items[0],   # assuming name unique
    #         "rcu": self._extract_capacity(response)
    #     }
    def get_playbook_by_name(self, name: str):
        """
        O(1) get by name using mapping item (secondary_id='NAME_MAP')
        """
        # pk = f"PLAYBOOK_NAME#{name.strip().lower()}"
        # response = self.table.get_item(
        #     Key={"primary_id": pk, "secondary_id": "NAME_MAP"}
        # )

        # mapping = response.get("Item")
        # if not mapping:
        #     return {"playbook": None, "rcu": self._extract_capacity(response)}

        # playbook_id = mapping["playbook_id"]
        # pb_response = self.table.get_item(
        #     Key={"primary_id": f"PLAYBOOK#{playbook_id}", "secondary_id": "METADATA"}
        # )

        # return {"playbook": pb_response.get("Item"), "rcu": self._extract_capacity(pb_response)}

        normalized = name.strip().lower()

        # 1️⃣ Try NAME_MAP first (O(1))
        pk = f"PLAYBOOK_NAME#{normalized}"
        response = self.table.get_item(
            Key={"primary_id": pk, "secondary_id": "NAME_MAP"}
        )

        mapping = response.get("Item")

        if mapping:
            playbook_id = mapping["playbook_id"]
            pb = self.table.get_item(
                    Key={
                        "primary_id": "METADATA",
                        "secondary_id": f"PLAYBOOK#{playbook_id}"
                    }
                )
    
            return {"playbook": pb.get("Item"), "rcu": self._extract_capacity(pb)}

    # 2️⃣ Fallback for old data
        scan = self.table.query(
                KeyConditionExpression=Key("primary_id").eq("METADATA"),
                FilterExpression=Attr("name").eq(name)
            )

        items = scan.get("Items", [])
        return {
                "playbook": items[0] if items else None,
                "rcu": self._extract_capacity(scan)
            }

    
    # def list_all_playbooks(self):
    #     response = self.table.scan(
    #         FilterExpression=
    #             Attr("entity_type").eq("PLAYBOOK_META") &
    #             Attr("is_deleted").ne(True),
    #         ReturnConsumedCapacity="TOTAL"
    #     )

    #     return {
    #         "playbooks": response.get("Items", []),
    #         "rcu": self._extract_capacity(response)
    #     }
    # def list_all_playbooks(self):
    #     response = self.table.query(
    #         KeyConditionExpression=Key("primary_id").begins_with("PLAYBOOK#") & Key("secondary_id").eq("METADATA"),
    #         ReturnConsumedCapacity="TOTAL"
    #     )
    #     items = response.get("Items", [])
    #     # filter out deleted playbooks in memory (low cost because only PLAYBOOK# items are returned)
    #     playbooks = [item for item in items if not item.get("is_deleted", False)]

    #     return {
    #     "playbooks": playbooks,
    #     "rcu": self._extract_capacity(response) 
    #     }
    # def list_all_playbooks(self):
    #     """
    #     List all playbooks efficiently: query only playbook metadata items
    #     (secondary_id='METADATA') to reduce RCU.
    #     """
    #     response = self.table.query(
    #         KeyConditionExpression=Key("secondary_id").eq("METADATA"),
    #         ReturnConsumedCapacity="TOTAL"
    #     )

    #     items = response.get("Items", [])
    #     # filter out deleted playbooks
    #     playbooks = [item for item in items if not item.get("is_deleted", False)]

    #     return {"playbooks": playbooks, "rcu": self._extract_capacity(response)}
    
    def list_all_playbooks(self):
        response = self.table.query(
            KeyConditionExpression=Key("primary_id").eq("METADATA"),
            ReturnConsumedCapacity="TOTAL"
        )
        playbooks = [item for item in response.get("Items", []) if not item.get("is_deleted", False)]
        return {"playbooks": playbooks, "rcu": self._extract_capacity(response)}

    

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
            response3=self.table.put_item(
                Item={
                    "primary_id": pk,
                    "secondary_id": "REQUEST",
                    "status": "LOCKED",
                    "created_at": now,
                    "ttl": int(datetime.utcnow().timestamp()) + 8640000
                },
                ConditionExpression="attribute_not_exists(primary_id)"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {"status": "Request already in progress"}
            # result["status"]
            raise

        playbook_id=str(uuid.uuid4())


        response=self.table.put_item(
            Item={
                "primary_id":"METADATA",
                "secondary_id":f"PLAYBOOK#{playbook_id}",
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
        response2=self.table.put_item(
        Item={
            "primary_id": f"PLAYBOOK_NAME#{name.strip().lower()}",
            "secondary_id": "NAME_MAP",  
            "playbook_id": playbook_id,
            "entity_type": "PLAYBOOK_NAME_INDEX",
            "created_at": now
        }
    )
        response_body={
            "status":"playbook created",
            "playbook_id":playbook_id,
            "capacity":{
                "playbook_write":self._extract_capacity(response),
                "playbook_name_mapping_write":self._extract_capacity(response2),
                "Idempotency_write":self._extract_capacity(response3)
                        }

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
                    "primary_id": "METADATA",
                    "secondary_id":f"PLAYBOOK#{playbook_id}"
                },
                UpdateExpression="SET is_deleted = :d, expire_at = :ttl",
                ConditionExpression="attribute_exists(secondary_id)",
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
