import os
from decouple import config
import pkg_resources
JWT_SECRET = config("JWT_SECRET")
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")
GOOGLE_SECRET = config("GOOGLE_SECRET")
REDIRECT_URL = config("REDIRECT_URL")
MAIL_USERNAME =config('MAIL_USERNAME')
MAIL_PASSWORD =config('MAIL_PASSWORD')
MAIL_FROM =config('MAIL_FROM')
MAIL_PORT = int(config('MAIL_PORT'))
MAIL_SERVER =config('MAIL_SERVER')
MAIL_FROM_NAME =config('MAIL_FROM_NAME')
TEMPLATE_FOLDER = config('TEMPLATE_FOLDER')
# EMAIL_VERIFICATION_TEMPLATE = config('EMAIL_VERIFICATION_TEMPLATE')
# PASSWORD_RESET_TEMPLATE = config('PASSWORD_RESET_TEMPLATE')
FILES_BASE_FOLDER = config('FILES_BASE_FOLDER')

# EMAIL_VERIFICATION_TEMPLATE="email/welcome_email.html"
# PASSWORD_RESET_TEMPLATE="email/password_reset.html"

# If the templates folder is not valid, then we use the bigfastapi templates folder
if os.path.exists(TEMPLATE_FOLDER) == False:
    TEMPLATE_FOLDER = pkg_resources.resource_filename('bigfastapi', 'templates/')
    
# EMAIL_VERIFICATION_TEMPLATE = os.path.join(TEMPLATE_FOLDER, "email", "welcome_email.html")
# PASSWORD_RESET_TEMPLATE = os.path.join(TEMPLATE_FOLDER,"email", "password_reset.html")