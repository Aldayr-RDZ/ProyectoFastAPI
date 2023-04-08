
from fastapi import APIRouter, status, Request, HTTPException, Response, Depends
from bson import ObjectId
from app.db import Project
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from typing import Union


# image upload
from fastapi.responses import FileResponse
import secrets
from fastapi import File, UploadFile
from PIL import Image
from fastapi.staticfiles import StaticFiles
import os
import secrets

from pymongo.collection import ReturnDocument

from .. import schemas
from app.serializers.projectSerializers import projectResponseEntity, projectListEntity
from app.auth.auth import AuthHandler
auth_handler = AuthHandler()
router = APIRouter()

# @router.post("/project", status_code=status.HTTP_201_CREATED)
# async def save_project(request: Request) -> dict:

#     collection_name = Project
#     try:
#         params = await request.json()
#         collection_name.insert_one(params)
#         params['_id'] = str(params['_id'])
#         return {"status": "success"}
#     except DuplicateKeyError:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT,
#                             detail=f'Post with same email')


@router.post("/project", status_code=status.HTTP_201_CREATED)
def create_project(project_details: schemas.CreateProjectSchema, user_id: str = Depends(auth_handler.auth_wrapper)):
    project_details.user = ObjectId(user_id)
    project_details.created_at = datetime.utcnow()
    project_details.update_at = project_details.created_at
    try:
        result = Project.insert_one(project_details.dict())
        pipeline = [
            {'$match': {'_id': result.inserted_id}},
            {'$lookup': {'from': 'users', 'localField': 'user',
                         'foreignField': '_id', 'as': 'user'}},
            {'$unwind': '$user'},
        ]
        new_project = projectListEntity(Project.aggregate(pipeline))[0]
        return new_project
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Project with title: '{project_details.name}' already exists")


# @router.get("/project/{id}")
# def get_project(id: str) -> dict:
#     collection_name = Project
#     item_details = collection_name.find_one(ObjectId(id))
#     if item_details == None:
#         return {"status": "error", "details": f"not found project with id {id} in the collection"}
#     else:
#         item_details["_id"] = str(item_details["_id"])
#     return item_details


@router.get('/project/{project_id}')
def get_project(project_id: str, user_id: str = Depends(auth_handler.auth_wrapper)):
    result = Project.find_one(ObjectId(project_id))
    project = projectResponseEntity(result)
    return {"status": "success", "project": project}

# @router.get("/projects")
# def get_projects(limit: int = 10, page: int = 1, search: str = '') -> dict:

#     collection_name = Project
#     item_details = collection_name.find().skip(page).limit(limit)
#     diccionary_projects = {"items": []}
#     for item in item_details:
#         item['_id'] = str(item['_id'])
#         diccionary_projects["items"].append(item)

#     return diccionary_projects


@router.get('/projects')  # checar este
def get_projects(limit: int = 10, page: int = 1, user_id: str = Depends(auth_handler.auth_wrapper)):
    skip = (page - 1) * limit
    pipeline = [
        {'$match': {}},

        {'$lookup': {'from': 'users', 'localField': 'user',
                     'foreignField': '_id', 'as': 'user'}},
        {'$unwind': '$user'},
        {
            '$skip':skip
        },{
            '$limit':limit
        }

    ]
   
    projects = projectListEntity(Project.aggregate(pipeline))
    return {"status": "success", 'results':len(projects),"projects": projects}

# @router.put("/project/{id}")
# async def update_project(id: str, request: Request) -> dict:
#     collection_name = Project

#     params = await request.json()
#     project_updated = collection_name.find_one_and_update(
#         {"_id": ObjectId(id)}, {"$set": dict(params)})

#     if project_updated == None:
#         return {"status": "error", "details": f"not found project to updated with id {id} in the collection"}
#     else:
#         return {"status": "success", "detail": "Project updated"}


@router.put('/projects/{project_id}')
def update_project(project_id: str, project_details: schemas.UpdateProjectSchema):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid id: {project_id}")
    updated_post = Project.find_one_and_update(
        {'_id': ObjectId(project_id)}, {'$set': project_details.dict(exclude_none=True)}, return_document=ReturnDocument.AFTER)
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No post with this id: {project_id} found')
    return projectResponseEntity(updated_post)


# @router.delete("/projects/{id}")
# def delete_project(id: str) -> dict:
#     collection_name = Project
#     project_deleted = collection_name.find_one_and_delete(
#         {"_id": ObjectId(id)})
#     print(project_deleted)
#     if project_deleted == None:
#         return {"status": "error", "details": f"not found project to deleted with id {id} in the collection"}
#     else:
#         return {"status": "success", "detail": "Project deleted"}


@router.delete("/project/{project_id}")
def delete_project(project_id: str):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid id: {project_id}")
    project = Project.find_one_and_delete({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No post with this id: {project_id} found')
    return {"message": "project elimated"}


router.mount("/static", StaticFiles(directory="static"), name="static")


@router.post("/upload-image/{id}")
async def upload_image(id: str, image: Union[UploadFile, None] = File(...)):
    if not image.filename:
        return {"message": "No upload file sent"}
    else:
        collection_name = Project
        FILEPATH = "./static/images/"
        filename = image.filename
        extension = filename.split('.')[1]

        if extension not in ["png", "jpg"]:
            return {"status": "error", "detail": "File extension not allowed"}

        # uasdi122.jpg
        token_name = secrets.token_hex(10)+"."+extension
        generated_name = FILEPATH + token_name
        file_content = await image.read()

        with open(generated_name, "wb") as image:
            image.write(file_content)

        # PILLOW
        img = Image.open(generated_name)
        # img = img.resize(size=(300, 300))
        img.save(generated_name)

        update_object = collection_name.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": {"image": token_name}}, return_document=ReturnDocument.AFTER)

        image.close()
        file_url = "localhost:8000" + generated_name[1:]
        update_object["_id"] = str(update_object['_id'])
        return {"status": file_url, "data_updated":  update_object}


# @router.post("/upload-image/{id}")
# async def upload_image(id: str, image: Union[UploadFile, None] = File(...)):

#     if not image.filename:
#         return {"message": "No upload file sent"}
#     else:
#         collection_name = Project
#         FILEPATH = "./static/images/"
#         filename = image.filename
#         extension = filename.split('.')[1]

#         if extension not in ["png", "jpg"]:
#             return {"status": "error", "detail": "File extension not allowed"}

#         # uasdi122.jpg
#         token_name = secrets.token_hex(10)+"."+extension
#         generated_name = FILEPATH + token_name
#         file_content = await image.read()

#         with open(generated_name, "wb") as image:
#             image.write(file_content)

#         # PILLOW
#         img = Image.open(generated_name)
#         # img = img.resize(size=(300, 300))
#         img.save(generated_name)

#         update_object = collection_name.find_one_and_update(
#             {"_id": ObjectId(id)}, {"$set": {"image": token_name}})

#         image.close()
#         file_url = "localhost:8000" + generated_name[1:]
#         update_object["_id"] = str(update_object['_id'])
#         return {"status": file_url, "data_updated":  update_object}


@router.get("/get-image/{file_name}")
def getFileImage(file_name: str):

    path_file = "./static/images/" + file_name
    if file_name in [file for file in os.listdir("./static/images/")]:
        return FileResponse(path=path_file)
    else:
        return {"status": "error", "details": "not found image"}
