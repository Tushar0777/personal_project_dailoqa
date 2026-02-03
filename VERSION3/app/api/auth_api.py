from fastapi import APIRouter,HTTPException,status
from app.auth.jwt_utils import JWTService
from app.services.user_service import UserService


router=APIRouter(prefix="/auth",tags=["Auth"])

@router.post("/login")
def login(user_id):

    user=UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
    
    token=JWTService.create_access_token(user_id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }