from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from app.db.mongodb import get_database
from app.modules.auth.schemas import UserRegisterRequest, UserLoginRequest
from app.core.security import hash_password, verify_password, create_access_token


async def register_user(user_in: UserRegisterRequest):
    db = get_database()
    email_clean = user_in.email.strip().lower()

    # Check for existing email
    existing_user = await db["users"].find_one({"email": email_clean})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user_doc = {
        "name": user_in.name.strip(),
        "email": email_clean,
        "password_hash": hash_password(user_in.password),
        "created_at": datetime.now(timezone.utc)
    }

    try:
        result = await db["users"].insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    
    return {
        "id": str(result.inserted_id),
        "name": user_doc["name"],
        "email": user_doc["email"],
        "created_at": user_doc["created_at"]
    }


async def authenticate_user(credentials: UserLoginRequest):
    db = get_database()
    email_clean = credentials.email.strip().lower()

    user = await db["users"].find_one({"email": email_clean})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]}
    )

    user_data = {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "created_at": user.get("created_at", datetime.now(timezone.utc))
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }


async def get_current_user_by_id(user_id: str):
    db = get_database()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization payload.")
        
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "created_at": user.get("created_at", datetime.now(timezone.utc))
    }
