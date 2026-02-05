from .base import BaseService
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime

class PermissionService(BaseService):
    """
    Service to manage role permissions and user permissions.
    """

    # ---------- ROLE PERMISSIONS ----------

    def list_permissions(self, role_name: str):
        """List permissions assigned to a role."""
        response = self.table.get_item(
            Key={
                "primary_id": f"ROLE#{role_name}",
                "secondary_id": "METADATA"
            },
            ReturnConsumedCapacity="TOTAL"
        )

        permissions = response.get("Item", {}).get("permissions", [])
        return {
            "role": role_name,
            "permissions": permissions,
            "rcu": self._extract_capacity(response)
        }

    def add_permission(self, role_name: str, permission: str):
        """Add a permission to a role."""
        response = self.table.update_item(
            Key={
                "primary_id": f"ROLE#{role_name}",
                "secondary_id": "METADATA"
            },
            UpdateExpression="SET permissions = list_append(if_not_exists(permissions, :empty), :p)",
            ExpressionAttributeValues={
                ":p": [permission],
                ":empty": []
            },
            ReturnConsumedCapacity="TOTAL"
        )
        return {
            "status": "PERMISSION_ADDED",
            "role": role_name,
            "permission": permission,
            "wcu": self._extract_capacity(response)
        }

    def remove_permission(self, role_name: str, permission: str):
        """Remove a permission from a role."""
        current = self.table.get_item(
            Key={
                "primary_id": f"ROLE#{role_name}",
                "secondary_id": "METADATA"
            }
        )
        item = current.get("Item")
        if not item:
            return {"status": "ROLE_NOT_FOUND"}

        permissions = item.get("permissions", [])
        if permission not in permissions:
            return {"status": "PERMISSION_NOT_FOUND"}

        permissions.remove(permission)

        response = self.table.update_item(
            Key={
                "primary_id": f"ROLE#{role_name}",
                "secondary_id": "METADATA"
            },
            UpdateExpression="SET permissions = :p",
            ExpressionAttributeValues={":p": permissions},
            ReturnConsumedCapacity="TOTAL"
        )

        return {
            "status": "PERMISSION_REMOVED",
            "role": role_name,
            "permission": permission,
            "wcu": self._extract_capacity(response)
        }

    def assign_all_permissions(self, role_name: str, all_permissions: list[str]):
        """Assign all permissions to a role (overwrite existing)."""
        response = self.table.update_item(
            Key={
                "primary_id": f"ROLE#{role_name}",
                "secondary_id": "METADATA"
            },
            # UpdateExpression="SET permissions = :p",
            UpdateExpression="SET #p = :p",
            ExpressionAttributeNames={
            "#p": "permissions"  # reserved keyword ko map kar rahe
            },
            ExpressionAttributeValues={
                ":p": all_permissions
            },
            ReturnValues="UPDATED_NEW",
            ReturnConsumedCapacity="TOTAL"
        )
        return {
            "status": "ALL_PERMISSIONS_ASSIGNED",
            "role": role_name,
            "permissions": all_permissions,
            "wcu": self._extract_capacity(response)
        }

    def bootstrap_admin_permissions(self, all_permissions: list[str]):
        """Assign all permissions to ADMIN role."""
        return self.assign_all_permissions("ADMIN", all_permissions)

    # ---------- USER PERMISSIONS ----------

    def get_user_permissions(self, user_id: str, user_service, role_service):
        """Get aggregated permissions of a user from their roles."""
        roles_result = user_service.get_user_roles(user_id)
        roles = roles_result.get("roles", [])

        if not roles:
            return {"user_id": user_id, "roles": [], "permissions": []}

        user_permissions = set()
        for role in roles:
            perms = role_service.get_permissions(role).get("permissions", [])
            user_permissions.update(perms)

        return {
            "user_id": user_id,
            "roles": roles,
            "permissions": list(user_permissions)
        }

    def list_all_users_with_roles_permissions(self, user_service, role_service):
        """List all users with username, roles, and permissions."""
        response = self.table.scan(
            FilterExpression=Attr("entity_type").eq("USER"),
            ReturnConsumedCapacity="TOTAL"
        )

        users = []
        for item in response.get("Items", []):
            user_id = item.get("primary_id").replace("USER#", "")
            username = item.get("username")
            user_info = self.get_user_permissions(user_id, user_service, role_service)
            user_info["username"] = username
            users.append(user_info)

        return {
            "users": users,
            "rcu": self._extract_capacity(response)
        }





# from .base import BaseService
# from boto3.dynamodb.conditions import Key, Attr
# from datetime import datetime

# class PermissionService(BaseService):
#     """
#     Manage permissions for roles.
#     """

