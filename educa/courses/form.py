# from django import forms
from .models import Courses, Module
from django.forms.models import inlineformset_factory

ModuleFormSet = inlineformset_factory(Courses, Module, fields=('title', 'description'), extra=2, can_delete=True)
