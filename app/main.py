# main.py 
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, user, projects
from app.config import settings
from app import email2
app = FastAPI()

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')
app.include_router(user.router, tags=['Users'], prefix='/api/user')
app.include_router(projects.router, tags=['Projects'], prefix='/api')
app.include_router(email2.router, tags=['Email'], prefix='/api/send')
# app.include_router(routers.router, tags=['Users'], prefix='/api/routers')

@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with MongoDB"}

# if __name__ == "__main__":
#     uvicorn.run(app='app.main:app', host="0.0.0.0", port=8000, reload=True)


# uvicorn –  a high-performance ASGI web server
# main:app: the app/main.py file
# app: the object returned after evoking FASTAPI()
# --host : allows us to bind the socket to a host. Defaults to 127.0.0.1
# --port : allows us to bind the socket to a specific port. 8000 is the default.
# --reload: Enables hot-reloading