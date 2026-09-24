from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.modules.auth.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    MessageResponse
)
from app.modules.auth.service import register_user, authenticate_user, get_current_user_by_id
from app.core.security import decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials are required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload["sub"]
    user = await get_current_user_by_id(user_id)
    return UserResponse(**user)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest):
    user = await register_user(payload)
    return UserResponse(**user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest):
    auth_data = await authenticate_user(payload)
    return TokenResponse(**auth_data)


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout():
    return MessageResponse(message="Successfully logged out.")
