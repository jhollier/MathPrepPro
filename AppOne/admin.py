from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from . import models

################################# Problems #####################################

class ProblemAdmin(admin.ModelAdmin): # This class is ONLY used for customizing the admin interface for this model
    # fields = ['field1', 'field2', etc] #This reorders the fields and is not needed. The deault order is the order in which the appear in the model class
    readonly_fields = ('id','creation_date') #displays the id on the object instance page, locks me from being able to modify the creation date
    search_fields = ['problem_name', 'problem_statement','id'] # Adds a search bar to the admin list view
    list_filter = ['problem_type'] # Adds filters on the right side of the model view
    list_display = ['problem_name','problem_type','creation_date','id'] # Fields shown on the admin list page which can be sorted! Default is first field only

admin.site.register(models.Problem, ProblemAdmin)

############################## UsersProfileInfo ################################

class UserProfileInfoAdmin(admin.ModelAdmin):
    list_display = ['username','email','problem_number','pro']

    def username(self, x):
        return x.user.username
    def email(self, x):
        return x.user.email

admin.site.register(models.UserProfileInfo, UserProfileInfoAdmin)

###################################### User ####################################

# This inline class injects the UserProfileInfo fields that are not one-to-one
# into the User admin detail page and they can be edited from there
class UserProfileInfoInline(admin.StackedInline):
    model = models.UserProfileInfo

class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInfoInline]
    #Could not figure out how to show the 'problem_number from the inline class on the admin list page for Users...'
    list_display = ['username','email','first_name','last_name','is_staff','date_joined']

admin.site.unregister(User)
admin.site.register(User,UserAdmin)
