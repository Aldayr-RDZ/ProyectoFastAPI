from fastapi import APIRouter, status, HTTPException, Depends, Response
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
from bson.objectid import ObjectId
# from typing import Union
# image upload
# import secrets
# from fastapi import File, UploadFile
# from PIL import Image
# from fastapi.staticfiles import StaticFiles
# import os

# from pymongo.errors import DuplicateKeyError

# module of database
from app.db import User
from datetime import datetime
from .. import schemas
from app.auth.auth import AuthHandler
from app.serializers.userSerializers import userEntity, userResponseEntity


auth_handler= AuthHandler()
router = APIRouter()
# CORS
# origins = ['*']

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=['*'],
#     allow_headers=['*']
# )


# dbname = get_database()
# User = dbname["users"]

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
    
    print(auth_details)
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

# @router.post('/login')
# def login(auth_details: AuthDetails):
#     user = None
#     for x in users:
#         if x['username'] == auth_details.username:
#             user = x
#             break
    
#     if (user is None) or (not auth_handler.verify_password(auth_details.password, user['password'])):
#         raise HTTPException(status_code=401, detail='Invalid username and/or password')
#     token = auth_handler.encode_token(user['username'])
#     return {'token':token}


@router.get('/protected', response_model=schemas.UserResponse)
def protected(user_id: str = Depends(AuthHandler().auth_wrapper)):
    user = userResponseEntity(User.find_one({'_id':ObjectId(str(user_id))}))
    return {'status': 'success', "user": user}


@router.get('/unprotected')
def unprotected():
    return {'hello': 'world'}


# @router.post("/project", status_code=status.HTTP_201_CREATED)
# async def save_project(request: Request) -> dict:

#     collection_name = dbname["projects"]
#     try:
#         params = await request.json()
#         collection_name.insert_one(params)
#         params['_id'] = str(params['_id'])
#         return {"status": "success"}
#     except DuplicateKeyError:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT,
#                             detail=f'Post with same email')


# @router.get("/project/{id}")
# def get_project(id: str) -> dict:
#     collection_name = dbname["projects"]
#     item_details = collection_name.find_one(ObjectId(id))
#     if item_details == None:
#         return {"status": "error", "details": f"not found project with id {id} in the collection"}
#     else:
#         item_details["_id"] = str(item_details["_id"])
#     return item_details


# @router.get("/projects")
# def get_projects(limit: int = 10, page: int = 1, search: str = '') -> dict:

#     collection_name = dbname["projects"]
#     item_details = collection_name.find().skip(page).limit(limit)
#     diccionary_projects = {"items": []}
#     for item in item_details:
#         item['_id'] = str(item['_id'])
#         diccionary_projects["items"].append(item)

#     return diccionary_projects


# @router.put("/projects/{id}")
# async def update_project(id: str, request: Request) -> dict:
#     collection_name = dbname["projects"]

#     params = await request.json()
#     project_updated = collection_name.find_one_and_update(
#         {"_id": ObjectId(id)}, {"$set": dict(params)})

#     if project_updated == None:
#         return {"status": "error", "details": f"not found project to updated with id {id} in the collection"}
#     else:
#         return {"status": "success", "detail": "Project updated"}


# @router.delete("/projects/{id}")
# def delete_project(id: str) -> dict:
#     collection_name = dbname["projects"]
#     project_deleted = collection_name.find_one_and_delete(
#         {"_id": ObjectId(id)})
#     print(project_deleted)
#     if project_deleted == None:
#         return {"status": "error", "details": f"not found project to deleted with id {id} in the collection"}
#     else:
#         return {"status": "success", "detail": "Project deleted"}


# app.mount("/static", StaticFiles(directory="static"), name="static")


# @router.post("/upload-image/{id}")
# async def upload_image(id: str, file: Union[UploadFile, None] = File(...)) -> dict:

#     if not file.filename:
#         return {"message": "No upload file sent"}
#     else:
#         collection_name = dbname["projects"]
#         FILEPATH = "./static/images/"
#         filename = file.filename
#         extension = filename.split('.')[1]

#         if extension not in ["png", "jpg"]:
#             return {"status": "error", "detail": "File extension not allowed"}

#         # uasdi122.jpg
#         token_name = secrets.token_hex(10)+"."+extension
#         generated_name = FILEPATH + token_name
#         file_content = await file.read()

#         with open(generated_name, "wb") as file:
#             file.write(file_content)

#         # PILLOW
#         img = Image.open(generated_name)
#         # img = img.resize(size=(300, 300))
#         img.save(generated_name)

#         update_object = collection_name.find_one_and_update(
#             {"_id": ObjectId(id)}, {"$set": {"image": token_name}})
#         file.close()
#         file_url = "localhost:8000" + generated_name[1:]
#         update_object["_id"] = str(update_object['_id'])
#         return {"status": file_url, "data_updated":  update_object}


# @router.get("/get-image/{image}")
# def getFileImage(file_name: str):
#     path_file = "./static/images/" + file_name
#     if file_name in [file for file in os.listdir("./static/images/")]:
#         return FileResponse(path=path_file)
#     else:
#         return {"status": "error", "details": "not found image"}

    # file_name= image
    # path_file = './static/images/' + file_name
    # lista_files = [file for file in os.listdir('./static/images/')]
    # print(lista_files)
    # if file_name in lista_files:
    #     return FileResponse(path=path_file)
    # else:
    #     return  {"status": "error", "details": "not found image"}



