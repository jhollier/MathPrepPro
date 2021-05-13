from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from . import models
from selenium import webdriver
from pathlib import Path
from django.contrib.sites.shortcuts import get_current_site
from os import path as image_check
from rest_framework.authtoken.models import Token

################################################################################
############################ General Views #####################################
################################################################################

def index(request):
    response = redirect('https://www.mathpreppro.com')
    return response

def home(request):
    return render(request, 'AppOne/home.html')

################################################################################
############################## PRO CBVs ########################################
################################################################################

class ProListView(ListView): # No login is required but you must have the Token specific url to access a person's list.
    model = models.Problem
    template_name = 'AppOne/pro_list.html'
    context_object_name = 'problem_list'

    def get_queryset(self):
        # user_email = self.kwargs['email']
        # user_obj = models.UserProfileInfo.objects.get(user = models.User.objects.get(email__istartswith = user_email)) #could do the starts with filter here??? https://docs.djangoproject.com/en/3.1/ref/models/querysets/
        user_token = self.kwargs['token'] # var from url
        user_obj = Token.objects.get(key=user_token)
        user_obj = user_obj.user
        user_obj = models.UserProfileInfo.objects.get(user=user_obj)
        user_prob = user_obj.problem_number
        problem_count = models.Problem.objects.filter(pk__lte = user_prob).count() # https://docs.djangoproject.com/en/3.1/ref/models/querysets/
        return models.Problem.objects.all()[:problem_count]

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user_token = self.kwargs['token'] # var from url
        user_obj = Token.objects.get(key=user_token)
        user_obj = user_obj.user
        user_obj = models.UserProfileInfo.objects.get(user=user_obj)
        context['pro'] = user_obj.pro
        context['token'] = user_token
        context['banner_url'] = "http://jhollier.pythonanywhere.com/static/images/admin/email_banner.png"
        return context

class ProDetailView(DetailView):
    fields = '__all__'
    model = models.Problem
    template_name = 'AppOne/pro_detail.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs) #This passess the kwargs up to the inherited class

        user_token = self.kwargs['token'] # var from url
        user_obj = Token.objects.get(key=user_token)
        user_obj = user_obj.user
        user_obj = models.UserProfileInfo.objects.get(user=user_obj)
        context['pro'] = user_obj.pro
        context['token'] = user_token
        context['show_problem'] = False
        if self.object.pk <= user_obj.problem_number: # Is someone trying to look at problem detail pages when they aren't on their list?
            context['show_problem'] = True
        context['problem_name'] = self.object.problem_name
        context['problem_statement'] = self.object.problem_statement
        context['problem_answer'] = self.object.problem_solution
        context['problem_solution_url'] = self.object.problem_solution_url
        context['pk'] = self.object.pk
        context['banner_url'] = "http://jhollier.pythonanywhere.com/static/images/admin/email_banner.png"
        full_image_dir = ''.join([str(Path(__file__).resolve().parent.parent),'/static/images/problems/',str(self.object.pk),'_image.png'])
        if image_check.exists(full_image_dir):
            context['image_dir'] = ''.join(['/images/problems/',str(self.object.pk),'_image.png'])
        return context

################################################################################
######################## Backend problem CBVs ##################################
################################################################################

class ProblemListView(ListView):
    context_object_name = 'problem_list' #If we do not set this, the default context will be '<model>_list' so in this case 'problem_list'
    model = models.Problem

class ProblemDetailView(DetailView):
    # context_object_name = 'problem_detail' #If we do not set this, the default context will be '<model name>' so in this case 'problem'
    fields = '__all__'
    model = models.Problem
    template_name = 'AppOne/problem_detail.html'

    def get_context_data(self,**kwargs):
            context = super().get_context_data(**kwargs) #This passess the kwargs up to the inherited class
            context['problem_name'] = self.object.problem_name
            context['problem_statement'] = self.object.problem_statement
            context['problem_answer'] = self.object.problem_solution
            context['pk'] = self.object.pk

            # Does a problem image exist? If so, assign it to the context so it can be used in a template tag
            full_image_dir = ''.join([str(Path(__file__).resolve().parent.parent),'/static/images/problems/',str(self.object.pk),'_image.png'])
            if image_check.exists(full_image_dir):
                context['image_dir'] = ''.join(['/images/problems/',str(self.object.pk),'_image.png'])

            return context

default_problem_statement_data = """<h5>Insert Problem Statement Here</h5>
<br>
<p>A) \(A\) </p>
<p>B) \(B\) </p>
<p>C) \(C\) </p>
<p>D) \(D\)</p>"""

