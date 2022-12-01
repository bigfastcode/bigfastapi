import os

import pkg_resources
from decouple import config

JWT_SECRET = config("JWT_SECRET")
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")
GOOGLE_SECRET = config("GOOGLE_SECRET")
REDIRECT_URL = config("REDIRECT_URL")
MAIL_USERNAME = config("MAIL_USERNAME")
MAIL_PASSWORD = config("MAIL_PASSWORD")
MAIL_FROM = config("MAIL_FROM")
DB_PORT = config("DB_PORT")
PYTHON_ENV = config("PYTHON_ENV")
DB_URL = config('DB_URL')
DB_TYPE = config('DB_TYPE')
API_REDIRECT_URL = config("API_REDIRECT_URL")
API_URL = config("API_URL")
MAIL_PORT = int(config("MAIL_PORT"))
MAIL_SERVER = config("MAIL_SERVER")
MAIL_FROM_NAME = config("MAIL_FROM_NAME")
TEMPLATE_FOLDER = config("TEMPLATE_FOLDER") + "/templates/email/"
BASE_URL = config("BASE_URL")
CLIENT_REDIRECT_URL = config("CLIENT_REDIRECT_URL")
# EMAIL_VERIFICATION_TEMPLATE = config('EMAIL_VERIFICATION_TEMPLATE')
# PASSWORD_RESET_TEMPLATE = config('PASSWORD_RESET_TEMPLATE')
FILES_BASE_FOLDER = config("FILES_BASE_FOLDER")
LANDING_PAGE_FORM_PATH = config("LANDING_PAGE_FORM_PATH")
LANDING_PAGE_FOLDER = config("LANDING_PAGE_FOLDER")
ANCHOR_TEST_KEY=config("ANCHOR_TEST_KEY")
ANCHOR_API_URL=config("ANCHOR_API_URL")
TELEX_ORGANIZATION_ID=config("TELEX_ORGANIZATION_ID")
TELEX_ORGANIZATION_KEY=config("TELEX_ORGANIZATION_KEY")
SMS_API=config("SMS_API")

# EMAIL_VERIFICATION_TEMPLATE="email/welcome_email.html"
# PASSWORD_RESET_TEMPLATE="email/password_reset.html"

# If the templates folder is not valid, then we use the bigfastapi templates folder
if os.path.exists(TEMPLATE_FOLDER) is False:
    TEMPLATE_FOLDER = pkg_resources.resource_filename("bigfastapi", "templates/")

# EMAIL_VERIFICATION_TEMPLATE = os.path.join(TEMPLATE_FOLDER, "email", "welcome_email.html")
# PASSWORD_RESET_TEMPLATE = os.path.join(TEMPLATE_FOLDER,"email", "password_reset.html")
