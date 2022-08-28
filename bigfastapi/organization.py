import os
from typing import Optional
from uuid import uuid4

import sqlalchemy.orm as orm
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import and_
from sqlalchemy.sql import expression

from bigfastapi.auth_api import is_authenticated
from bigfastapi.core.helpers import Helpers
from bigfastapi.db.database import get_db
from bigfastapi.files import upload_image
from bigfastapi.models import organization_models, user_models
from bigfastapi.models.extra_info_models import ExtraInfo
from bigfastapi.models.organization_models import (
    OrganizationInvite,
    OrganizationUser,
    Role,
)
from bigfastapi.schemas import organization_schemas, users_schemas
from bigfastapi.schemas.organization_schemas import (
    AddRole,
    OrganizationBase,
    OrganizationUserBase,
)
from bigfastapi.services import email_services, organization_services
from bigfastapi.utils import paginator
from bigfastapi.utils.image_utils import gen_thumbnail, save_thumbnail_info
from bigfastapi.utils.utils import paginate_data

# from bigfastapi.services import email_services
from .models import organization_models as _models

app = APIRouter(tags=["Organization"])


@app.post("/organizations")
def create_organization(
    organization: organization_schemas.OrganizationCreate,
    background_tasks: BackgroundTasks,
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db),
):
    """intro--> This endpoint allows you to create a new organization. To use this endpoint you need to make a post request to the `/organizations` endpoint with the specified body of request.

    reqBody-->mission: This is the mission f the organization
    reqBody-->vision: This is the vision of the organization
    reqBody-->name: This is the name of the organization
    reqBody-->country: This is the organization's country of operation
    reqBody-->state: This is the organization's state of operation
    reqBody-->address: This is a descriptive address of where the organization is located
    reqBody-->currency_code: This is the currency of preference of the organization
    reqBody-->phone_number: This is the phone contact detail of the organization
    reqBody-->email This is the email contact address of the organization
    reqBody-->current_subscription: This is the current subscription plan of the organization
    reqBody-->tagline: This is a tagline to identify the organization with
    reqBody-->image: This is a link to cover image for the organization
    reqBody-->values: This describes the values of the organization
    reqBody-->business_type: This is the type of business the organization runs
    reqBody-->image_full_path: This is full url path to the company's cover image


    returnDesc--> On sucessful request, it returns
        returnBody--> details of the newly created organization
    """
    try:

        db_org = organization_services.get_organization_by_name(
            name=organization.name, creator_id=user.id, db=db
        )

        if db_org:
            raise HTTPException(
                status_code=400,
                detail=f"{organization.name} already exist in your business collection",
            )

        created_org = organization_services.create_organization(
            user=user, db=db, organization=organization
        )

        if organization.wallet is True:
            organization_services.run_wallet_creation(created_org, db)

        background_tasks.add_task(
            organization_services.send_slack_notification, user.email, organization
        )

        return JSONResponse(
            {
                "message": "Organization created successfully",
                "data": jsonable_encoder(created_org),
            },
            status_code=201,
        )

    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.get("/organizations")
def get_organizations(
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db),
    page_size: int = 15,
    page_number: int = 1,
):
    """intro--> This endpoint allows you to retrieve all organizations. To use this endpoint you need to make a get request to the /organizations endpoint

            paramDesc--> On get request, the request url takes two(2) optional query parameters
                param--> page_size: This is the size per page, this is 10 by default
                param--> page_number: This is the page of interest, this is 1 by default

    returnDesc--> On sucessful request, it returns:

        returnBody--> a list of organizations
    """
    all_orgs = organization_services.get_organizations(user, db)

    return paginate_data(all_orgs, page_size, page_number)


