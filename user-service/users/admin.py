from django.contrib import admin
from users.models import ClientProfile, User,OTP
# Register your models here.

admin.site.register(OTP)
admin.site.register(User)
