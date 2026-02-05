from fastapi import Depends,HTTPException,status,Header
from fastapi.security import OAuth2PasswordBearer
# from app.auth.jwt_utils import JWTService
from ..auth.jwt_utils import JWTService
# from app.services.user_service import UserService
from ..services.user_service import UserService
# from app.services.role_service import RoleService
from ..services.role_service import RoleService


# oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_user_service()->UserService:
    return UserService()

def get_role_service() -> RoleService:
    return RoleService()


def verify_token(token: str):
    user_id = JWTService.decode_token(token)

    # user_service = get_user_service
    # result = user_service.get_user(user_id)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    user_service=get_user_service()
    result=user_service.get_user(user_id)

    if not result["user"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found"
        )
    
    return user_id

    # if not result["user"]:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="User not found"
    #     )

    # return user_id

def get_current_user(authorization:str=Header(...,alias="Authorization"))->str:
    # user_id=JWTService.decode_token(token)

    # if not user_id:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or Expired token")
    

    # return user_id
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    return user


def get_current_user_role(user_id:str=Depends(get_current_user),
                          user_service:UserService=Depends(get_user_service)
                          ):
    result=user_service.get_user_roles(user_id)
    roles=result["roles"]

    if not roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no role assigned")

    return roles


def require_permission(permission:str):
    def checker(roles:list[str]=Depends(get_current_user_role),
                role_service:RoleService=Depends(get_role_service)
                ):
        
        for role in roles:
            perms=role_service.get_permissions(role)["permissions"]
            if permission in perms:
                return True
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"missing permissions {permission}")
        

    return checker


    

# from fastapi import Depends, HTTPException, status, Header
# from ..auth.jwt_utils import JWTService
# from ..services.user_service import UserService
# from ..services.role_service import RoleService


# # ---------- SERVICES ----------

# def get_user_service() -> UserService:
#     return UserService()

# def get_role_service() -> RoleService:
#     return RoleService()


# # ---------- AUTH ----------

# def verify_token(token: str) -> str:
#     user_id = JWTService.decode_token(token)

#     if not user_id:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token"
#         )

#     user_service = get_user_service()
#     result = user_service.get_user(user_id)

#     if not result["user"]:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found"
#         )

#     return user_id


# def get_current_user(authorization: str = Header(...)) -> str:
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid Authorization header"
#         )

#     token = authorization.replace("Bearer ", "")
#     return verify_token(token)


# # ---------- RBAC ----------

# def get_current_user_role(
#     user_id: str = Depends(get_current_user),
#     user_service: UserService = Depends(get_user_service)
# ):
#     result = user_service.get_user_roles(user_id)
#     roles = result["roles"]

#     if not roles:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="No role assigned"
#         )

#     return roles


# def require_permission(permission: str):
#     def checker(
#         roles: list[str] = Depends(get_current_user_role),
#         role_service: RoleService = Depends(get_role_service)
#     ):
#         for role in roles:
#             perms = role_service.get_permissions(role)["permissions"]
#             if permission in perms:
#                 return True

#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=f"Missing permission: {permission}"
#         )

#     return checker