@app.get("/organizations/{organization_id}", status_code=200)
async def get_organization(
    organization_id: str,
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db),
):
    """intro--> This endpoint allows you to retrieve details of a particular organizations.
    To use this endpoint you need to make a get request to the /organizations/{organization_id} endpoint

            paramDesc--> On get request, the request url takes the parameter, organization id
                param--> organization_id: This is unique Id of the organization of interest

    returnDesc--> On sucessful request, it returns:

        returnBody--> details of the queried organization
    """

    # is_org_member = Helpers.is_organization_member(user.id, organization_id, db)
    # return is_org_member

    # if is_org_member is True:
    organization = await organization_services.get_organization(
        organization_id, user, db
    )
    # menu = get_organization_menu(organization_id, db)
    return {"data": {"organization": organization}}  # , "menu":MENU

    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND
    #     )


@app.get(
    "/organizations/{organization_id}/users",
    status_code=200,
    response_model=organization_schemas.OrganizationUsersResponse,
)
async def get_organization_users(
    organization_id: str,
    search_value: str = None,
    sorting_key: str = None,
    page: int = 1,
    size: int = 50,
    db: orm.Session = Depends(get_db),
    user: users_schemas.User = Depends(is_authenticated),
):
    """intro--> This endpoint allows you to get all users in an organization. To use this endpoint you need to make a get request to the `/organizations/{organization_id}/users` endpoint.
    The `organization_id` parameter is used to query the users(invited users included) in an organization.

        paramDesc--> On get request, the request url takes the parameter, organization id
            param--> organization_id: This is unique Id of the organization of interest

    returnDesc--> On sucessful request, it returns:

        returnBody--> list of all users in the queried organization
    """
    try:

        Helpers.check_user_org_validity(
            user_id=user.id, organization_id=organization_id, db=db
        )

        organization = (
            db.query(_models.Organization)
            .filter(_models.Organization.id == organization_id)
            .first()
        )

        organization_owner_id = organization.user_id

        organization_owner = (
            db.query(user_models.User)
            .filter(user_models.User.id == organization_owner_id)
            .first()
        )

        # invited_list = (
        #     db.query(OrganizationUser)
        #     .filter(
        #         and_(
        #             OrganizationUser.organization_id == organization_id,
        #             OrganizationUser.is_deleted == False,
        #         )
        #     )
        #     .all()
        # )

        page_size = 50 if size < 1 or size > 100 else size
        page_number = 1 if page <= 0 else page
        offset = await paginator.off_set(page=page_number, size=page_size)

        # All the users in the organization with their roles
        query = (
            db.query(OrganizationUser)
            .join(user_models.User)
            .join(Role)
            .with_entities(
                user_models.User.id,
                user_models.User.first_name,
                user_models.User.last_name,
                user_models.User.email,
                Role.role_name,
            )
            .filter(
                and_(
                    OrganizationUser.user_id == user_models.User.id,
                    OrganizationUser.role_id == Role.id,
                    OrganizationUser.organization_id == organization_id,
                    OrganizationUser.is_deleted == expression.false(),
                )
            )
            .order_by(OrganizationUser.date_created.desc())
            .offset(offset=offset)
            .limit(limit=size)
        )

        invited_list = query.all()
        total_items = query.count()

        # invited_list = list(map(lambda x: row_to_dict(x), invited_list))

        # invited_users = []

        # if len(invited_list) > 0:
        #     for invited in invited_list:
        #         user = (
        #             db.query(user_models.User)
        #             .filter(
        #                 and_(
        #                     user_models.User.id == invited["user_id"],
        #                     user_models.User.is_deleted == False,
        #                 )
        #             )
        #             .first()
        #         )
        #         role = db.query(Role).filter(Role.id == invited["role_id"]).first()
        #         if user.id == invited["user_id"]:
        #             invited["first_name"] = user.first_name
        #             invited["last_name"] = user.last_name
        #             invited["email"] = user.email
        #             invited["role"] = role.role_name

        #         invited_users.append(invited)

        pointers = await paginator.page_urls(
            page=page, size=page_size, count=total_items, endpoint="/users"
        )

        response = {
            "page": page_number,
            "size": page_size,
            "total": total_items,
            "previous_page": pointers["previous"],
            "next_page": pointers["next"],
            "items": [{"owner": organization_owner, "invited_users": invited_list}],
        }

        # users = {"organization_owner": organization_owner, "users": jsonable_encoder(invited_users)}

        return JSONResponse({"data": jsonable_encoder(response)}, status_code=200)

    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.delete("/organizations/{organization_id}/users/{user_id}")
