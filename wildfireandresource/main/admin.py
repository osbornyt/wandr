from django.contrib import admin

# Register your models here.
from .models import Form, UserForm, AnswerField, Vendor

admin.site.register(Form)
admin.site.register(UserForm)
admin.site.register(AnswerField)
admin.site.register(Vendor)
