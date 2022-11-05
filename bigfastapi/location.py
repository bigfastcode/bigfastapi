import asyncio

import sqlalchemy.orm as orm
from fastapi import APIRouter, Depends

from bigfastapi.core.helpers import Helpers
from bigfastapi.db.database import get_db
from bigfastapi.models.location_models import Location
from bigfastapi.schemas import users_schemas
from bigfastapi.services.auth_service import is_authenticated
from bigfastapi.utils import paginator

app = APIRouter(tags=["Locations"])


@app.get("/locations", status_code=200)
def get_all_locations(
    organization_id: str,
    page: int = 1,
    size: int = 50,
    search_value: str = "",
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db),
):
    # check if user is a member of this organization
    asyncio.run(
        Helpers.check_user_org_validity(
            user_id=user.id, organization_id=organization_id, db=db
        )
    )

    page_size = 50 if size < 1 or size > 100 else size
    page_number = 1 if page <= 0 else page

    locations_query = db.query(Location)

    if search_value:
        locations_query = locations_query.filter(
            Location.state.like(f"%{search_value}%")
        )

    db.execute("SET sql_mode = (SELECT REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY', ''))")

    locations = (
        locations_query.distinct(Location.state)
        .group_by(Location.state)
        .limit(limit=size)
        .all()
    )
    total_items = locations_query.count()

    pointers = asyncio.run(
        paginator.page_urls(
            page=page, size=page_size, count=total_items, endpoint="/locations"
        )
    )

    response = {
        "page": page_number,
        "size": page_size,
        "total": total_items,
        "previous_page": pointers["previous"],
        "next_page": pointers["next"],
        "items": locations,
    }

    return {"data": response}