#     def list_permissions(self, role_name: str):
#         """
#         Returns the list of permissions assigned to a role.
#         """
#         response = self.table.get_item(
#             Key={
#                 "primary_id": f"ROLE#{role_name}",
#                 "secondary_id": "METADATA"
#             },
#             ReturnConsumedCapacity="TOTAL"
#         )

#         permissions = response.get("Item", {}).get("permissions", [])
#         return {
#             "role": role_name,
#             "permissions": permissions,
#             "rcu": self._extract_capacity(response)
#         }

#     def add_permission(self, role_name: str, permission: str):
#         """
#         Add a permission to a role.
#         """
#         # Append permission to existing list or create new list
#         response = self.table.update_item(
#             Key={
#                 "primary_id": f"ROLE#{role_name}",
#                 "secondary_id": "METADATA"
#             },
#             UpdateExpression="SET permissions = list_append(if_not_exists(permissions, :empty), :p)",
#             ExpressionAttributeValues={
#                 ":p": [permission],
#                 ":empty": []
#             },
#             ReturnConsumedCapacity="TOTAL"
#         )
#         return {
#             "status": "PERMISSION_ADDED",
#             "role": role_name,
#             "permission": permission,
#             "wcu": self._extract_capacity(response)
#         }

#     def remove_permission(self, role_name: str, permission: str):
#         """
#         Remove a permission from a role.
#         """
#         # Get current permissions first
#         current = self.table.get_item(
#             Key={
#                 "primary_id": f"ROLE#{role_name}",
#                 "secondary_id": "METADATA"
#             }
#         )
#         item = current.get("Item")
#         if not item:
#             return {"status": "ROLE_NOT_FOUND"}

#         permissions = item.get("permissions", [])
#         if permission not in permissions:
#             return {"status": "PERMISSION_NOT_FOUND"}

#         permissions.remove(permission)

#         response = self.table.update_item(
#             Key={
#                 "primary_id": f"ROLE#{role_name}",
#                 "secondary_id": "METADATA"
#             },
#             UpdateExpression="SET permissions = :p",
#             ExpressionAttributeValues={
#                 ":p": permissions
#             },
#             ReturnConsumedCapacity="TOTAL"
#         )

#         return {
#             "status": "PERMISSION_REMOVED",
#             "role": role_name,
#             "permission": permission,
#             "wcu": self._extract_capacity(response)
#         }

#     def assign_all_permissions(self, role_name: str, all_permissions: list[str]):
#         """
#         Overwrites role's permissions with a full list (useful for ADMIN).
#         """
#         response = self.table.update_item(
#             Key={
#                 "primary_id": f"ROLE#{role_name}",
#                 "secondary_id": "METADATA"
#             },
#             UpdateExpression="SET permissions = :p",
#             ExpressionAttributeValues={
#                 ":p": all_permissions
#             },
#             ReturnConsumedCapacity="TOTAL"
#         )

#         return {
#             "status": "ALL_PERMISSIONS_ASSIGNED",
#             "role": role_name,
#             "permissions": all_permissions,
#             "wcu": self._extract_capacity(response)
#         }
    

#     def bootstrap_admin_permissions(self, all_permissions: list[str]):
#         """
#         Assign all permissions to ADMIN role.
#         """
#         return self.assign_all_permissions("ADMIN", all_permissions)

#     def get_user_permissions(self, user_id: str, user_service, role_service):
#         """
#         Returns all permissions of a user by aggregating permissions from their roles.
#         """
#         roles_result = user_service.get_user_roles(user_id)
#         roles = roles_result.get("roles", [])

#         if not roles:
#             return {"user_id": user_id, "permissions": [], "roles": []}

#         user_permissions = set()
#         for role in roles:
#             perms = role_service.get_permissions(role).get("permissions", [])
#             user_permissions.update(perms)

#         return {
#             "user_id": user_id,
#             "roles": roles,
#             "permissions": list(user_permissions)
#         }

#     def list_all_users_with_roles_permissions(self, user_service, role_service):
#         """
#         Returns all users with their username, roles, and permissions.
#         """
#         # Scan all user profiles
#         response = self.table.scan(
#             FilterExpression=Attr("entity_type").eq("USER"),
#             ReturnConsumedCapacity="TOTAL"
#         )

#         users = []
#         for item in response.get("Items", []):
#             user_id = item.get("primary_id").replace("USER#", "")
#             username = item.get("username")
#             # Fetch user permissions using get_user_permissions
#             user_info = self.get_user_permissions(user_id, user_service, role_service)
#             user_info["username"] = username
#             users.append(user_info)

#         return {
#             "users": users,
#             "rcu": self._extract_capacity(response)
#         }
