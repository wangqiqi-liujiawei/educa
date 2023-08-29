# from django.test import TestCase
from django.contrib.auth.models import User
from courses.models import Subject, Courses, Module

# Create your tests here.
user = User.objects.last()
subject = Subject.objects.last()
c1 = Courses.objects.create(subject=subject, owner=user, title='Courses1', slug='courses1')
c2 = Courses.objects.create(subject=subject, owner=user, title='Courses2', slug='courses2')
m1 = Module.objects.create(course=c1, title='Module 1')
m2 = Module.objects.create(couse=c1, title='Module 2')
m1.order()
