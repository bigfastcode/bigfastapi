from fastapi import FastAPI

from . import accounts as _accounts, blog as _blog, organization as _organization

app = FastAPI()

app.include_router(_accounts.app)
app.include_router(_blog.app)
app.include_router(_organization.app)