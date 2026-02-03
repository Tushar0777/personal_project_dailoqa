from .base import BaseService

class RoleService(BaseService):
    def get_permissions(self,role_name:str):
        response=self.table.get_item(
            Key={
                "primary_id":f"ROLE#{role_name}",
                "secondary_id":"METADATA"
            },
            ReturnConsumedCapacity="TOTAL"
        )


        return{
            "permissions":response.get("Item",{}).get("permissions",[]),
            "rcu":self._extract_capacity(response)
        }