# Software Pattern

## ROUTING

BFA is structured to have it routing and functon calls for each feature in a seperate main file at the root of bigfastapi directory. These files shoud be distinctively named in such a way that is consistent with the
name of the feature. For example, the routing file for a Comment feature will be comment.py. Similarly an Authentication feature will be auth.py.

Definitions of all endpoints (GET, POST, PATCH etc) related to a feature must be written in its main file.
For example, comments.py has to contain the definition of all GET, POST and others endpoints related to comment. In the same context, auth.py will contain similar endpoints for auth related fetaure.

## MODELS

The models directory house all feature models created. For easy search and identification, each model file is to be named after it corresponding feature name. The convention is to combine the feature name and the word, model using using "\_" as a seperator. For example, a file housing comment feature model will be name as "comment_model.py".

It is possisble to have more than one model in relation to a feature. in this case, all of the models related to a feature should be defined in the same model file. A typical example of this scenerio is PasswordReset and PasswordResetToken models that both relate to the Authentication feature. Both, in this case, should reside in
auth_medels.

A model, as used here, can be thought of as an OOP entity. The functions in the class can be anything that manipulate the entity. For example, hybrid properties and class methods.

When creating model classes (entities), ensure to extend the declarative Base class of bigfastapi.db.database so
SQLAlchemy can create a table with your class attributes as table schemas.

## SCHEMA

Like the models directory, schema directory contain all feature related schemas. The naming convention for
each schema file follows the pattern `{feature-name}_schema`. For example, a schema file for Credit related feature will be "credit_schema.py".
Note that this is by no way the same as the naming of the classes in the schema file

# Quick Start

To quickly start contributing features to BFA,

1. Add a model file and model classes following the details in the "MODEL" section above.
2. Add a schema file related to your feature and add the needed Request and Response schema classes to the file
3. Add a main feature file (Routing/controller file) in the root of the bigfastapi directory and include all
   routings and function calls related to your feature in the file.
4. Include a test file and corresponsing test for your feature where necessary.

NOTE: To keep your main feature (controller) file clean, abstract functional logic realated to endpoints to a service
class. For easy search and identification, each feature should have just a service file containing all of it service logic. This file should be named to be consistent with the name of it feature and housed in the service directory.

In a nutshell, each funtionality should have not more that 4 (four) related files - the controller file, the models file, the schema file, and the service file. Depending on the functionality, the number of related files could be less.

# Naming Convention

1. All classes should be defined using Pascal casing style
2. Functions should be named using snake casing style
3. Variable naming should also follow the snake casing style
4. Constants should be all-Capitilized
5. The alias of IMPORTED files, classes or functions should follow easy recognisable patterns.
   Avoid the use of adjoining underscores (`-`) in naming for imports.

   For example

   ```
   import datetime as _dt   - NOT ACCEPTABLE
   import datetime as dt    ACCEPTABLE

   ```

# MANAGING ERROR

---

Check for all possible errors and raise them.

# functions

All functions including endpoint functions should have comments in docstring. These comments describe the main purpose of the function.

# Contribution guide.

All pull requests should be merged only if they comply with the requirements specified.

## Endpoints.

All resource endpoints should:

- **_Have appropriate request body and response models_**

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

It is also important to note that the response model added to the endpoints will apply only for the success status code - 200. To add [response models for other status codes](https://fastapi.tiangolo.com/advanced/additional-responses/), which is advisable, create models with the required fields and field types to match the response status code and detail. The example below demonstrates this implementation.

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

- **_Use lowercase in URLs_**

Case sensitivity in URLs makes them unclear. It’s best to use lowercase (i.e. /user instead of /User) when declaring your API endpoints.

- **_Use pluralised nouns and centralise operations_**

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

- **_Avoid more than two-level nesting_**

In two-level nesting more than two nested resources cannot be used. For example, `posts/{post_id}/comments/{comment_id}` is nested in two levels and is more readable compared to `customers/{customer_id}/payments/{payment_id}/receipts/{receipt_id}/files/{file_id}` which is more than two levels.

## Controller logic

All controllers are created inside the `/bigfastapi` folder. The logic inside these controllers should be limited to requests and responses. All operations should be moved into the appropriate service file for the controller. The service files are to be stored in the `/bigfastapi/services` directory.

## Imports

Importing a model or a schema file should be done following the correction option below:

```
from bigfastapi.models import models - CORRECT APPROACH

from .models import receipt_models - WRONG APPROACH

```

> The sole purpose of these guidelines is to ensure consistency across the codebase and improve the quality of code. If you find anything missing in this documentation, open an issue or raise a pull request if you can get it done.
