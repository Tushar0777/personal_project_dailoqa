from fastapi import APIRouter,Depends,HTTPException,status,Body
from ..services.user_service import UserService
from ..services.role_service import RoleService
from ..services.permission_service import PermissionService
from ..api.deps import require_permission
from botocore.exceptions import ClientError

router=APIRouter(prefix="/users",tags=['users'])

def get_user_service():
    return UserService()

def get_user_role():
    return RoleService()

def get_permission_service():
    return PermissionService()


@router.post("/")
def create_user(
    username:str=Body(...),
    password:str=Body(...),
    service:UserService=Depends(get_user_service)):
    try:
        result=service.create_user(username,password)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        # Username already exists
        if error_code == "ConditionalCheckFailedException":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        # Any other DynamoDB error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating user"
        )

    except Exception as e:
        # Fallback safety net
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred"
        )

    return result


@router.delete("/{user_name}/roles",dependencies=[Depends(require_permission("ASSIGN_ROLE"))])
def remove_role(
    user_name:str,
    role:str=Body(...),
    user_service:UserService=Depends(get_user_service)):
     result=user_service.get_user_by_username(username=user_name)

     if not result["user"]:
         return{
             "removed":False,
             "reason":"User not found",
             "wcu":0
         }
     user_id=result["user"]["user_id"]
     
     response=user_service.remove_role(user_id=user_id,role=role)
     if not response["removed"]:
         return {
            "status": "ROLE_NOT_ASSIGNED",
            "user_name": user_name,
            "role": role,
            "wcu": 0
        }
     return {
            "status": "ROLE_REMOVED",
            "user_name": user_name,
            "role": role,
            "wcu": response["wcu"]
        }


@router.post(
    "/assign-role",
    dependencies=[Depends(require_permission("ASSIGN_ROLE"))]
)
def assign_role_by_username(
        user_name:str=Body(...),
        role:str=Body(...),
        user_service:UserService=Depends(get_user_service),
        role_service:RoleService=Depends(get_user_role)
):
      # username → user
    result = user_service.get_user_by_username(user_name)

    if not result["user"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_id = result["user"]["user_id"]

    # assign role
    response = user_service.assign_role(user_id, role)

    if not response["assigned"]:
        return {
            "status": "ROLE_ALREADY_ASSIGNED",
            "username": user_name,
            "role": role,
            "wcu": 0
        }

    return {
        "status": "ROLE_ASSIGNED",
        "username": user_name,
        "role": role,
        "wcu": response.get("ConsumedCapacity", {}).get("CapacityUnits", 0)
    }


@router.get("/all-users", dependencies=[Depends(require_permission("VIEW_ROLE"))])
def list_all_users(service: PermissionService = Depends(get_permission_service),
                   user_service: UserService = Depends(get_user_service),
                   role_service: RoleService = Depends(get_user_role)):
    return service.list_all_users_with_roles_permissions(user_service, role_service)


@router.post("/bootstrap-admin")
def bootstrap_admin(
    username: str,
    service: UserService = Depends(get_user_service)
):
    result = service.get_user_by_username(username)

    if not result["user"]:
        raise HTTPException(404, "User not found")

    user_id = result["user"]["user_id"]

    service.assign_role(user_id, "ADMIN")

    return {
        "status": "BOOTSTRAP_ADMIN_DONE",
        "username": username
    }