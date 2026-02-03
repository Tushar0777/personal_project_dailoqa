from fastapi import APIRouter,Depends
from ..services.user_service import UserService
from ..api.deps import require_permission

router=APIRouter(prefix="/users",tags=['users'])

def get_user_service():
    return UserService()

@router.post("/",dependencies=[Depends(require_permission("CREATE_USER"))])
def create_user(user_id:str,name:str,service:UserService=Depends(get_user_service)):
    return service.create_user(user_id,name)


@router.post("{user_id}/roles",dependencies=[Depends(require_permission("ASSIGN_ROLE"))])
def assign_role(user_id:str,role:str,service:UserService=Depends(get_user_service)):
    return service.assign_role(user_id=user_id,role=role)

@router.delete("{user_id}/roles",dependencies=[Depends(require_permission("ASSIGN_ROLE"))])
def remove_role(user_id:str,role:str,service:UserService=Depends(get_user_service)):
    return service.remove_role(user_id=user_id,role=role)
