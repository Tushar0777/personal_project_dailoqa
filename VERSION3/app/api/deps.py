from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
# from app.auth.jwt_utils import JWTService
from ..auth.jwt_utils import JWTService
# from app.services.user_service import UserService
from ..services.user_service import UserService
# from app.services.role_service import RoleService
from ..services.role_service import RoleService


oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_service()->UserService:
    return UserService()

def get_role_service() -> RoleService:
    return RoleService()


def get_current_user_id(token:str=Depends(oauth2_scheme))->str:
    user_id=JWTService.decode_token(token)

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or Expired token")
    

    return user_id


def get_current_user_role(user_id:str=Depends(get_current_user_id),
                          user_service:UserService=Depends(get_user_service)
                          ):
    result=user_service.get_user_roles(user_id)
    roles=result["roles"]

    if not roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="no role assigned")

    return roles


def require_permission(permission:str):
    def checker(roles:list[str]=Depends(get_current_user_role),
                role_service:RoleService=Depends(get_role_service)
                ):
        
        for role in roles:
            perms=role_service.get_permissions(role)["permissions"]
            if permission in perms:
                return True
            
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"missing permissions {permission}")
        

    return checker
    

# # dummy function for now
# def get_current_user():
#     # Replace with your auth logic later (JWT/OAuth)
#     return {"username": "dummy_user", "permissions": ["VIEW_PLAYBOOK", "ADD_PLAYBOOK"]}

# def require_permission(permission_name: str):
#     def dependency(user=Depends(get_current_user)):
#         # user.permissions should be a list of permissions
#         if permission_name not in user.get("permissions", []):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"You don't have permission: {permission_name}"
#             )
#         return True
#     return dependency

        

    


