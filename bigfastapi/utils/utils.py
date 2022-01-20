import random
import re

import validators
    

def generate_short_id(size=9, chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(random.choice(chars) for _ in range(size))


def validate_email(email):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if(re.search(regex, email)):
        return {"status": True, "message": "Valid"} 
    else:
        return {"status": False, "message": "Enter Valid E-mail"}


def ValidateUrl(url):
    valid=validators.url(url)
    if valid==True:
        return True
    else:
        return False