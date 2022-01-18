import uvicorn
from fastapi import FastAPI
from bigfastapi.database import create_database
from bigfastapi.accounts import app as accounts_router
from bigfastapi.organization import app as organization_router
from bigfastapi.countries import app as countries
from bigfastapi.blog import app as blog
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
app.include_router(blog, tags=["Blog"])


@app.get("/", tags=["Home"])
async def get_root() -> dict:
    return {
        "message": "Welcome to BigFastAPI."
    }

if __name__ == "__main__":
     uvicorn.run("main:app", port=7001, reload=True)
     