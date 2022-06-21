from fastapi import APIRouter, HTTPException
from fastapi import APIRouter
import fastapi as _fastapi
import sqlalchemy.orm as _orm
from bigfastapi.db.database import get_db
from bigfastapi.schemas import tutorial_schema
from bigfastapi.models import tutorial_models
from typing import List


app = APIRouter(tags=["Tutorials"])


# SAVE TUTORIAL ENDPOINT
@app.post('/tutorial', response_model=tutorial_schema.TutorialSingleRes)
async def store(newTutorial: tutorial_schema.TutorialRequest, db: _orm.Session = _fastapi.Depends(get_db)):
    """intro-->This endpoint allows you to create a tutorial. To use this endpoint you need to make a post request to the /tutorial endpoint with a specified body of request 

        reqBody-->category: This is the tutorial category you want the tutorial to be in
        reqBody-->title: This is the title of the tutorial
        reqBody-->description: This is the description of the tutorial
        reqBody-->added_by: This is the name of the user that adds the tutorial
        reqBody-->thumbnail: This is an desciptive placeholder
        reqBody-->stream_url: This is the streaming link of the tutorial broadcast 
        reqBody-->text: This is the text body of tutorial

    returnDesc--> On sucessful request, it returns 
        returnBody--> details of the newly created tutorial
    """
    try:
        tutorial = await saveNewTutorial(newTutorial, db)
        return tutorial_models.buildSuccessRes(tutorial, False)
    except PermissionError as exception:
        raise HTTPException(status_code=401, detail=str(exception))
    except LookupError as exception:
        raise HTTPException(status_code=404, detail=str(exception))


# GET TUTORIALS - Can be filtered by category, title or both
@app.get('/tutorials', response_model=tutorial_schema.TutorialListRes)
async def getTutorials(
        category: str = None, title: str = None,
        page_size: int = 10, page: int = 1,
        db: _orm.Session = _fastapi.Depends(get_db)):
    
    """intro-->This endpoint allows you retrieve tutorials. To use this endpoint you need to make a get request to the /tutorials with a chain of query parameters 

        paramDesc-->On get request, the url takes four optional query parameters
            param-->category: This is the category of the tutorial
            param-->title: This is the title of the tutorial
            param-->page_size: This is the size per page, this is 10 by default
            param-->page: This is the page of interest, this is 1 by default
        
    returnDesc--> On sucessful request, it returns 
        returnBody--> an array of queried tutorials
    """

    rowCount = await tutorial_models.getRowCount(db)
    skip = getSkip(page, page_size)

    tutorials = await runFetchQuery(category, title, page_size, skip, rowCount, db)
    return buildSuccessRes(
        tutorials, True, page_size, rowCount,
        getPagination(page, page_size, rowCount, '/tutorials'))


# GET TUTORIALS IN GROUPED OF CATEGORIES- Return result as groups of categories
@app.get('/tutorials/group/categories')
async def getGroup(
        page_size: int = 10, page: int = 1,
        db: _orm.Session = _fastapi.Depends(get_db)):
    
    """intro-->This endpoint allows you to retrieve tutorials in grouped categories. To use this endpoint you need to make a get request to the /tutorials/group/categories endpoint

        paramDesc-->On get request, this endpoint takes two optional query parameters
            param-->page_size: This is the size per page, this is 10 by default
            param-->page: This is the page of interest, this is 1 by default
        
    returnDesc--> On sucessful request, it returns the 
        returnBody--> grouped list of queried tutorials
    """

    rowCount = await tutorial_models.getRowCount(db)
    skip = getSkip(page, page_size)
    groupedTutorials = await tutorial_models.groupByCategory(db, skip, page_size)
    pagination = getPagination(
        page, page_size, rowCount, '/tutorials/group/categories')
    return {"data": groupedTutorials, "total": rowCount, "count": page_size, "pagination": pagination}


# GET A LIST OF ALL TUTORIAL CATEGORIES
@app.get('/tutorials/categories')
async def getCategoryLsit(page_size: int = 10, page: int = 1,
                          db: _orm.Session = _fastapi.Depends(get_db)):
    """intro-->This endpoint allows you to retrieve a list of all available tutorial categories. To use this endpoint you need to make a get request to the /tutorials/categories endpoint

        paramDesc-->On get request, this endpoint takes two optional query parameters
            param-->page_size: This is the size per page, this is 10 by default
            param-->page: This is the page of interest, this is 1 by default
        
    returnDesc--> On sucessful request, it returns a 
        returnBody--> list of all available tutorial categories
    """
    skip = getSkip(page, page_size)
    tutorials = await tutorial_models.groupByCategory(db, skip, page_size)
    categories = buildCategoryList(tutorials)
    return {"data": categories}


