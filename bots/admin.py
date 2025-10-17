from django.contrib import admin
from .models import Command, Raspberry, History

admin.site.register(Command)
admin.site.register(Raspberry)
admin.site.register(History)