def delete_organization_user(
    organization_id: str, user_id: str, db: orm.Session = Depends(get_db)
):
    """intro--> This endpoint allows you to delete a particular user from an organization. To use this endpoint you need to make a delete request to the /organizations/{organization_id}/users/{user_id} endpoint

        paramDesc--> On delete request, the request url takes two(2) parameters, organization id and user id
            param--> organization_id: This is unique Id of the organization of interest
            param--> user_id: This is the unique id of the user to be removed from the organization

    returnDesc--> On sucessful request, it returns message,
        returnBody--> User with email {email} successfully removed from the organization
    """
    try:

        # fetch the organization user from the user table
        user = db.query(user_models.User).filter(user_models.User.id == user_id).first()

        if user is not None:
            organization_user = (
                db.query(OrganizationUser)
                .filter(
                    and_(
                        OrganizationUser.user_id == user_id,
                        OrganizationUser.organization_id == organization_id,
                    )
                )
                .first()
            )

            organization_user.is_deleted = True
            user.is_deleted = True
            db.add(organization_user)
            db.commit()
            db.refresh(organization_user)
            db.add(user)
            db.commit()
            db.refresh(user)

            return {
                "message": f"User with email {user.email} successfully removed from the organization"
            }

        return {"message": "User does not exist"}

    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.get("/organizations/{organization_id}/roles")
def get_roles(
    organization_id: str,
    db: orm.Session = Depends(get_db),
):
    """intro--> This endpoint allows you to retrieve all available roles in an organization. To use this endpoint you need to make a get request to the /organizations/{organization_id}/roles endpoint

        paramDesc--> On get request, the request url takes the parameter, organization id.
            param-->organization_id: This is the unique id of the organization of interest.

    returnDesc--> On sucessful request, it returns:

        returnBody--> list of all available roles in the queried organization
    """
    roles = db.query(Role).filter(Role.organization_id == organization_id)
    roles = list(map(organization_schemas.Role.from_orm, roles))

    return roles


