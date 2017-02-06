from django.views import generic
from braces import views
from django.contrib.auth.forms import PasswordChangeForm
from .forms import ChangePasswordForm
from .models import Person, School, Grade
from django.shortcuts import render, render_to_response, HttpResponse
from django.http import JsonResponse


import logging
from django.core import serializers
from django.core.paginator import Paginator


# Create your views here.


class PersonListView(views.StaffuserRequiredMixin, views.AjaxResponseMixin, generic.ListView):
    """
        Class to list all the persons

        If the user is staff only students will show

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.ListView: Inherits generic.ListView that makes a page representing a list of objects.
        :return: List of person objects
    """

    login_url = '/login'
    template_name = 'administration/person_list.html'

    def post_ajax(self, request, *args, **kwargs):
        """
            Function that checks if the post request is an ajax post and finds the searched for Persons.

            :param self:
                References to the class itself and all it's variables
            :param request:
                The request
            :return: List of person objects
        """
        search_text = request.POST['search_text']
        person_list = Person.objects.filter(username__icontains=search_text)
        return render_to_response('administration/person_ajax.html', {'persons': person_list})

    def get_queryset(self):
        """
           Function that Overrides the default queryset from generic.ListView to get the proper Person object list.

           :param self: References to the class itself and all it's variables
           :return: List of person objects
        """
        if not self.request.user.is_superuser:
            return Person.objects.filter(is_staff=False, is_superuser=False)
        else:
            return Person.objects.all()


class PersonDetailView(views.StaffuserRequiredMixin, generic.DetailView):
    """
        Class to get a specific Person based on the username

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.DetailView: Inherits generic.DetailView that makes a page representing a specific object.
        :return: Person object

    """

    model = Person
    template_name = 'administration/person_detail.html'
    slug_field = "username"


class PersonCreateView(views.StaffuserRequiredMixin,  generic.CreateView):
    """
        Class to create a Person object

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.CreateView: Inherits generic.CreateView that displays a form for creating a object and
            saving the form when validated
    """

    login_url = '/login/'
    is_staff = False
    template_name = 'administration/student_create.html'
    model = Person
    fields = ['username', 'first_name', 'last_name', 'email', 'sex', 'grade']
    success_url = '/administrasjon/brukere'

    def get_initial(self):
        if self.kwargs.get('pk'):
            self.success_url = 'administrasjon/skoler/' + self.kwargs.get('school_pk') + '/klasse/' + \
                               self.kwargs.get('pk')
            return {'grade': self.kwargs.get('pk'),'is_staff': self.is_staff}

    def get_form_class(self):
        if self.request.user.is_superuser:
            self.fields = ['username', 'first_name', 'last_name', 'email', 'sex', 'grade', 'is_staff']
        return super(PersonCreateView, self).get_form_class()

    def form_valid(self, form):
        """
            Function that overrides the default form_valid so that a password and is_staff can be added if
            necessary.

            :param self: References to the class itself and all it's variables.
            :param form: References to the model form.
            :return: The HttpResponse set in success_url.
        """

        person = form.save(commit=False)
        staff = self.request.POST.get('staff')
        if staff:
            person.is_staff = staff
        person.set_password('ntnu123')
        person.save()
        return super(PersonCreateView, self).form_valid(form)


class PersonUpdateView(views.StaffuserRequiredMixin, generic.UpdateView):
    """
        Class to update a Person object based on the username

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in
            as staff
        :param generic.UpdateView: Inherits generic.CreateView that displays a form for updating a specific object and
            saving the form when validated.
        :return: The HttpResponse set in success_url
    """
    template_name = 'administration/student_create.html'
    login_url = '/login'
    model = Person
    slug_field = "username"
    fields = ['first_name', 'last_name', 'email', 'sex', 'grade']


class SchoolListView(views.StaffuserRequiredMixin, generic.ListView):
    """
        Class to list out all School objects

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.ListView: Inherits generic.ListView that represents a page containing a list of objects
        :return: List of School objects

    """
    login_url = '/login'
    model = School
    template_name = 'administration/school_list.html'
    paginate_by = 20


class SchoolDetailView(views.StaffuserRequiredMixin, generic.DetailView):
    """
        Class to get a specific Person based on the username

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.UpdateView: Inherits generic.DetailView that makes a page representing a specific object.
        :return: School object

    """
    model = School
    template_name = 'administration/school_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SchoolDetailView, self).get_context_data(**kwargs)
        context['grades'] = Grade.objects.filter(school_id=self.kwargs['pk'])
        return context


class SchoolCreateView(views.SuperuserRequiredMixin, generic.CreateView):
    """
        Class to create a School object

        :param views.SuperuserRequiredMixin: Inherits views.SuperuserRequiredMixin that checks if the user is logged in as a
            superuser
        :param generic.CreateView: Inherits generic.CreateView that displays a form for creating a object and
            saving the form when validated
        :return: The HttpResponse set in success_url
    """
    login_url = '/login'
    template_name = 'administration/school_form.html'
    model = School
    fields = ['school_name', 'school_address']
    success_url = '/administration/allschools/'


class SchoolUpdateView(views.SuperuserRequiredMixin, generic.UpdateView):
    """
        Class to update a School object based on the school.id

        :param views.SuperuserRequiredMixin: Inherits views.SuperuserRequiredMixin that checks if the user is logged in as a
            superuser
        :param generic.UpdateView: Inherits generic.CreateView that displays a form for updating a object and
            saving the form when validated.
        :return: The HttpResponse set in success_url
    """
    login_url = '/login'
    model = School
    template_name = 'administration/school_form.html'
    fields = ['school_name', 'school_address']


class GradeDetailView(views.StaffuserRequiredMixin, generic.DetailView):
    """
        Class to get a specific Grade based on the grade.id

        :param views.StaffuserRequiredMixin: Inherits views.StaffuserRequiredMixin that checks if the user is logged in as staff
        :param generic.UpdateView: Inherits generic.DetailView that makes a page representing a specific object.
        :return: School object

    """
    login_url = '/login'
    model = Grade
    template_name = 'administration/grade_detail.html'

    def get_context_data(self, **kwargs):
        context = super(GradeDetailView, self).get_context_data(**kwargs)
        context['students'] = Person.objects.filter(grade_id=self.kwargs['pk'], is_staff=False)
        context['teachers'] = Person.objects.filter(grade_id=self.kwargs['pk'], is_staff=True)
        return context


class GradeCreateView(views.SuperuserRequiredMixin, generic.CreateView):
    """
        Class to create a Grade object

        :param views.SuperuserRequiredMixin: Inherits views.SuperuserRequiredMixin that checks if the user is logged in as a
            superuser
        :param generic.CreateView: Inherits generic.CreateView that displays a form for creating a object and
            saving the form when validated
        :return: The HttpResponse set in success_url
    """
    login_url = '/login'
    model = Grade
    template_name = 'administration/grade_form.html'
    fields = ['grade_name', 'tests']

    def form_valid(self, form):
        grade = form.save(commit=False)
        grade.school_id = self.kwargs['pk']
        grade.save()

        return super(GradeCreateView, self).form_valid(form)


class GradeUpdateView(views.SuperuserRequiredMixin, generic.UpdateView):
    login_url = '/login'
    model = Grade
    template_name = 'administration/grade_form.html'
    fields = ['grade_name', 'tests']




