import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','MathPrepPro.settings')
import django
django.setup()

from django.contrib.auth.models import User
import datetime
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.core.mail import get_connection
from django.core.exceptions import ObjectDoesNotExist
from secrets_sendinblue import *
import sys

################################################################################

# Workflow
# 1. Divide unsubs into PRO and non PRO
# 2. If any PRO users happen to have unsubed, add them back to the subed list. They must contact admin to cancel so the payment can be stopped.
# 3. Delete any non pro users from the backend

# To Dos:
# 1. Update the host site
# 2. Update the from email

# Improvements
# 1.

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = SEND_IN_BLUE_KEY
api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
list_id_subed = 2
list_id_unsub = 6
hoursAgo = datetime.datetime.now() - datetime.timedelta(hours = 1)
modified_since = hoursAgo.strftime('%Y-%m-%dT%H:%M')
limit = 500
offset = 0
sort = 'desc'

unsub_emails = []
unsub_pro_emails = []
admin_errors = []

def collect_unsubs(): # group the contacts into lists based on their PRO status from the last 24 hours.

    unsub_list = None

    try:
        unsub_list = api_instance.get_contacts_from_list(list_id_unsub, modified_since=modified_since, limit=limit, offset=offset, sort=sort)
    except ApiException as e:
        admin_errors.append("1, Exception when calling ContactsApi->get_contacts_from_list: %s\n" % e)

    try:
        for person in unsub_list.contacts:
            pro_status = person['attributes']['PRO']
            # print(pro_status)
            email = person['email']
            if pro_status == True:
                unsub_pro_emails.append(email)
            else:
                unsub_emails.append(email)
    except:
        admin_errors.append("".join(['2, ', person, str(sys.exc_info()[0]), ]))

def move_pro_contacts(): # Move the unsubed PRO users back to subed list.

    unsub_list = None
    update_contact = None

    try:
        unsub_list = api_instance.get_contacts_from_list(list_id_unsub, modified_since=modified_since, limit=limit, offset=offset, sort=sort)
        update_contact = sib_api_v3_sdk.UpdateContact(list_ids = [2], unlink_list_ids = [6])
    except:
        admin_errors.append("3, Exception when calling ContactsApi->get_contacts_from_list: %s\n" % e)

    for person in unsub_list.contacts:
        identifier = person['email']
        if (identifier in unsub_pro_emails): # Move pro back to subed list
            try:
                api_instance.update_contact(identifier, update_contact)
            except:
                admin_errors.append("".join(['4, ', identifier, str(sys.exc_info()[0]), ]))
        else: # do not move none PRO users
            pass

def delete_non_pro_unsub():
    for email in unsub_emails:
        try:
            User.objects.get(email=email).delete()
        except ObjectDoesNotExist:
            pass
        except:
            admin_errors.append("".join(['5, ', email, str(sys.exc_info()[0]), ]))

def notify_admin(errors):
    if errors:
        context = {}
        email_title = "Admin Errors - 3-unsub"
        to_email = 'mathpreppro@gmail.com'
        context['errors'] = errors
        try:
            error_email = []
            error_email.append(generate_email('AppOne/admin_error.html', context, email_title, [to_email]))
            get_connection().send_messages(error_email)
        except:
            pass

if __name__ == '__main__':
    collect_unsubs()
    move_pro_contacts()
    delete_non_pro_unsub()
    notify_admin(admin_errors)

################################### ERRORS #####################################
# 1 Trying to grab all new unsubed users
# 2 Trying to categorize an unsub
# 3 Trying to grab all unsubs to move
# 4 Trying to move (or leave) and unsub
# 5 Trying to delete unmoved unsubs from backend db

################################### API LINKS ##################################

# https://github.com/sendinblue/APIv3-python-library
# https://github.com/sendinblue/APIv3-python-library/blob/master/docs/ContactsApi.md#get_contacts_from_list
