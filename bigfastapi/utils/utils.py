import random
import re
import validators
import fastapi
import json
import pkg_resources

DATA_PATH = pkg_resources.resource_filename('bigfastapi', 'data/')


def generate_short_id(size=9, chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(random.choice(chars) for _ in range(size))


def validate_email(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if (re.search(regex, email)):
        return {"status": True, "message": "Valid"}
    else:
        return {"status": False, "message": "Enter Valid E-mail"}


def ValidateUrl(url):
    valid = validators.url(url)
    if valid == True:
        return True
    else:
        return False


def paginate_data(data, page_size: int, page_number: int):
    start = (page_number - 1) * page_size
    end = start + page_size


    return {
        "data": data[start: end],
        "total_documents": data.__len__(),
        "page_limit": page_size
    }


def find_country(ctry):
     with open(DATA_PATH + "/countries.json") as file:
        cap_country = ctry.capitalize()
        countries = json.load(file)
        found_country = next((country for country in countries if country['name'] == cap_country), None)
        if found_country is None:
            raise fastapi.HTTPException(status_code=403, detail="This country doesn't exist")
        return found_country['name']


def dialcode(dcode):
     with open(DATA_PATH + "/dialcode.json") as file:
        dialcodes = json.load(file)
        found_dialcode = next((dialcode for dialcode in dialcodes if dialcode['dial_code'] == dcode), None)
        if found_dialcode is None:
            raise fastapi.HTTPException(status_code=403, detail="This is an invalid dialcode")
        return found_dialcode['dial_code']


def generate_code(new_length:int= None):
    length = 6
    if new_length is not None:
        length = new_length
    if length < 4:
        raise fastapi.HTTPException(status_code=400, detail="Minimum code lenght is 4")
    code = ""
    for i in range(length):
        code += str(random.randint(0,9))
    return code
