import requests
import sqlalchemy.orm as _orm
from decouple import config

from bigfastapi.models import organisation_user_model
from bigfastapi.models.organisation_models import Organization


class Helpers:
    async def is_organization_member(user_id: str, organization_id: str, db: _orm.Session):
        organization = (
            db.query(Organization)
                .filter_by(creator=user_id)
                .filter(Organization.id == organization_id)
                .first()
        )

        store_user = db.query(organisation_user_model.OrganisationUser).filter_by(store_id=organization_id).filter_by(
            user_id=user_id).first()
        if store_user == None and organization == None:
            return False
        return True

    # Sends a notification to slack.
    # NOTE: DO NOT CALL THIS METHOD IN THE SAME THREAD AS YOUR REQUEST. USE A BACKGROUND TASK
    @staticmethod
    def slack_notification(url:str, text: str, verify: bool = True):
        requests.post(url=config(url), json={"text": text}, headers={"Content-Type": "application/json"},
                    verify=verify)
