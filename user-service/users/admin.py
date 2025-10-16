from django.contrib import admin
from users.models import ClientProfile,AdvocateProfile,AdvocateCase
# Register your models here.

admin.site.register(ClientProfile)
admin.site.register(AdvocateProfile)
admin.site.register(AdvocateCase)

