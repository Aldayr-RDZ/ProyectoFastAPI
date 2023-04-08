from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Union
from bson.objectid import ObjectId
from fastapi import File, UploadFile
# class AuthDetails(BaseModel):
#     username: str
#     password: str


class UserBaseSchema(BaseModel):
    name: str
    email: str
    photo: Union[str, None] = None
    role: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None

    class Config:
        orm_mode = True


class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    passwordConfirm: str
    verified: bool = False


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserResponseSchema(UserBaseSchema):
    id: str
    pass


class UserResponse(BaseModel):
    status: str
    user: UserResponseSchema


class ProjectBaseSchema(BaseModel):
    name: str
    description: str
    year: int
    category: str
    langs: str
    image: Union[str, None] = None
    created_at: Union[datetime, None] = None
    update_at: Union[datetime, None] = None

    class Config:
            orm_mode = True
            allow_population_by_field_name = True
            arbitrary_types_allowed = True
            json_encoders = {ObjectId: str}

class CreateProjectSchema(ProjectBaseSchema):
    user: Union[ObjectId, None] = None
    pass


class UpdateProjectSchema(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    year: Union[int, None] = None
    category: Union[str, None] = None
    langs: Union[str, None] = None
    image: Union[str, None] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}





# class ProjectBaseSchema(BaseModel):


#     class Config:
#         orm_mode = True

# class ProjectResponsesSchema(BaseModel):
#     id: str
#     pass


# class ProjectResponse(BaseModel):
#     status: str
#     project: ProjectBaseSchema
