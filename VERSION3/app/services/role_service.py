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


# list of all the permissions
# VIEW_PLAYBOOK
# VIEW_PLAYBOOK_CONTENT
# CREATE_PLAYBOOK
# CREATE_VERSION
# EDIT_VERSION
# DELETE_PLAYBOOK
# DELETE_VERSION
# ASSIGN_ROLE
