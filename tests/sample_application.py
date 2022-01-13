from fastapi import FastAPI
from bigfastapi import database as _db
from bigfastapi import organization
from bigfastapi import cs_token

print(cs_token)


app = FastAPI(
    # dependencies=[Depends(_db.get_db)]
    )


app.include_router(organization.app)
# app.include_router(cs_accounts)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}