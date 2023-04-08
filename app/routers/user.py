from fastapi import APIRouter, Depends
from bson.objectid import ObjectId
from app.serializers.userSerializers import userResponseEntity

from app.db import User
from .. import schemas
from app.auth.auth import AuthHandler

router = APIRouter()
auth_handler= AuthHandler()

@router.get('/protected', response_model=schemas.UserResponse)
def protected(user_id: str = Depends(auth_handler.auth_wrapper)):
    user = userResponseEntity(User.find_one({'_id':ObjectId(str(user_id))}))
    return {'status': 'success', "user": user}

@router.get('/hola')
def protected():
    return {'status': 'success', "user": "holamundo"}