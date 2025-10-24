from django.contrib import admin
from users.models import ClientProfile,AdvocateProfile,OTP
# Register your models here.

admin.site.register(ClientProfile)
admin.site.register(AdvocateProfile)
admin.site.register(OTP)

