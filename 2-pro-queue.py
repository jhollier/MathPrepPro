import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','MathPrepPro.settings')
import django
django.setup()

from AppOne import models
from django.contrib.auth.models import User
import datetime
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.core.mail import get_connection
from rest_framework.authtoken.models import Token
from emails import *
from secrets_sendinblue import *
import sys
from django.db import IntegrityError

################################################################################

# Workflow
# 1. Add new pro users to backend db. If they already exist, upgrade them.
# 2. Send email with pro list for preexisting users.
# 3. Move contats from pro_queue list to subed list.
# 4. Update all the moved contacts to be PRO status.

# To Dos:
# 1. Update the host site
# 2. Update the from email

# Improvements
# 1. The pro status is not even needed on sendinblue
# 2. Can the pro status be set once the contact is initially created? Wont know till the front end is created

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = SEND_IN_BLUE_KEY
api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
list_id_subed = 2
list_id_pro_queue = 4
hoursAgo = datetime.datetime.now() - datetime.timedelta(hours = 1)
modified_since = hoursAgo.strftime('%Y-%m-%dT%H:%M')
limit = 500
offset = 0
sort = 'desc'

pro_user_emails = []
preexisting_pro_user_emails = []
admin_errors = []

def set_to_pro(email):

    try: # Set user to PRO in backend db
        new_pro_user = User.objects.get(email = email)
        new_pro_user = models.UserProfileInfo.objects.get(user = new_pro_user)
        new_pro_user.pro = True
        new_pro_user.save()
    except:
        admin_errors.append("".join(['3, ', email, str(sys.exc_info()[0]), ]))

def create_pro_users():

    contacts = []

    try: # Grab list of new Pro subscribers
        pro_queue_list = api_instance.get_contacts_from_list(list_id_pro_queue, modified_since=modified_since, limit=limit, offset=offset, sort=sort)
        contacts = pro_queue_list.contacts
    except ApiException as e:
        admin_errors.append("1, Exception when calling ContactsApi->get_contacts_from_list: %s\n" % e)

    for person in contacts:
        email = person['email']
        pro_user_emails.append(email)

        try: # Create new user
            User.objects.create(username=email, email=email)
            set_to_pro(email)
        except IntegrityError: # if the user is already in the db
            set_to_pro(email)
            preexisting_pro_user_emails.append(email)
            # print("The user with email = %s is already in the db. Their status will be upgraded to PRO and a problem list sent\n" % email)
        except:
            admin_errors.append("".join(['2, ', email, str(sys.exc_info()[0]), ]))

def send_pro_list_email():

    host_base_site = "https://www.daily.mathpreppro.com/"
    email_list = []

    for email in preexisting_pro_user_emails:
        try:
            email_title = "MathPrepPro - Prior Solutions"
            to_email = email
            context = {}
            pro_user = User.objects.get(email=email)
            pro_user = models.Token.objects.get(user=pro_user)
            token = pro_user.key
            context['solutions_url'] = "".join([host_base_site, "prolist/", token])
            email_list.append(generate_email('AppOne/welcome_pro.html', context, email_title, [to_email]))
        except:
            admin_errors.append("".join(['4, ', email, str(sys.exc_info()[0]), ]))

    try:
        get_connection().send_messages(email_list)
    except:
        admin_errors.append("".join(['5, ', str(sys.exc_info()[0]), ]))

def move_pro_contacts():

    pro_queue_list = None
    update_contact = None

    try:
        pro_queue_list = api_instance.get_contacts_from_list(list_id_pro_queue, modified_since=modified_since, limit=limit, offset=offset, sort=sort)
        update_contact = sib_api_v3_sdk.UpdateContact(list_ids = [2], unlink_list_ids = [4])
    except ApiException as e:
        admin_errors.append("6, Exception when calling ContactsApi->get_contacts_from_list: %s\n" % e)

    for person in pro_queue_list.contacts:
        identifier = person['email']
        try:
            api_instance.update_contact(identifier, update_contact)
        except:
            admin_errors.append("".join(['7, ', person, str(sys.exc_info()[0]), ]))

def set_to_pro_in_list():

    update_contact = sib_api_v3_sdk.UpdateContact(attributes = {'PRO':True})
    for identifier in pro_user_emails:
        try:
            api_instance.update_contact(identifier, update_contact)
        except ApiException as e:
            admin_errors.append("8, Exception when calling ContactsApi->get_contacts_from_list: %s\n" % e)

def notify_admin(errors):
    if errors:
        context = {}
        email_title = "Admin Errors - 2-pro-queue"
        to_email = 'mathpreppro@gmail.com'
        context['errors'] = errors
        try:
            error_email = []
            error_email.append(generate_email('AppOne/admin_error.html', context, email_title, [to_email]))
            get_connection().send_messages(error_email)
        except:
            pass

if __name__ == '__main__':
    create_pro_users()
    send_pro_list_email()
    move_pro_contacts()
    set_to_pro_in_list()
    notify_admin(admin_errors)

################################### ERRORS #####################################
# 1 Trying to grab new pro contacts list
# 2 Trying to create new pro user
# 3 Trying to set a user to pro
# 4 Trying to build email
# 5 Trying to send email list
# 6 Trying to grab new pro contacts to move
# 7 Trying to move contact
# 8 Trying to set moved contact to PRO

################################### API LINKS ##################################

# https://github.com/sendinblue/APIv3-python-library
# https://github.com/sendinblue/APIv3-python-library/blob/master/docs/ContactsApi.md#get_contacts_from_list