@app.post("/organizations/{organization_id}/roles")
def add_role(
    payload: AddRole,
    organization_id: str,
    db: orm.Session = Depends(get_db),
):
    """intro--> This endpoint allows you to create roles in an organization. To use this endpoint you need to make a post request to the /organizations/{organization_id}/roles endpoint with a specified body of request

        paramDesc--> On get request, the request url takes the parameter, organization id
            param--> organization_id: This is the unique Id of the organization of interest

            reqBody--> organization_id: This is a unique Id of the organization of interest
            reqBody--> role_name: This is the name of the new role to be created in the organization

    returnDesc--> On sucessful request, it returns:
        returnBody--> details of the newly created organization role.
    """
    try:

        roles = db.query(Role).filter(Role.organization_id == organization_id).all()
        if len(roles) < 1:
            existing_role = (
                db.query(Role)
                .filter(Role.role_name == payload.role_name.lower())
                .first()
            )
            if existing_role is None:
                role = Role(
                    id=uuid4().hex,
                    organization_id=organization_id.strip(),
                    role_name=payload.role_name.lower(),
                )

                db.add(role)
                db.commit()
                db.refresh(role)

                return role
            return {"message": "role already exist"}
        return
    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.put(
    "/organizations/accept-invite/{invite_code}",
    response_model=organization_schemas.AcceptInviteResponse,
)
def accept_invite(
    payload: organization_schemas.OrganizationUser,
    invite_code: str,
    db: orm.Session = Depends(get_db),
):
    """intro-->This endpoint allows for a user to accept an invite. To use this endpoint you need to make a put request to the /users/accept-invite/{token} where token is a unique value recieved by the user on invite. It also takes a specified body of request

    paramDesc-->On put request this enpoint takes the query parameter "token"
        param-->token: This is a unique token recieved by the user on invite
        reqBody-->user_email: This is the email address of the user
        reqBody-->user_id: This is the unique user id
        reqBody-->user_role: This specifies the role of the user in the organization
        reqBody-->is_accepted: This is the the acceptance state of the invite
        reqBody-->is_revoked: This is the revoke state of the user
        reqBody-->is_deleted: This specifies if the invite is deleted/expired
        reqBody-->organization_id: This is a unique id of the registered organization

    returnDesc--> On sucessful request, it returns:

        returnBody--> An object with a key `invited` containing the new organization user data, and `organization` containing information about the organization
         the user is invited to.
    """
    try:

        existing_invite = (
            db.query(OrganizationInvite)
            .filter(
                and_(
                    OrganizationInvite.invite_code == invite_code,
                    OrganizationInvite.is_deleted == False,
                    OrganizationInvite.is_revoked == False,
                )
            )
            .first()
        )

        if existing_invite is None:
            return JSONResponse(
                {
                    "message": "Invite not found. If you think this is shouldn't be, try again or ask the inviter to invite you again."
                },
                status_code=404,
            )

        organization = (
            db.query(organization_models.Organization)
            .filter(
                organization_models.Organization.id == existing_invite.organization_id
            )
            .first()
        )

        organization_user = OrganizationUser(
            id=uuid4().hex,
            organization_id=existing_invite.organization_id,
            user_id=payload.user_id,
            role_id=existing_invite.role_id,
        )
        db.add(organization_user)
        db.commit()
        db.refresh(organization_user)

        existing_invite.is_deleted = True
        existing_invite.is_accepted = True
        db.commit()
        db.refresh(existing_invite)

        return {
            "invited": OrganizationUserBase.from_orm(organization_user),
            "organization": OrganizationBase.from_orm(organization),
        }

    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.post(
    "/organizations/{organization_id}/invite-user",
    status_code=201,
    response_model=organization_schemas.InviteResponse,
)
async def invite_user(
    payload: organization_schemas.UserInvite,
    organization_id: str,
    background_tasks: BackgroundTasks,
    template: Optional[str] = "invite_email.html",
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db),
):
    """intro--> This endpoint is used to trigger a user invite. To use this endpoint you need to make a post request to the /users/invite/ endpoint with the specified body of request

        reqBody--> user_email: This is the email address of the user to be invited.
        reqBody--> user_id: This is the unique user id of the logged in user
        reqBody--> user_role: This specifies the role of the user to be invited in the organization
        reqBody--> organization: This specifies the information of the registered organization
        reqBody--> app_url: This is the url to be navigated to on invite accept, usually the url of the application.
        reqBody--> email_details: This is the key content of the invite email to be sent.

    'returnDesc'--> On sucessful request, it returns:

        returnBody-->  An object with a key `message`.
    """
    try:
        await Helpers.check_user_org_validity(
            user_id=user.id, organization_id=organization_id, db=db
        )

        invite_token = uuid4().hex
        invite_url = f"{payload.app_url}/accept-invite?invite_token={invite_token}"
        payload.email_details.link = invite_url
        email_info = payload.email_details
        email_info.organization_id = organization_id

        role = db.query(Role).filter(Role.role_name == payload.role.lower()).first()

        # make sure you can't send invite to yourself
        if user.email == payload.email:
            return JSONResponse(
                {"message": "You cannot send an invite to yourself"}, status_code=403
            )

        existing_invite = (
            db.query(OrganizationInvite)
            .filter(
                and_(
                    OrganizationInvite.email == payload.email,
                    OrganizationInvite.is_deleted == False,
                )
            )
            .first()
        )
        if existing_invite is not None:
            return JSONResponse({"message": "Invite already sent"}, status_code=409)

        await email_services.send_email(
            template_body=email_info,
            background_tasks=background_tasks,
            recipients=[payload.email],
            template=template,
            db=db,
        )

        invite = OrganizationInvite(
            id=uuid4().hex,
            organization_id=payload.organization.get("id"),
            user_id=payload.user_id,
            email=payload.email,
            role_id=role.id,
            invite_code=invite_token,
        )

        db.add(invite)
        db.commit()
        db.refresh(invite)

        return JSONResponse(
            {
                "data": jsonable_encoder(invite),
                "message": "Invite email will be sent in the background.",
            },
            status_code=201,
        )

    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.get(
    "/organizations/get-invite/{invite_code}",
    response_model=organization_schemas.SingleInviteResponse,
)
async def get_single_invite(
    invite_code: str,
    db: orm.Session = Depends(get_db),
):
    """intro--> This endpoint is used to get an invite link for a single user. To use this endpoint you need to make a get request to the /users/invite/{invite_code} endpoint

    paramDesc--> On get request, the url takes an invite code
        param--> invite_code: This is a unique code needed to get an invite link


    returnDesc--> On sucessful request, it returns
        returnBody--> An object with a key `invite` containing the invite data and a key `user` containing an empty string `''`
        indicating the user is not a member of another organization in the application or `exists` indicating that the invited user is a member of another organization in the application.
    """
    try:

        # user invite code to query the invite table
        existing_invite = (
            db.query(OrganizationInvite)
            .filter(
                and_(
                    OrganizationInvite.invite_code == invite_code,
                    OrganizationInvite.is_deleted == False,
                    OrganizationInvite.is_revoked == False,
                )
            )
            .first()
        )
        if existing_invite:
            existing_user = (
                db.query(user_models.User)
                .filter(user_models.User.email == existing_invite.user_email)
                .first()
            )

            organization = (
                db.query(organization_models.Organization)
                .filter(
                    organization_models.Organization.id
                    == existing_invite.organization_id
                )
                .first()
            )

            setattr(existing_invite, "organization", organization)
            user_exists = ""
            if existing_user is not None:
                user_exists = "exists"
            if not existing_invite:
                return JSONResponse(
                    {
                        "message": "Invite not found! Try again or ask the inviter to invite you again."
                    },
                    status_code=404,
                )

            return {"invite": existing_invite, "user": user_exists}
        return JSONResponse({"message": "Invalid invite code"}, status_code=404)

    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.put(
    "/organizations/decline-invite/{invite_code}",
    response_model=organization_schemas.DeclinedInviteResponse,
)
def decline_invite(invite_code: str, db: orm.Session = Depends(get_db)):
    """intro--> This endpoint is used to decline an invite. To use this endpoint you need to make a put request to the /users/invite/{invite_code}/decline endpoint

    paramDesc--> On put request, the url takes an invite code
        param-->invite_code: This is a unique code linked to invite


    returnDesc--> On sucessful request, it returns message:

        returnBody--> an object contain the invite data with the `is_deleted` field set to True
    """
    try:

        declined_invite = (
            db.query(OrganizationInvite)
            .filter(OrganizationInvite.invite_code == invite_code)
            .first()
        )

        declined_invite.is_deleted = True
        db.add(declined_invite)
        db.commit()
        db.refresh(declined_invite)

        return declined_invite

    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.delete(
    "/organizations/{organization_id}/revoke-invite/{invite_code}",
    response_model=organization_schemas.RevokedInviteResponse,
)
def revoke_invite(
    organization_id: str,
    invite_code: str,
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db),
):
    """intro-->This endpoint is used to revoke the invitation of a previously invited user. To use this endpoint you need to make a delete request to the /users/revoke-invite/{invite_code} endpoint

    paramDesc-->On delete request, the url takes an invite code
        param-->invite_code: This is a unique code linked to invite


    returnDesc--> On successful request, it returns message,
        returnBody--> an object contain the invite data with the `is_deleted` and `is_revoked` field set to True
    """
    try:

        revoked_invite = (
            db.query(OrganizationInvite)
            .filter(
                and_(
                    OrganizationInvite.organization_id == organization_id,
                    OrganizationInvite.invite_code == invite_code,
                )
            )
            .first()
        )

        revoked_invite.is_revoked = True
        revoked_invite.is_deleted = True
        db.add(revoked_invite)
        db.commit()
        db.refresh(revoked_invite)

        return revoked_invite

    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.get(
    "/organizations/{organization_id}/invites",
    status_code=200,
    response_model=organization_schemas.AllInvites,
)
async def get_pending_invites(
    organization_id: str,
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db),
):
    """intro--> This endpoint allows you to retrieve all pending invites to an organization. To use this endpoint you need to make a get request to the /organizations/invites/{organization_id} endpoint

        paramDesc--> On get request, the request url takes the parameter, organization id
            param--> organization_id: This is the unique Id of the organization of interest


    returnDesc--> On sucessful request, it returns:

        returnBody--> all pending invites in the queried organization
    """
    try:
        await Helpers.check_user_org_validity(
            user_id=user.id, organization_id=organization_id, db=db
        )

        pending_invites = (
            db.query(OrganizationInvite)
            .filter(
                and_(
                    OrganizationInvite.organization_id == organization_id,
                    OrganizationInvite.is_deleted == False,
                    OrganizationInvite.is_accepted == False,
                    OrganizationInvite.is_revoked == False,
                )
            )
            .all()
        )

        return JSONResponse(
            {"data": jsonable_encoder(pending_invites)}, status_code=200
        )

    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.put("/organizations/{organization_id}")
