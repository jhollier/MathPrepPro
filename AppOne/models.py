from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from pathlib import Path
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

################################################################################

# All code supporting the ImageFields have been commented out. Apparently is it
# better to server static images from a static folder rather than in the database.
# https://docs.djangoproject.com/en/3.1/howto/static-files/deployment/

# upload_to passes two arguments but I don't need the second...not sure what the best
# proactice is here for not using the second one...

problem_location = ''.join([str(Path(__file__).resolve().parent.parent),'\\static\\images\\problems\\'])
solution_location = '' # DELETE

class Problem(models.Model):
    problem_name = models.CharField(max_length=250)
    problem_statement = models.TextField(max_length=5000)
    problem_statement_image = models.ImageField(upload_to=problem_location, null=True, blank=True)
    problem_solution = models.CharField(max_length=500)
    # problem_solution_image = models.ImageField(upload_to=solution_location, null=True, blank=True) # DEPLOYMENT DELETE
    problem_type = models.CharField(max_length=250)
    creation_date = models.DateField(auto_now=False,auto_now_add=True)
    problem_solution_url = models.CharField(max_length=500, null=True, blank=True)

    # This is to delete an image if one already exists for both image fields: https://stackoverflow.com/questions/4394194/replacing-a-django-image-doesnt-delete-original
    def save(self, *args, **kwargs):
        # delete old file when replacing by updating the file
        try:
            this = Problem.objects.get(id=self.id)
            if this.problem_statement_image != self.problem_statement_image:
                this.problem_statement_image.delete(save=False)
        except:
            pass # when new photo then we do nothing, normal case
        super(Problem, self).save(*args, **kwargs)

    def __str__(self):
        return self.problem_name

    # The ProblemCreateView needs this function in order to redirect to something
    # In this case, we want to redirect to the newly created detail page
    def get_absolute_url(self):
        return reverse('detail',kwargs={'pk':self.pk})

################################################################################

# Extending the default User model to contain additional fields
class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # https://github.com/skorokithakis/django-annoying#autoonetoonefield

    problem_number = models.IntegerField(default=1)
    pro = models.BooleanField(default=False)

    def next_problem_number(self):
        print('Old problem number is ' + str(self.problem_number))
        self.problem_number +=1
        print('New problem number is ' + str(self.problem_number))

    def __str__(self):
        return self.user.username

# https://stackoverflow.com/questions/1652550/can-django-automatically-create-a-related-one-to-one-model
# https://stackoverflow.com/questions/5608001/create-onetoone-instance-on-model-creation
# This checks to see when a user is created. It automatically creates a UserProfileInfo instance as well.
# The default problem_number will be 1!
#
# I tried to use the AutoOneToOneFild here but it didn't work... https://github.com/skorokithakis/django-annoying#autoonetoonefield

# Creates a UserProfileInfo instance when a new User is added to the db
@receiver(post_save, sender=User)
def create_modelb(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance, 'UserProfileInfo'):
            UserProfileInfo.objects.create(user=instance)

# Creates a token when a new User is added to the db
# Not entirely sure what the arguments should really be or if it matters...
# https://www.youtube.com/watch?v=Wq6JqXqOzCE
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)
