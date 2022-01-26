import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi.schemas import notification_schemas, users_schemas
from bigfastapi.models import notification_models
from bigfastapi.models import organisation_models
from bigfastapi.models import wallet_models
from bigfastapi import wallet
import bigfastapi.db.database as database
import fastapi as _fastapi
from bigfastapi.notification import is_authenticated
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
test_db = TestingSessionLocal()


#####################################################################
# THE TEST CASES ARE NOT COMPLETE YET. HAVE SOME ISSUES WITH PYTHON.#
# WILL COMPLETE AFTER DOING SOME RESEARCH                           #
#####################################################################
async def override_is_authenticated():
    user_data = {
        "id": "9cd87677378946d88dc7903b6710ae55",
        "first_name": "John",
        "last_name": "Doe",
        "email": "test@gmail.com",
        "password": "hashedpassword",
        "is_active": True,
        "is_verified": True,
        "is_superuser": True,
        "phone_number": "123456789000",
        "organization": "test"
    }
    return users_schemas.User(**user_data)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(scope="module")
def setUp():
    database.Base.metadata.create_all(bind=engine, tables=[wallet_models.Wallet.__table__,
                                                           organisation_models.Organization.__table__])
    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[is_authenticated] = override_is_authenticated

    organization = organisation_models.Organization(
        id="9cd87677378946d88dc7903b6710ae79",
        mission="test mission",
        vision="test mission",
        name="test name 2",
        values="test values"
    )

    test_db.add(organization)
    test_db.commit()
    test_db.refresh(organization)

    return organization

    # database.Base.metadata.drop_all(bind=engine, tables=[notification_models.Notification.__tablename__])


def test_get_wallet(setUp):
    response = client.post("/wallets/9cd87677378946d88dc7903b6710ae77")
    assert response.status_code == 200
    assert response.json().get('balance') == 0
    assert response.json().get('organization_id') == '9cd87677378946d88dc7903b6710ae77'


def test_debit_wallet(setUp):
    response = client.post("/wallets/9cd87677378946d88dc7903b6710ae77")
    assert response.status_code == 200
    assertRaises(_fastapi.HTTPException, wallet.debit_wallet(wallet_id=response.json().get('id'), amount=1500))