async def update_organization(
    organization_id: str,
    organization: organization_schemas.OrganizationUpdate,
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db),
):
    """intro--> This endpoint allows you to update the details of a particular organization organization. To use this endpoint you need to make a put request to the /organizations/{organization_id} endpoint with a specified body of request

        paramDesc--> On put request, the request url takes the parameter, organization id
            param--> organization_id: This is the unique Id of the organization of interest

            reqBody--> mission: This is the mission f the organization
            reqBody--> vision: This is the vision of the organization
            reqBody--> name: This is the name of the organization
            reqBody--> country: This is the organization's country of operation
            reqBody--> state: This is the organization's state of operation
            reqBody--> address: This is a descriptive address of where the organization is located
            reqBody--> currency_preference: This is the currency of preference of the organization
            reqBody--> phone_number: This is the phone contact detail of the organization
            reqBody--> email This is the email contact address of the organization
            reqBody--> current_subscription: This is the current subscription plan of the organization
            reqBody--> tagline: This is a tagline to identify the organization with
            reqBody--> image: This is a link to cover image for the organization
            reqBody--> values: This describes the values of the organization
            reqBody--> business_type: This is the type of business the organization runs
            reqBody--> credit_balance: This is a value representing the organization's credit balance
            reqBody--> image_full_path: This is full url path to the company's cover image
            reqBody--> add_template: This is a boolean value that determines wether to add already available templates for the organization.

    returnDesc--> On successful request, it returns:

        returnBody--> details of the updated organization
    """
    return await organization_services.update_organization(
        organization_id, organization, user, db
    )


