import datetime
from uuid import uuid4
from pydantic import BaseModel
from fastapi import APIRouter, status, HTTPException, BackgroundTasks
from typing import List
import fastapi
from fastapi_mail import FastMail, MessageSchema
from .services import email_services
import sqlalchemy.orm as orm
from fastapi.responses import JSONResponse
from bigfastapi.services.auth_service import is_authenticated
from .schemas import users_schemas
from .schemas import contact_schemas
from .models import contact_model

from bigfastapi.db.database import get_db

app = APIRouter(tags=["Contacts and Contact Us"])
fm = FastMail(email_services.conf)


@app.post("/contact")
def create_contact(contact: contact_schemas.ContactBase, db: orm.Session = fastapi.Depends(get_db),
    user: users_schemas.User = fastapi.Depends(is_authenticated)):
    """intro-->This endpoint is used get all contacts. To use this endpoint you need to make a get request to the /contact endpoint 

    returnDesc--> On sucessful request, it returns
        returnBody--> an array of all contact's details
    """
    if user.is_superuser is not True:
        return JSONResponse({"message": "Only an Admin can create a contact"}, status_code=status.HTTP_401_UNAUTHORIZED)

    cont = contact_model.ContactUs(id=uuid4().hex,
                                    phone=contact.phone,
                                    address=contact.address,
                                    map_coordinates=contact.map_coordinates)
    db.add(cont)
    db.commit()
    db.refresh(cont)
    return {"message": "Contact created successfully", "contact": contact_schemas.Contact.from_orm(cont)}


@app.put("/contact/{contact_id}")
def update_contact(contact: contact_schemas.ContactBase, contact_id: str, db: orm.Session = fastapi.Depends(get_db),
                   user: users_schemas.User = fastapi.Depends(is_authenticated)):
    if user.is_superuser is not True:
        return JSONResponse({"message": "Only an Admin can update a contact"}, status_code=status.HTTP_401_UNAUTHORIZED)

    Uc = db.query(contact_model.Contact).filter(contact_model.Contact.id == contact_id).first()
    if not Uc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    Uc.phone = contact.phone
    Uc.address = contact.address
    Uc.map_coordinates = contact.map_coordinates
    db.commit()
    db.refresh(Uc)
    return {"message": "Contact updated successfully", "Uc": contact_schemas.Contact.from_orm(Uc)}


@app.get("/contact", response_model=List[contact_schemas.Contact])
def get_all_contacts(db: orm.Session = fastapi.Depends(get_db)):
    """intro-->This endpoint is used get all contacts. To use this endpoint you need to make a get request to the /contact endpoint 

    returnDesc--> On sucessful request, it returns
        returnBody--> an array of all contact's details
    """
    contacts = db.query(contact_model.ContactUs).all()
    return list(map(contact_schemas.Contact.from_orm, contacts))


@app.get("/contact/{contact_id}", response_model=contact_schemas.Contact)
def get_contact_by_id(contact_id: str, db: orm.Session = fastapi.Depends(get_db)):
    """intro-->This endpoint is used get a particular contact. To use this endpoint you need to make a get request to the /contact/{contact_id} endpoint 
    
    returnDesc--> On successful request, it returns
        returnBody--> details of queried contact
    """
    contact = db.query(contact_model.ContactUs).filter(contact_model.ContactUs.id == contact_id).first()
    if contact:
        return contact_schemas.Contact.from_orm(contact)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")


