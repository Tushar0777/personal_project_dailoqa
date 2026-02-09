from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from .base import BaseService
from datetime import datetime,timedelta
import time


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
            Key={
                "primary_id":f"PLAYBOOK#{playbook_id}",
                "secondary_id":f"VERSION#{version}"
            },
            ReturnConsumedCapacity="TOTAL"
        )

        return{
            "version":response.get("Item"),
            "rcu":self._extract_capacity(response)
        }
    
    # def add_version(self,playbook_id:str,version:int,content:str):
    #     now=datetime.utcnow().isoformat()
    #     try:
    #         response=self.table.put_item(
    #             Item={
    #                 "primary_id":f"PLAYBOOK#{playbook_id}",
    #                 "secondary_id":f"VERSION#{version}",
    #                 "entity_type":"PLAYBOOK_VERSION",
    #                 "version":version,
    #                 "content":content,
    #                 "created_at":now
    #             },
    #             ConditionExpression="attribute_not_exists(primary_id) AND attribute_not_exists(secondary_id)",
    #             ReturnConsumedCapacity="TOTAL"
    #         )
    #     except ClientError as e:
    #         if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
    #             return {"status": "VERSION_ALREADY_EXISTS"}
    #         raise

    #     return {
    #         "status": "VERSION_CREATED",
    #         "playbook_id": playbook_id,
    #         "version": version,
    #         "wcu": self._extract_capacity(response)
    #     }
    
    def add_version(self, playbook_id: str, content: str):
        now = datetime.utcnow().isoformat()

        # 1️⃣ Fetch metadata
        meta = self.table.get_item(
            Key={
                "primary_id": "METADATA",
                "secondary_id": f"PLAYBOOK#{playbook_id}"
            }
        ).get("Item")

        if not meta or meta.get("is_deleted"):
            return {"status": "PLAYBOOK_NOT_FOUND"}

        latest_version = meta.get("latest_version", 0)
        new_version = latest_version + 1

        # 2️⃣ Create version item
        try:
            response = self.table.put_item(
                Item={
                    "primary_id": f"PLAYBOOK#{playbook_id}",
                    "secondary_id": f"VERSION#{new_version}",
                    "entity_type": "PLAYBOOK_VERSION",
                    "version": new_version,
                    "content": content,
                    "created_at": now
                },
                ConditionExpression="attribute_not_exists(primary_id) AND attribute_not_exists(secondary_id)",
                ReturnConsumedCapacity="TOTAL"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {"status": "VERSION_ALREADY_EXISTS"}
            raise

        # 3️⃣ Atomically update metadata
        self.table.update_item(
            Key={
                "primary_id": "METADATA",
                "secondary_id": f"PLAYBOOK#{playbook_id}"
            },
            UpdateExpression="""
                SET latest_version = :lv,
                    total_versions = total_versions + :one,
                    updated_at = :t
            """,
            ExpressionAttributeValues={
                ":lv": new_version,
                ":one": 1,
                ":t": now
            }
        )

        return {
            "status": "VERSION_CREATED",
            "playbook_id": playbook_id,
            "version": new_version,
            "wcu": self._extract_capacity(response)
        }
    
    def get_latest_version(self, playbook_id: str):
    # 1️⃣ Fetch metadata
        meta = self.table.get_item(
            Key={
                "primary_id": "METADATA",
                "secondary_id": f"PLAYBOOK#{playbook_id}"
            },
            ReturnConsumedCapacity="TOTAL"
        )

        metadata = meta.get("Item")
        if not metadata or metadata.get("is_deleted"):
            return {"status": "PLAYBOOK_NOT_FOUND"}

        latest_version = metadata.get("latest_version", 0)

        if latest_version == 0:
            return {"status": "NO_VERSIONS"}

        # 2️⃣ Fetch latest version item
        version = self.table.get_item(
            Key={
                "primary_id": f"PLAYBOOK#{playbook_id}",
                "secondary_id": f"VERSION#{latest_version}"
            },
            ReturnConsumedCapacity="TOTAL"
        )

        item = version.get("Item")
        if not item or item.get("is_deleted"):
            return {"status": "LATEST_VERSION_NOT_AVAILABLE"}

        return {
            "status": "OK",
            "version": item,
            "latest_version": latest_version,
            "rcu": (
                self._extract_capacity(meta) +
                self._extract_capacity(version)
            )
        }

    
    # def soft_delete_version(self, playbook_id: str, version: int):
    #     response = self.table.update_item(
    #         Key={
    #             "primary_id": f"PLAYBOOK#{playbook_id}",
    #             "secondary_id": f"VERSION#{version}"
    #         },
    #         UpdateExpression="SET is_deleted = :d, deleted_at = :t",
    #         ExpressionAttributeValues={
    #             ":d": True,
    #             ":t": datetime.utcnow().isoformat()
    #         },
    #         ReturnConsumedCapacity="TOTAL"
    #     )
    #     return {
    #         "status": "VERSION_SOFT_DELETED",
    #         "wcu": self._extract_capacity(response)
    #     }
    
    # def hard_delete_version(self, playbook_id: str, version: int):
    #     response = self.table.delete_item(
    #         Key={
                # "primary_id": f"PLAYBOOK#{playbook_id}",
        #         "secondary_id": f"VERSION#{version}"
        #     },
        #     ReturnConsumedCapacity="TOTAL"
        # )
        # return {
        #     "status": "VERSION_HARD_DELETED",
        #     "wcu": self._extract_capacity(response)
        # }
    
    def delete_version(self, playbook_id: str, version: int):
        # expire_at = int(
        #     (datetime.utcnow() + timedelta(minutes=ttl_minutes)).timestamp()
        # )
        ttl_days = 7
        expire_at = int(time.time()) + (ttl_days * 24 * 60 * 60)

        try:
            response = self.table.update_item(
                Key={
                    "primary_id": f"PLAYBOOK#{playbook_id}",
                    "secondary_id": f"VERSION#{version}"
                },
                UpdateExpression="""
                    SET is_deleted = :d,
                        deleted_at = :t,
                        timetolive = :ttl
                """,
                ConditionExpression="attribute_exists(primary_id)",
                ExpressionAttributeValues={
                    ":d": True,
                    ":t": datetime.utcnow().isoformat(),
                    ":ttl": expire_at
                },
                ReturnConsumedCapacity="TOTAL"
            )
        # except ClientError as e:
        #     if e["Error"]["Code"] == "ConditionalCheckFailedException":
        #         return {"status": "VERSION_NOT_FOUND"}
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {"status": "VERSION_NOT_FOUND"}
            raise

        return {
            "status": "VERSION_MARKED_FOR_DELETION",
            "ttl_epoch": expire_at,
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
            UpdateExpression='''
            SET content = :c, 
                previous_content = if_not_exists(previous_content, :pc), 
                updated_at = :t''',
            ConditionExpression="attribute_exists(primary_id)",
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
