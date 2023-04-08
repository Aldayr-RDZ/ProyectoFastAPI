from fastapi import APIRouter, status, HTTPException, Depends, Response, Request
from random import randbytes
import random
import hashlib
from app.email import Email
from pydantic import EmailStr
# module of database
from app.db import User
from datetime import datetime
from .. import schemas
from app.auth.auth import AuthHandler
from app.serializers.userSerializers import userEntity, userResponseEntity

auth_handler= AuthHandler()
router = APIRouter()


@router.get('/users')
def get_all_users():
    collection_name = User.find()
    dictionary_users= {'users':[]}
    for item in collection_name:
        item['_id'] = str(item['_id'])
        dictionary_users["users"].append(item)
        
    return dictionary_users
    

@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def register(auth_details: schemas.CreateUserSchema):
    
    #Verificar si el email existe
    user = User.find_one({'email':auth_details.email.lower()})
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Acount already exist")
    #Comparamos si constraseña y confirmar contraseña
    if auth_details.password != auth_details.passwordConfirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password do not match')
    # Hash la contraseña
    auth_details.password = AuthHandler().get_password_hash(password=auth_details.password)
    del auth_details.passwordConfirm
    auth_details.role = 'user'
    auth_details.verified = True
    auth_details.email = auth_details.email.lower()
    auth_details.created_at = datetime.utcnow()
    auth_details.updated_at= auth_details.created_at
    result = User.insert_one(auth_details.dict())
    new_user = userResponseEntity(User.find_one({'_id':result.inserted_id}))
    return {"status": "success", "user": new_user}

# @router.post('/register', status_code=status.HTTP_201_CREATED)
# async def register(auth_details: schemas.CreateUserSchema, request: Request):
    
#     #Verificar si el email existe
#     user = User.find_one({'email':auth_details.email.lower()})
#     if user:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Acount already exist")
#     #Comparamos si constraseña y confirmar contraseña
#     if auth_details.password != auth_details.passwordConfirm:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password do not match')
#     # Hash la contraseña
#     auth_details.password = AuthHandler().get_password_hash(password=auth_details.password)
#     del auth_details.passwordConfirm
#     auth_details.role = 'user'
#     auth_details.verified = False
#     auth_details.email = auth_details.email.lower()
#     auth_details.created_at = datetime.utcnow()
#     auth_details.updated_at= auth_details.created_at
#     result = User.insert_one(auth_details.dict())
#     # new_user = userResponseEntity(User.find_one({'_id':result.inserted_id}))
#     new_user = User.find_one({'_id':result.inserted_id})
#     try:
#         token = randbytes(10)
#         hashedCode = hashlib.sha256()
#         hashedCode.update(token)
#         verification_code = hashedCode.hexdigest()
#         print(verification_code)
#         User.find_one_and_update({"_id": result.inserted_id}, {
#             "$set": {"verification_code": verification_code, "updated_at": datetime.utcnow()}})

#         url = f"{request.url.scheme}://{request.client.host}:{request.url.port}/api/auth/verifyemail/{token.hex()}"
#         await Email(userEntity(new_user), url, [EmailStr(auth_details.email)]).sendVerificationCode()
#     except Exception as error:
#         User.find_one_and_update({"_id": result.inserted_id}, {
#             "$set": {"verification_code": None, "updated_at": datetime.utcnow()}})
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                             detail='There was an error sending email')
#     return {'status': 'success', 'message': 'Verification token successfully sent to your email'}
    
@router.post('/login')
def login(auth_details: schemas.LoginUserSchema, response: Response, Authorize: AuthHandler = Depends()):
    #Verificamos si el usuario existe
    db_user = User.find_one({"email":auth_details.email})
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect Email or Password')
    user = userEntity(db_user)

    #Verificamos si la contraaseña es valida 
    if not Authorize.verify_password(auth_details.password, user['password']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrecto Email or Password')
    
    #Creamos el access token 
    access_token = Authorize.encode_token(str(user['id']))
    response.set_cookie('access_token', access_token, 5000 *60, 5000*60, '/', None, False, True, 'lax')
    return{'status':'success', 'access_token':access_token}

# @router.get('/verifyemail/{token}')
# def verify_me(token: str):
#     hashedCode = hashlib.sha256()
#     hashedCode.update(bytes.fromhex(token))
#     verification_code = hashedCode.hexdigest()
#     result = User.find_one_and_update({"verification_code": verification_code}, {
#         "$set": {"verification_code": None, "verified": True, "updated_at": datetime.utcnow()}}, new=True)
#     if not result:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail='Invalid verification code or account already verified')
#     return {
#         "status": "success",
#         "message": "Account verified successfully"
#     }
