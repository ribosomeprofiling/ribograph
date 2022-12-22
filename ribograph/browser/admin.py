from django.contrib import admin

from .models import Experiment, Project, Reference

my_models = [Experiment, Project, Reference]

for m in my_models:
    admin.site.register(m)
