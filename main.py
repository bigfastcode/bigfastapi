import uvicorn
from fastapi import FastAPI
from bigfastapi.database import create_database
from bigfastapi.accounts import app as accounts_router
from bigfastapi.organization import app as organization_router
from bigfastapi.countries import app as countries
<<<<<<< HEAD
from bigfastapi.blog import app as blog
=======
from bigfastapi.comments import app as comments
>>>>>>> 3d47805363a4e333b538e07ba4841954725cf234
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

create_database()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers=["*"]
)

# routers
app.include_router(accounts_router, tags=["Auth"])
app.include_router(organization_router, tags=["Organization"])
app.include_router(countries, tags=["Countries"])
<<<<<<< HEAD
app.include_router(blog, tags=["Blog"])

=======
app.include_router(comments, tags=["Comments"])
>>>>>>> 3d47805363a4e333b538e07ba4841954725cf234

@app.get("/", tags=["Home"])
async def get_root() -> dict:
    return {
        "message": "Welcome to BigFastAPI. This is an example of an API built using BigFastAPI. Please visit here to view the docs:",
        "url": "http://127.0.0.1:7001/docs"
    }

if __name__ == "__main__":
     uvicorn.run("main:app", port=7001, reload=True)
     