class ProblemCreateView(CreateView):
    fields = ['problem_name','problem_statement','problem_solution','problem_type']# We want to be able to edit all the fields but I could change to ('<field1>, <field2>, etc')
    model = models.Problem
    # template_name = 'AppOne/problem_form' # The default template_name is '<model>_form' so we don't even need this unless we want to change it

    # Defining the default html formating I want in the creation form
    def get_initial(self,**kwargs):
        initial = super().get_initial(**kwargs)

        initial['problem_statement'] = default_problem_statement_data #See VARS
        return initial

class ProblemUpdateView(UpdateView):
    fields = '__all__'
    model = models.Problem

    # Injecting a context dictionary to be called by the html. For the UpdateView template, the default object that is passed is 'form'
    # Calling this gives some weird formated shit. We need to define another context with data from the model instance.
    def get_context_data(self,**kwargs):
            context = super().get_context_data(**kwargs) #This passess the kwargs up to the inherited class
            context['problem_name'] = self.object.problem_name
            context['problem_statement'] = self.object.problem_statement
            context['problem_answer'] = self.object.problem_solution
            context['pk'] = self.object.pk

            # Does a problem image exist? If so, assign it to the context so it can be used in a template tag
            full_image_dir = ''.join([str(Path(__file__).resolve().parent.parent),'/static/images/problems/',str(self.object.pk),'_image.png'])
            if image_check.exists(full_image_dir):
                context['image_dir'] = ''.join(['images/problems/',str(self.object.pk),'_image.png'])

            return context

    # By default, the success url looks the be the previous page...I think
    # This allows us to basically sumbit and refresh so we can instantly see the new data
    def get_success_url(self):
        problempk = self.kwargs['pk']
        return reverse_lazy('update', kwargs={'pk':problempk})

    def form_valid(self, form):
        response = super(ProblemUpdateView, self).form_valid(form)

        ################################################################################
        ### Redefining this function to add screenshot functionality when sumbitted. ###
        ###                                                                          ###
        ### This functionality is going to be depricated from deployment for now.    ###
        ### Images will be created locally and uploaded seperately for now.          ###
        ###                                                                          ###
        ################################################################################

        ### LOCAL ONLY CODE ###

        # number=str(self.object.pk)
        # with webdriver.Chrome() as driver:
        #     url = "".join(['http://',get_current_site(self.request).domain,'/prolist/da747e06c9fd8e1a4b33c9b8aad1f05ba94eedab/',number,'/']) # Option 1 to grab Admin prolist detail
        #     # url = "".join(['http://',get_current_site(self.request).domain,self.object.get_absolute_url()]) # This interestingly returns domain/list/1/
        #     # url = self.request.build_absolute_uri() # Option 2
        #     driver.get(url)
        #     driver.implicitly_wait(3)
        #     element = driver.find_element_by_id('screenshot') # Methods to find web elements: https://chercher.tech/python/webelement-locator
        #     SCREENSHOT_DIR = str(Path(__file__).resolve().parent.parent)
        #     element.screenshot(SCREENSHOT_DIR + "/static/images/problems/" + number + "_statement.png") # This will replace an image if one already exists with that name

        ### DEV CODE FOR TAKING THE SCREENSHOTS ON PYTHONANYWHERE.COM SERVER - DOES NOT WORK WELL ###

        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-gpu")
        # driver = webdriver.Chrome(options=chrome_options)
        # with webdriver.Chrome(options=chrome_options) as driver:
        #     number=str(self.object.pk)
        #     url = "".join(['http://', get_current_site(self.request).domain, '/update/', number, '/'])
        #     driver.implicitly_wait(3)
        #     driver.get(url)
        #     element = driver.find_element_by_id('screenshot') #Use with free account
        #     SCREENSHOT_DIR = str(Path(__file__).resolve().parent.parent)
        #     element.screenshot(SCREENSHOT_DIR + "/static/images/problems/" + number + "_statement.png")
        #     driver.quit() # Seems to run better with this....

        return response

class ProblemDeleteView(DeleteView):
    model = models.Problem
    # template_name = 'AppOne/problem_confirm_delete' # Default Value
    # context_object_name = 'problem' # Default Value
    success_url = reverse_lazy('problem_list')
    # https://stackoverflow.com/questions/48669514/difference-between-reverse-and-reverse-lazy-in-django
    # When using a class, we must use reverse_lazy() since class based attributes are evaluated on Import which is before the urls patterns are loaded
    # When using a def (function), we can use reverse() since that is evaluated only when called which is after the url patterns are loaded
