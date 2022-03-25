import datetime
from uuid import uuid4
from pydantic import BaseModel
from fastapi import APIRouter, status, HTTPException, BackgroundTasks
from typing import List
import fastapi
from fastapi_mail import FastMail, MessageSchema
from .email import conf
import sqlalchemy.orm as orm
from fastapi.responses import JSONResponse
from .auth_api import is_authenticated
from .schemas import users_schemas
from .schemas import contact_schemas
from .models import contact_model

from bigfastapi.db.database import get_db

app = APIRouter(tags=["Contacts and Contact Us"])
fm = FastMail(conf)


@app.post("/contact")
def create_contact(contact: contact_schemas.ContactBase, db: orm.Session = fastapi.Depends(get_db),
                   user: users_schemas.User = fastapi.Depends(is_authenticated)):
    if user.is_superuser is True:
        cont = contact_model.Contact(id=uuid4().hex,
                                     phone=contact.phone,
                                     address=contact.address,
                                     map_coordinates=contact.map_coordinates)
        db.add(cont)
        db.commit()
        db.refresh(cont)
        return {"message": "Contact created successfully", "contact": contact_schemas.Contact.from_orm(cont)}
    return JSONResponse({"message": "Only an Admin can create a contact"}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.put("/contact/{contact_id}")
def update_contact(contact: contact_schemas.ContactBase, contact_id: str, db: orm.Session = fastapi.Depends(get_db),
                   user: users_schemas.User = fastapi.Depends(is_authenticated)):
    if user.is_superuser is True:
        Uc = db.query(contact_model.Contact).filter(contact_model.Contact.id == contact_id).first()
        if Uc:
            Uc.phone = contact.phone
            Uc.address = contact.address
            Uc.map_coordinates = contact.map_coordinates
            db.commit()
            db.refresh(Uc)
            return {"message": "Contact updated successfully", "Uc": contact_schemas.Contact.from_orm(Uc)}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return JSONResponse({"message": "Only an Admin can update a contact"}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.get("/contact", response_model=List[contact_schemas.Contact])
def get_all_contacts(db: orm.Session = fastapi.Depends(get_db)):
    contacts = db.query(contact_model.Contact).all()
    return list(map(contact_schemas.Contact.from_orm, contacts))


@app.get("/contact/{contact_id}", response_model=contact_schemas.Contact)
def get_contact_by_id(contact_id: str, db: orm.Session = fastapi.Depends(get_db)):
    contact = db.query(contact_model.Contact).filter(contact_model.Contact.id == contact_id).first()
    if contact:
        return contact_schemas.Contact.from_orm(contact)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")


@app.delete("/contact/{contact_id}")
def delete_contact(contact_id: str, db: orm.Session = fastapi.Depends(get_db),
                   user: users_schemas.User = fastapi.Depends(is_authenticated)):
    if user.is_superuser is True:
        Dc = db.query(contact_model.Contact).filter(contact_model.Contact.id == contact_id).first()
        if Dc:
            db.delete(Dc)
            db.commit()
            return contact_model.Contact.from_orm(Dc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return JSONResponse({"message": "Only an Admin can delete a contact"}, status_code=status.HTTP_401_UNAUTHORIZED)

    # ============================ CONTACT US =====================================#


@app.post("/contactus")
def create_contactUS(contact: contact_schemas.ContactUSB, background_tasks: BackgroundTasks,
                     db: orm.Session = fastapi.Depends(get_db)):
    cont = contact_model.ContactUS(id=uuid4().hex,
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


@app.get("/contactus", response_model=List[contact_schemas.ContactUS])
def get_all_contactUS(db: orm.Session = fastapi.Depends(get_db),
                      user: users_schemas.User = fastapi.Depends(is_authenticated)):
    if user.is_superuser is True:
        contacts = db.query(contact_model.ContactUS).all()
        return list(map(contact_schemas.ContactUS.from_orm, contacts))
    return JSONResponse({"message": "Admin access only"}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.get("/contactus/{contactus_id}", response_model=contact_schemas.ContactUS)
def get_contactUS_by_id(contactus_id: str, db: orm.Session = fastapi.Depends(get_db),
                        user: users_schemas.User = fastapi.Depends(is_authenticated)):
    if user.is_superuser is True:
        contact = db.query(contact_model.ContactUS).filter(contact_model.ContactUS.id == contactus_id).first()
        if contact:
            return contact_schemas.ContactUS.from_orm(contact)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact details not found")
    return JSONResponse({"message": "Admin access only"}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.delete("/contactus/{contactus_id}")
def delete_contactUS(contactus_id: str, db: orm.Session = fastapi.Depends(get_db),
                     user: users_schemas.User = fastapi.Depends(is_authenticated)):
    if user.is_superuser is True:
        Dc = db.query(contact_model.ContactUS).filter(contact_model.ContactUS.id == contactus_id).first()
        if Dc:
            db.delete(Dc)
            db.commit()
            return contact_model.ContactUS.from_orm(Dc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact details not found")
    return JSONResponse({"message": "Admin access only"}, status_code=status.HTTP_401_UNAUTHORIZED)

    # =====================Contact mail service====================#


def SendContactMail(background_tasks: BackgroundTasks, message1, message2):
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message1)
    background_tasks.add_task(fm.send_message, message2)