# SEARCH TUTORIAL BY MATCHING KEYWORDS
@app.get('/tutorials/search/{keyword}', response_model=tutorial_schema.TutorialListRes)
async def searchByKeyWord(
        keyword: str, page_size: int = 10, page: int = 1,
        db: _orm.Session = _fastapi.Depends(get_db)):
    """intro-->This endpoint allows you to retrieve a list of tutorials based on a keyword query. To use this endpoint you need to make a get request to the /tutorials/search/{keyword} endpoint

    paramDesc-->On get request, this endpoint takes three query parameters
        param-->keyword: This is the keyword of interest to be used for querying tutorials
        param-->page_size: This is the size per page, this is 10 by default
        param-->page: This is the page of interest, this is 1 by default
    
    returnDesc--> On sucessful request, it returns a 
        returnBody--> list of all tutorials that contains the queried keyword
    """
    rowCount = await tutorial_models.getRowCount(db)
    skip = getSkip(page, page_size)
    pagination = getPagination(
        page, page_size, rowCount, '/tutorials/search/{keyword}')
    tutorials = await tutorial_models.searchWithAll(keyword, db, skip, page_size)
    return buildSuccessRes(tutorials, True, page_size, rowCount, pagination)


# UPDATE TUTORIAL DETAILS
@app.put('/tutorials/{itemId}')
async def update(
        itemId: str, newTutorial: tutorial_schema.TutorialRequest,
        db: _orm.Session = _fastapi.Depends(get_db)):

    """intro-->This endpoint allows you to update the details of a particular tutorial. To use this endpoint you need to make a put request to the /tutorials/{itemId} endpoint

    paramDesc-->On get request, this endpoint takes two optional query parameters
        param-->page_size: This is the size per page, this is 10 by default
        param-->page: This is the page of interest, this is 1 by default
    
    returnDesc--> On sucessful request, it returns a 
        returnBody--> list of all available tutorial categories
    """
    try:
        tutorial = await tutorial_models.update(newTutorial, itemId, newTutorial.added_by, db)
        return tutorial_models.buildSuccessRes(tutorial, False)
    except PermissionError as exception:
        raise HTTPException(status_code=401, details=str(exception))
    except LookupError as exception:
        raise HTTPException(status_code=404, details=str(exception))


@app.delete('/tutorials/{itemId}/user/{userId}')
async def delete(itemId: str, userId: str, db: _orm.Session = _fastapi.Depends(get_db)):

    """intro-->This endpoint allows a super user to delete a tutorial. To use this endpoint you need to make a delete request to the /tutorials/{itemId}/user/{userId} endpoint

    paramDesc-->On delete request, this endpoint takes two parameters
        param-->itemId: This is the unique id of the tutorial
        param-->userId: This is the id of the user making the request, user must be a super user for this to go through

    returnDesc--> On sucessful request, it returns a 
        returnBody--> list of all available tutorial categories
    """

    try:
        dbResponse = await tutorial_models.delete(itemId, userId, db)
        return {'data': dbResponse}
    except PermissionError as exception:
        raise HTTPException(status_code=401, details=str(exception))
    except LookupError as exception:
        raise HTTPException(status_code=404, details=str(exception))


# --------------------------------------------------------------------------------------------------#
#                                    HELPER FUNCTIONS SECION
# --------------------------------------------------------------------------------------------------#


# SKIP and OFFSET
def getSkip(page: int, pageSize: int):
    return (page-1)*pageSize


# SAVE A NEW TUTORIA
async def saveNewTutorial(newTutorial: tutorial_schema.TutorialRequest, db: _orm.Session):
    user = await tutorial_models.getUser(newTutorial.added_by, db)
    if user != None:
        if user.is_superuser:
            dbRes = await tutorial_models.store(newTutorial, db)
            return dbRes
        else:
            raise PermissionError("Lacks super admin access")
    else:
        raise LookupError('Could not find user')


# PAGINATION LOGIC
def getPagination(page: int, pageSize: int, count: int, endpoint: str):
    paging = {}
    if (pageSize + getSkip(page, pageSize)) >= count:
        paging['next'] = None
        if page > 1:
            paging['previous'] = f"{endpoint}?page={page-1}&page_size={pageSize}"
        else:
            paging['previous'] = None
    else:
        paging['next'] = f"{endpoint}?page={page+1}&page_size={pageSize}"
        if page > 1:
            paging['previous'] = f"{endpoint}?page={page-1}&page_size={pageSize}"
        else:
            paging['previous'] = None

    return paging


# RUN QUERY
async def runFetchQuery(
        category: str, title: str, page_size: int, skip: int,
        rowCount: int, db: _orm.Session = _fastapi.Depends(get_db)):

    if category is None and title is None:
        return await tutorial_models.fetchAll(db, skip, page_size)
    if category is None and title != None:
        return await tutorial_models.getBytitle(title, db, skip, page_size)
    if category != None and title != None:
        return await tutorial_models.getByCatByTitle(category, title, db, skip, page_size)


# BUID CATEGORY LIST
def buildCategoryList(tutorials: List[tutorial_models.Tutorial]):
    categories = []
    for tutorial in tutorials:
        categories.append(tutorial.category)

    return categories


# GENERIC STRUCTURED RESPONSE BUILDER
def buildSuccessRes(resData, isList: bool, pageSize: int, totalCount: int, pagination: dict):
    if isList:
        return tutorial_schema.TutorialListRes(
            data=resData, total=totalCount, count=pageSize, pagination=pagination)
    else:
        return tutorial_schema.TutorialSingleRes(data=resData)
