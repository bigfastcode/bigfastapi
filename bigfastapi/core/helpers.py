import sqlalchemy.orm as _orm
from bigfastapi.models import store_user_model

from  bigfastapi.models.organisation_models import Organization

class Helpers:
    async def is_organization_member(user_id: str, organization_id: str, db: _orm.Session):
        organization = (
            db.query(Organization)
                .filter_by(creator=user_id)
                .filter(Organization.id == organization_id)
                .first()
        )

        store_user = db.query(store_user_model.StoreUser).filter_by(store_id=organization_id).filter_by(
            user_id=user_id).first()
        if store_user == None and organization == None:
            return False
        return True
