"""
A collection of filter endpoints to filter data in
an organization based on a string query
"""

import sqlalchemy.orm as orm
from fastapi import APIRouter, Depends

from bigfastapi.db.database import get_db

app = APIRouter(tags=["Receipts"])


@app.post("/filters", status_code=201)
def create_filter(
    organization_id: str,
    table_name: str,
    filter_query: str,
    db: orm.Session = Depends(get_db),
):
    """
    Create a filter for an organization data.
    e.g A filter for `receipts`.

    Parameters
    ----------
    organization_id: The id of the organization
    table_name: The name of the table

    Raises
    ------
    UnauthorizedException

    BadRequestException

    """


@app.post("/filters", status_code=201)
def get_table_filters(
    organization_id: str, table: str, db: orm.Session = Depends(get_db)
):
    """
    Retrieve all filters for a table.
    e.g A filter for `receipts`.

    Parameters
    ----------


    Raises
    ------
    UnauthorizedException

    BadRequestException

    """
