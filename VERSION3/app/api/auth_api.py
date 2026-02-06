from fastapi import APIRouter,HTTPException,status,Depends,Body
# from app.auth.jwt_utils import JWTService
from ..auth.jwt_utils import JWTService
# from app.services.user_service import UserService
from ..services.user_service import UserService


router=APIRouter(prefix="/auth",tags=["Auth"])


def get_user_service()->UserService:
    return UserService()


@router.post("/login")
def login(
    user_name:str=Body(...),
    password:str=Body(...),
    user_service:UserService=Depends(get_user_service)):
# user id leke
    result = user_service.get_user_by_username(user_name)
    if not result["user"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = result["user"]
    print(user)

    if user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    user_id=user["user_id"]
    role=user_service.get_user_roles(user_id)
    token = JWTService.create_access_token(user_id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "role":role["roles"] 
    }



#     result=user_service.get_user(user_id)
#     if not result["user"]:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
# # creat acess token ye token bana dega us user ka    
#     token=JWTService.create_access_token(user_id)

#     return {
#         "access_token": token,
#         "token_type": "bearer"
#     }