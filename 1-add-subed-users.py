import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','MathPrepPro.settings')
import django
django.setup()

from AppOne import models
import sys
import datetime
import time
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from secrets_sendinblue import *

################################################################################

# Workflow
# 1. Grabs all new subed users (non pro) and sends them (email only) to the backend db. Note any PRO users added within the last 24 hours will be 'continued'
#
# Improvements
# 1. Date might need some improvements wrt time zone, etc. Might be fine though
# 2. Not sure what happens if contacts list is paginated after 500 people - likely will never be a problem
# 3. Add email to admin if there is an error here

admin_errors = []

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = SEND_IN_BLUE_KEY
api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
list_id_subed = 2
hoursAgo = datetime.datetime.now() - datetime.timedelta(hours = 1)
modified_since = hoursAgo.strftime('%Y-%m-%dT%H:%M')
limit = 500 # int | Number of documents per page (optional) (default to 50)
offset = 0
sort = 'desc'

def add_sub_users():

    contacts = []
    try:
        subed_list = api_instance.get_contacts_from_list(list_id_subed, modified_since=modified_since, limit=limit, offset=offset, sort=sort)
        contacts = subed_list.contacts
    except ApiException as e:
        admin_errors.append("1, Exception when calling ContactsApi->get_contacts_from_list: %s\n" % e)

    for person in contacts:
        try:
            email = person['email']
            models.User.objects.create(username=email, email=email)
        except django.db.utils.IntegrityError: # if the user already exists, do nothing
            pass
        except:
            admin_errors.append("".join(['2, ', person, str(sys.exc_info()[0]), ]))

def notify_admin(errors):
    if errors:
        context = {}
        email_title = "Admin Errors - 1-add-subed-user"
        to_email = 'mathpreppro@gmail.com'
        context['errors'] = errors
        try:
            error_email = []
            error_email.append(generate_email('AppOne/admin_error.html', context, email_title, [to_email]))
            get_connection().send_messages(error_email)
        except:
            pass

if __name__ == '__main__':
    add_sub_users()
    notify_admin(admin_errors)

################################### ERRORS #####################################
# 1 Trying to grab new subed users
# 2 Trying add subed user to the backed db

################################### API LINKS ##################################

# https://github.com/sendinblue/APIv3-python-library
# https://github.com/sendinblue/APIv3-python-library/blob/master/docs/ContactsApi.md#get_contacts_from_list