@app.delete("/contact/{contact_id}")
def delete_contact(contact_id: str, db: orm.Session = fastapi.Depends(get_db),
                   user: users_schemas.User = fastapi.Depends(is_authenticated)):
    """intro-->This endpoint allows you to delete a contact. To use this endpoint you need to make a delete request to the /contact/{contact_id} endpoint 
            paramDesc-->On get request the url takes a query parameter contact_id
                param-->contact_id: This the unique identifier of the contact
    returnDesc--> On successful request, it returns message
        returnBody--> "success"
    """
    if user.is_superuser is True:
        Dc = db.query(contact_model.ContactUs).filter(contact_model.ContactUs.id == contact_id).first()
        if Dc:
            db.delete(Dc)
            db.commit()
            return contact_model.ContactUs.from_orm(Dc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return JSONResponse({"message": "Only an Admin can delete a contact"}, status_code=status.HTTP_401_UNAUTHORIZED)

    # ============================ CONTACT US =====================================#


@app.post("/contactus")
def create_contactUS(contact: contact_schemas.ContactUSB, background_tasks: BackgroundTasks,
                     db: orm.Session = fastapi.Depends(get_db)):
    """intro-->This endpoint is used to send a contact-us message. To use this endpoint you need to make a post request to the /contactus endpoint with a specified body of request
        reqBody-->name: This requires the name of the person the message
        reqBody-->email: This requires the email of the person sending the message
        reqBody-->subject: This is the subject of the message
        reqBody-->message: This is the body of the contact-us message
        
    returnDesc--> On successful request, it returns message
        returnBody--> "message sent successfully"
    """
    cont = contact_model.ContactRequest(id=uuid4().hex,
                                   name=contact.name,
                                   email=contact.email,
                                   subject=contact.subject,
                                   message=contact.message)
    db.add(cont)
    db.commit()
    db.refresh(cont)

    message1 = MessageSchema(
        subject="New Contact Request",
        recipients=["admins@bigfastapi.com"],
        body=f"Dear Admin,\n A new contact request was sent from: {cont.email}\n {cont.name}\n{cont.subject} \n{cont.message}\nThanks.")

    visitor_name = cont.name
    split_name = visitor_name.split()
    Indexed_name = split_name[0]
    date_created = datetime.datetime.now()

    message2 = MessageSchema(
        subject="Message Received",
        recipients=[cont.email],
        body=f"Good day {Indexed_name},\nyour message has been received at {date_created}\nbe rest assured that we will get back to you in due time,\nhave a lovely day.")
    SendContactMail(background_tasks=background_tasks, message1=message1, message2=message2)
    return {"message": "message sent successfully"}


@app.get("/contactus", response_model=List[contact_schemas.ContactRequest])
def get_all_contactUS(db: orm.Session = fastapi.Depends(get_db),
                      user: users_schemas.User = fastapi.Depends(is_authenticated)):
    """intro-->This endpoint allows you to retrieve all contact-us message. To use this endpoint you need to make a get request to the /contactus
    returnDesc--> On successful request, it returns message
        returnBody--> "success"
    """
    if user.is_superuser is True:
        contacts = db.query(contact_model.ContactRequest).all()
        return list(map(contact_schemas.ContactRequest.from_orm, contacts))
    return JSONResponse({"message": "Admin access only"}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.get("/contactus/{contactus_id}", response_model=contact_schemas.ContactRequest)
def get_contactUS_by_id(contactus_id: str, db: orm.Session = fastapi.Depends(get_db),
                        user: users_schemas.User = fastapi.Depends(is_authenticated)):
    """intro-->This endpoint allows you to retrieve a particular contact-us message. To use this endpoint you need to make a get request to the /contactus/{contactus_id}
        paramDesc-->On get request the url takes a query parameter contactus_id
            param-->contactus_id: This the unique identifier of the contact-us message
    returnDesc--> On successful request, it returns 
        returnBody--> details of the contact us
    """
    if user.is_superuser is True:
        contact = db.query(contact_model.ContactRequest).filter(contact_model.ContactRequest.id == contactus_id).first()
        if contact:
            return contact_schemas.ContactRequest.from_orm(contact)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact details not found")
    return JSONResponse({"message": "Admin access only"}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.delete("/contactus/{contactus_id}")
def delete_contactUS(contactus_id: str, db: orm.Session = fastapi.Depends(get_db),
                     user: users_schemas.User = fastapi.Depends(is_authenticated)):
    """intro-->This endpoint allows you to delete a contact-us message. To use this endpoint you need to make a delete request to the /contactus/{contactus_id}
        paramDesc-->On get request the url takes a query parameter contactus_id
            param-->contactus_id: This the unique identifier of the contact-us message
    returnDesc--> On successful request, it returns message
        returnBody--> "success"
    """
    if user.is_superuser is True:
        Dc = db.query(contact_model.ContactRequest).filter(contact_model.ContactRequest.id == contactus_id).first()
        if Dc:
            db.delete(Dc)
            db.commit()
            return contact_model.ContactRequest.from_orm(Dc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact details not found")
    return JSONResponse({"message": "Admin access only"}, status_code=status.HTTP_401_UNAUTHORIZED)

    # =====================Contact mail service====================#


def SendContactMail(background_tasks: BackgroundTasks, message1, message2):
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message1)
    background_tasks.add_task(fm.send_message, message2)