@app.patch("/organizations/{organization_id}/update-image")
async def change_organization_image(
    organization_id: str,
    file: UploadFile = File(...),
    db: orm.Session = Depends(get_db),
    user: str = Depends(is_authenticated),
):
    """intro--> This endpoint allows you to upload/change the cover image of an organization.
        To use this endpoint you need to make a get patch request to the
        endpoint, /organizations/{organization_id}/update-image.

        requestHeader-->Authorization: Bearer token
        requestBody-->organization_id: The organization unique id as string
        requestBody-->file: The image file to be uploaded

    returnDesc--> On sucessful request, it returns:
        returnBody--> Updated organization object
    """
    bucket_name = "organzationImages"
    organization = await _models.fetchOrganization(organization_id, db)
    if not organization:
        raise HTTPException(status_code=404, detail="organization does not exist")
    #  Delete previous organization image if exist
    await _models.deleteBizImageIfExist(organization)

    uploaded_image = await upload_image(file, db, bucket_name)
    # Update organization image to uploaded image endpoint
    organization.image_url = f"/{bucket_name}/{uploaded_image}"

    try:
        # generate thumbnail
        root_location = os.path.abspath("filestorage")
        thumbnail = gen_thumbnail(
            organization.image_url, root_location,
            organization.id, clean=True
        )
        # save thumbnail path to ExtraInfo table with "org_id" as key
        save_thumbnail_info(thumbnail, organization.id, db)

        db.commit()
        db.refresh(organization)
        # menu = get_organization_menu(organization_id, db)
        return {
            "message": "Successful",
            "data": {"organization": organization},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/organizations/{organization_id}/image")
async def get_organization_image_upload(
    organization_id: str,
    width: int = 100,
    height: int = 100,
    db: orm.Session = Depends(get_db)
):
    """intro--> This endpoint allows you to retrieve the cover image of an organization. To use this endpoint you need to make a get request to the /organizations/{organization_id}/image endpoint

        paramDesc--> On get request, the request url takes the parameter, organization id
            param--> organization_id: This is the unique Id of the organization of interest
            param--> width: this is the width of the image thumbnail
            param--> height: this is the height of the image thumbnail

    returnDesc--> On sucessful request, it returns:

        returnBody--> full_image_path property of the organization
    """
    try:

        org = (
            db.query(_models.Organization)
            .filter(_models.Organization.id == organization_id)
            .first()
        )

        size = (width, height)
        image = org.image_url
        filename = f"{image}"

        root_location = os.path.abspath("filestorage")
        full_image_path = root_location + filename

        # set thumbnail key and query ExtraInfo by key
        key = f"thumbnail_{organization_id}_{size}"
        thumbnail_info = db.query(ExtraInfo).filter(ExtraInfo.key==key).first()

        if thumbnail_info:
            thumb_path, thumb_size = thumbnail_info.value.split(" && ")

            # return thumbnail if path and size exists
            if str(size) == thumb_size and os.path.exists(thumb_path):
                return FileResponse(thumb_path)

            # If thumbnail of size does'nt exist and image to create new exist, create new
            elif org.image_url != "" and os.path.exists(full_image_path):
                if (str(size) != thumb_size) or not os.path.exists(thumb_path):
                    thumbnail = gen_thumbnail(
                        org.image_url, root_location,
                        org.id, size, "thumbnails"
                    )
                    save_thumbnail_info(thumbnail, org.id, db, size)
                    return FileResponse(thumbnail)
            
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        
        # Create new thumbnail if organization has no entry in ExtraInfo table
        else:
            thumbnail = gen_thumbnail(
                org.image_url, root_location,
                org.id, size, "thumbnails"
            )
            save_thumbnail_info(thumbnail, org.id, db, size)
            return FileResponse(thumbnail)

    except Exception as ex:
        if type(ex) == HTTPException:
            raise ex
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.delete("/organizations/{organization_id}", status_code=204)
async def delete_organization(
    organization_id: str,
    user: users_schemas.User = Depends(is_authenticated),
    db: orm.Session = Depends(get_db),
):
    """intro--> This endpoint allows you to delete an organization. To use this endpoint you need to make a delete request to the /organizations/{organization_id} endpoint

        paramDesc--> On delete request, the request url takes the parameter, organization id
            param--> organization_id: This is the unique Id of the organization of interest

    returnDesc--> On sucessful request, it returns:

        returnBody--> "success"
    """
    return await organization_services.delete_organization(organization_id, user, db)


# /////////////////////////////////////////////////////////////////////////////////
# organization Services
