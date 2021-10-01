import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','MathPrepPro.settings')
import django
django.setup()
################################################################################

from django.core.mail import send_mail, send_mass_mail, get_connection, EmailMultiAlternatives
from AppOne import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render
from emails import *
import sys

################################ NOTES #########################################

# Production to dos:
# 1. Change the from email
# 2. Update the host_base

################################################################################

def send_daily_emails():
    '''
    Compiles and pushes all daily emails to AWS SES.
    Returns a list of user emails that failed to compile.
    '''

    admin_errors = []
    email_list = []
    user_query = None
    
    user_query = User.objects.all()
    admin_errors.append("".join(['1, ', str(sys.exc_info()[0]), ]))

    for person in user_query:

        try:
            person_userprofileinfo = models.UserProfileInfo.objects.get(user = person)
            problem_number = person_userprofileinfo.problem_number
            problem_query = models.Problem.objects.get(pk=problem_number)
            to_email = person.email
            email_title = "".join(["Daily Problem - ", str(problem_query.problem_name)])

            context = {}
            context['problem_statement'] = problem_query.problem_statement
            context['problem_image_url'] = "".join([host_base_site, "static/images/problems/", str(problem_query.pk), "_statement.png"])
            context['video_url'] = problem_query.problem_solution_url
            context['pk'] = problem_number
            context['pro'] = person_userprofileinfo.pro
            if context['pro']:
                token_obj = models.Token.objects.get(user=person)
                token = token_obj.key
            context['solutions_url'] = "".join([host_base_site, "prolist/", token])
            context['pro_detail_url'] = "".join([host_base_site, "prolist/", token, "/", str(problem_number)])
            email_list.append(generate_email('AppOne/daily_problem.html', context, email_title, [to_email]))
        except:
            # Do not error out if a single email fails to compile
            admin_errors.append("".join([person.email, str(sys.exc_info()[0]), ]))

    get_connection().send_messages(email_list)
    admin_errors.append("".join(['3, ', str(sys.exc_info()[0]), ]))
    
    return admin_errors


def notify_admin(errors):
    '''
    Notify the admin directly if any emails failed to comiple.
    Takes in a list of user emails that did not compile.
    '''
    
        context = {}
        email_title = "Admin Errors - 5-send-daily-emails"
        to_email = 'mathpreppro@gmail.com'
        context['errors'] = errors
        error_email = []
        error_email.append(generate_email('AppOne/admin_error.html', context, email_title, [to_email]))
        get_connection().send_messages(error_email)
 

if __name__ == '__main__':
    errors = send_daily_emails()
    if errors:
        notify_admin(errors)
