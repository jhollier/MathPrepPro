import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','MathPrepPro.settings')
import django
django.setup()
################################################################################
from AppOne import models

def update_problem_number():
    primary_keys = []

    # old_problem_number_list = []
    # new_problem_number_list = []

    for obj in models.Problem.objects.order_by('pk'):
        primary_keys.append(obj.pk)

    user_query = models.UserProfileInfo.objects.order_by('problem_number')
    for obj in user_query:
        a = obj.problem_number
        # old_problem_number_list.append(a) # for debugging only
        a += 1 # itterate to next pk

        if a > primary_keys[-1]:
            # notify_admin() # Could insert a function here that would email me if I am delinquent on problems...
            continue

        while a not in primary_keys: # Find the next problem pk
            a +=1

        obj.problem_number = a
        obj.save()

        # new_problem_number_list.append(a) # for debuggin only

if __name__ == '__main__':

    update_problem_number()
