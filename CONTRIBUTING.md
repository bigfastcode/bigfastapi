
# Software Pattern
-----

The main file of an endpoint has to contain all the endpoints and external items related
to that. For example, comments.py has to contain the definition of all GET and POST that
have to do with comments.

Inside the models folder, a corresponding file with the models for that endpoint should belong
created that contains the model. For example, we have a comments_model.py file in the models
folder. This file has to contain the definition of the model

A single model, e.g a 'comment' can be thought of as an OOP entity. The functions of this class
have to be anything that manipulate that particular comment, for example - hybrid properties and class methods.

If a piece of functionality has multiple models, they go into the same file. For example, auth.py could
have two models - Sessions and Tokens. These all go in the same models file.

All other functionality related to an endpoint has to be in the respective service folder. That means we have just 4
files for each functionality - the controller file, the models file, the schema file, and the service file. The schema files, however, are Pydantic schemas.

# Naming Variables
---

Models should be capitalised, e.g class User, and should inherit from bigfastapi.database. This should be
imported as import bigfastapi.database as database.

All functions should be like this: def get_country_states(country_code: str):

Underscores should not be used to name any variables.

# Errors
---

Check for all possible errors and raise them.


# functions

All functions including endpoint functions should have comments in docstring. These comments describe the main purpose of the function.



# Contribution guide.
All pull requests should be merged only if they comply with the requirements specified.

## Endpoints.

All resource endpoints should:

- ***Have appropriate request body and response models***

FastAPI supports the [declaration of request body](https://fastapi.tiangolo.com/tutorial/body/) to specify the fields required to access the endpoints and [response models](https://fastapi.tiangolo.com/tutorial/response-model/) to describe the output based on status codes. Specifying these models helps with the proper description of the API to its direct consumers(in our case, the frontend and mobile developers).

> Note: The [models](https://fastapi.tiangolo.com/tutorial/response-model/) for the request body and responses should be created in the `bigfastapi/schemas` folder.

The schema below is a sample to create an email:

```
class Receipt(BaseModel):
    id: Optional[str]
    organization_id: Optional[str]
    sender_email: Optional[str]
    message: Optional[str]
    subject: Optional[str]
    recipient: Optional[str]
    file_id: Optional[str]

    class Config:
        orm_mode = True

class atrributes(Receipt):
    recipient: List[EmailStr] = []
```

The `attributes` class here inherits from `Receipts` to override the recipient type when creating a receipt.

The response schemas for these resources are also created with classes. The schema below is an example response to retrieve a receipt.

```
class Receipt(BaseModel):
    id: Optional[str]
    organization_id: Optional[str]
    sender_email: Optional[str]
    message: Optional[str]
    subject: Optional[str]
    recipient: Optional[str]
    file_id: Optional[str]

    class Config:
        orm_mode = True
```

Although this is a case of a single resource response, fetching all receipts requires a paginated response which also follows the same object-oriented approach with the response fields having their types specified. Here's an example of a paginated response to fetch all receipts.

```
class FetchReceiptsResponse(BaseModel):
    page: int
    size: int
    total: int
    items: List[Receipt]
    previous_page: Optional[str]
    next_page: Optional[str]
```

It is also important to note that the response model added to the endpoints will apply only for the success status code - 200.  To add [response models for other status codes](https://fastapi.tiangolo.com/advanced/additional-responses/), which is advisable, create models with the required fields and field types to match the response status code and detail. The example below demonstrates this implementation.

```
class Message(BaseModel):
    message: str


@app.get("/items/{item_id}", 
response_model=Item, 
responses={
       404: {
          "model": Message, 
          "description": "This item does not exist."
         }
})
async def read_item(item_id: str):
    if item_id == "foo":
        return {"id": "foo", "value": "there goes my hero"}
    else:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
```

Note the consistency with the status code and the JSONResponse `content` field. Don't worry about the rendering on the documentation, it is handled by FastAPI :)


- ***Use lowercase in URLs***

Case sensitivity in URLs makes them unclear. It’s best to use lowercase (i.e. /user instead of /User) when declaring your API endpoints.

- ***Use pluralised nouns and centralise operations***

Think of a business concept like `receipt` and build one endpoint for them with separate HTTP methods describing what you want to do with the entity. For example:

```
Endpoint: /receipts
Action verbs: 
      - GET [/receipts] (to fetch all receipts)
      - POST [/receipts] (to create a new receipts)
      - DELETE [/receipts] (to delete all receipts)
      - GET [/receipts/{receipt_id}] (to fetch the details of a receipt)
      - PATCH [/receipts/{receipt_id}] (to update a field in a receipt)
      - PUT [/receipts/{receipt_id}] (to update all fields a receipt)
      - DELETE [/receipt/{receipt_id}] (to delete a receipt)
```

Additionally, nouns should be in their plural form unless they represent a single resource. Unnecessarily long nouns should also be avoided because they make things look messy and unorganised. For example, you should use `/subscribers` instead of `/api-subscribers`.
  
- ***Avoid more than two-level nesting***

In two-level nesting more than two nested resources cannot be used. For example, `posts/{post_id}/comments/{comment_id}` is nested in two levels and is more readable compared to `customers/{customer_id}/payments/{payment_id}/receipts/{receipt_id}/files/{file_id}` which is more than two levels.

## Controller logic

All controllers are created inside the `/bigfastapi` folder. The logic inside these controllers should be limited to requests and responses. All operations should be moved into the appropriate service file for the controller. The service files are to be stored in the `/bigfastapi/services` directory.


## Models

All models are to be named in PascalCase e.g LandingPage.

All file-level functions in their model file should be moved to their services file. The models are only going to contain models relating to a resource and not services.

## Imports

Importing a model or a schema file should be done relatively in the format below:

```
from .models import receipt_models
from .schemas import receipt_schemas
```

> The sole purpose of these guidelines is to ensure consistency across the codebase and improve the quality of code. If you find anything missing in this documentation, open an issue or raise a pull request if you can get it done.

