import requests
import sqlalchemy.orm as _orm
from decouple import config

from bigfastapi.models.organization_models import Organization, OrganizationUser


class Helpers:
    async def is_organization_member(user_id: str, organization_id: str, db: _orm.Session):
        organization = (
            db.query(Organization)
                .filter_by(user_id=user_id)
                .filter(Organization.id == organization_id)
                .first()
        )

        store_user = db.query(OrganizationUser).filter_by(organization_id=organization_id).filter_by(
            user_id=user_id).first()
        if store_user == None and organization == None:
            return False
        return True

    async def get_org_currency(organization_id: str, db: _orm.Session):
        organisation = db.query(Organization).filter(Organization.id == organization_id).first()
        return organisation.currency_code

    # Sends a notification to slack.
    # NOTE: DO NOT CALL THIS METHOD IN THE SAME THREAD AS YOUR REQUEST. USE A BACKGROUND TASK
    @staticmethod   
    def slack_notification(url: str, text: str, verify: bool = True):
        requests.post(url=config(url), json={"text": text}, headers={"Content-Type": "application/json"},
                    verify=verify)
