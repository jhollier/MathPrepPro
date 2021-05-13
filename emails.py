import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','MathPrepPro.settings')
import django
django.setup()
################################################################################

from django.core.mail import get_connection, EmailMultiAlternatives
from AppOne import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.authtoken.models import Token

### UNIVERSAL EMAIL FUNCTION ###

host_base_site = "https://www.daily.mathpreppro.com/"
from_email = 'MathPrepPro <contact@mathpreppro.com>'
pro_sign_up_url = "https://www.mathpreppro.com/pro"
unsub_url = "https://www.mathpreppro.com/28b73f87"

def generate_email(template, context, email_title, to_email):
    context['banner_url'] = "".join([host_base_site, "static/images/admin/email_banner.png"]) #"http://jhollier.pythonanywhere.com/static/images/admin/email_banner.png"
    context['front_end_url'] = host_base_site
    context['unsub_url'] = unsub_url
    context['pro_sign_up_url'] = pro_sign_up_url
    context['gif_url'] = "".join([host_base_site, "static/images/admin/giffy.gif"]) #"http://jhollier.pythonanywhere.com/static/images/admin/giffy.gif"
    from_email = 'MathPrepPro <contact@mathpreppro.com>'
    html_message = render_to_string(template,context)
    plain_message = strip_tags(html_message)
    message = EmailMultiAlternatives(email_title, plain_message, from_email, to_email) #(subject, message, from_email, recipient_list)
    message.attach_alternative(html_message, 'text/html')
    return message


### DAILY EMAIL TESTS ###

def daily_email_test(thing_1, thing_2):

    print("Generating context...")

    email_list = []

    for person in thing_1:

        problem_number = 1
        problem_query = models.Problem.objects.get(pk=problem_number)
        email_title = "".join(["Daily Problem - ", str(problem_query.problem_name)])
        to_email = person

        context = {}
        context['problem_statement'] = problem_query.problem_statement
        context['problem_image_url'] = "".join([host_base_site, "static/images/problems/", str(problem_query.pk), "_statement.png"])
        context['video_url'] = problem_query.problem_solution_url
        context['pro'] = thing_2
        context['pk'] = problem_number
        if context['pro']:
            person = User.objects.get(email="mathpreppro@gmail.com")
            token = models.Token.objects.get(user=person)
            token = token.key
            context['solutions_url'] = "".join([host_base_site, "prolist/", token])
            context['pro_detail_url'] = "".join([host_base_site, "prolist/", token, "/", str(problem_number)])

        try:
            email_list.append(generate_email('AppOne/daily_problem.html', context, email_title, [to_email]))
        except:
            print('error')

    get_connection().send_messages(email_list)
    print("Email(s) sent!")

def daily_pro_email_deliverability_test(): # https://www.gmass.co/inbox
    print("Starting test...")
    to_email = ['ajay.silicomm@gmail.com', 'ajaygoel999@gmail.com', 'ajay@parttimesnob.com', 'test@chromecompete.com', 'ajay@ajaygoel.net', 'ajay@gmailgenius.com', 'test@ajaygoel.org', 'me@dropboxslideshow.com', 'test@wordzen.com', 'rajgoel8477@gmail.com', 'briansmith8477@gmail.com', 'ajay@butterclaw.com', 'ajay@madsciencekidz.com', 'ajay@couchlock.com', 'ajay@downfor.io', 'ajay2@ctopowered.com', 'ajay@londelljackson.com', 'ajay@ariellevin.com', 'ajay@iquipu.nl', 'ajay@cryptopolitan.com']
    pro = True
    daily_email_test(to_email, pro)

def daily_sub_email_deliverability_test(): # https://www.gmass.co/inbox
    print("Starting test...")
    to_email = ['ajay.silicomm@gmail.com', 'ajaygoel999@gmail.com', 'ajay@parttimesnob.com', 'test@chromecompete.com', 'ajay@ajaygoel.net', 'ajay@gmailgenius.com', 'test@ajaygoel.org', 'me@dropboxslideshow.com', 'test@wordzen.com', 'rajgoel8477@gmail.com', 'briansmith8477@gmail.com', 'ajay@butterclaw.com', 'ajay@madsciencekidz.com', 'ajay@couchlock.com', 'ajay@downfor.io', 'ajay2@ctopowered.com', 'ajay@londelljackson.com', 'ajay@ariellevin.com', 'ajay@iquipu.nl', 'ajay@cryptopolitan.com']
    pro = False
    daily_email_test(to_email, pro)

def daily_pro_email_to_admin_test():
    print("Starting test...")
    to_email = ['mathpreppro@gmail.com']
    pro = True
    daily_email_test(to_email, pro)

def daily_sub_email_to_admin_test():
    print("Starting test...")
    to_email = ['mathpreppro@gmail.com']
    pro = False
    daily_email_test(to_email, pro)

### PRIOR SOLUTION EMAIL TESTS ###

def prior_solutions_test(thing_1):

    print("Generating context...")

    email_list = []

    for email in thing_1:

        email_title = "MathPrepPro - Prior Solutions"
        to_email = email

        context = {}
        person = User.objects.get(email="mathpreppro@gmail.com")
        token = models.Token.objects.get(user=person)
        token = token.key
        context['solutions_url'] = "".join([host_base_site, "prolist/", token])

        try:
            email_list.append(generate_email('AppOne/welcome_pro.html', context, email_title, [to_email]))
        except:
            continue

    get_connection().send_messages(email_list)
    print("Email(s) sent!")

def prior_solutions_deliverability_test():
    print("Starting test...")
    to_email = ['ajay.silicomm@gmail.com', 'ajaygoel999@gmail.com', 'ajay@parttimesnob.com', 'test@chromecompete.com', 'ajay@ajaygoel.net', 'ajay@gmailgenius.com', 'test@ajaygoel.org', 'me@dropboxslideshow.com', 'test@wordzen.com', 'rajgoel8477@gmail.com', 'briansmith8477@gmail.com', 'ajay@butterclaw.com', 'ajay@madsciencekidz.com', 'ajay@couchlock.com', 'ajay@downfor.io', 'ajay2@ctopowered.com', 'ajay@londelljackson.com', 'ajay@ariellevin.com', 'ajay@iquipu.nl', 'ajay@cryptopolitan.com']
    prior_solutions_test(to_email)


def prior_solutions_to_admin_test():
    print("Starting test...")
    to_email = ['mathpreppro@gmail.com']
    prior_solutions_test(to_email)


if __name__ == '__main__':
    # daily_pro_email_deliverability_test()
    # daily_sub_email_deliverability_test()
    daily_pro_email_to_admin_test()
    # daily_sub_email_to_admin_test()
    # prior_solutions_deliverability_test()
    # prior_solutions_to_admin_test()


### Deliverability results ###

# 2.14.21
#  daily pro email did not make it through the AppRiver filter
#  daily sub email did not make it through the Mimecast filter
