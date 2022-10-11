from typing import Optional, Union

import requests
import sqlalchemy.orm as orm
from decouple import config
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from bigfastapi.core import messages
from bigfastapi.db.database import SessionLocal
from bigfastapi.models.organization_models import Organization, OrganizationUser


class Helpers:
    async def is_organization_member(
        user_id: str, organization_id: str, db: Optional[orm.Session]
    ):

        if db is None:
            db = SessionLocal()

        organization = (
            db.query(Organization)
            .filter_by(user_id=user_id)
            .filter(Organization.id == organization_id)
            .first()
        )

        org_user = (
            db.query(OrganizationUser)
            .filter_by(organization_id=organization_id)
            .filter_by(user_id=user_id)
            .first()
        )
        if org_user is None and organization is None:
            return False
        return True

    async def check_user_org_validity(
        user_id: str,
        organization_id: str,
        db: Optional[orm.Session],  # type-hinting preventing use as dependency
    ) -> bool:
        """
        This method can be called at the top of a request-response controller
        to check if the user making a request is a member of the organization
        data is to be retrieved from.

        """

        if db is None:
            db = SessionLocal()
        organization = (
            db.query(Organization).filter(Organization.id == organization_id).first()
        )

        if organization is None:
            raise HTTPException(status_code=404, detail="Organization does not exist")

        is_valid_member = await Helpers.is_organization_member(
            user_id=user_id, organization_id=organization_id, db=db
        )

        if is_valid_member is False:
            raise HTTPException(
                status_code=403,
                detail=messages.NOT_ORGANIZATION_MEMBER,
            )

        return is_valid_member

    async def get_org_currency(organization_id: str, db: orm.Session):
        organisation = (
            db.query(Organization).filter(Organization.id == organization_id).first()
        )
        return organisation.currency_code

    def valid_organization_id(
        organization_id: str, db
    ) -> Union[Organization, JSONResponse]:
        if db is None:
            db = SessionLocal()

        organization = (
            db.query(Organization).filter(Organization.id == organization_id).first()
        )

        if not organization:
            return JSONResponse(
                {"message": "Organization does not exist"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return organization

    # Sends a notification to slack.
    # NOTE: DO NOT CALL THIS METHOD IN THE SAME THREAD AS YOUR REQUEST. USE A BACKGROUND TASK
    @staticmethod
    def slack_notification(url: str, text: str, verify: bool = True):
        requests.post(
            url=config(url),
            json={"text": text},
            headers={"Content-Type": "application/json"},
            verify=verify,
        )
