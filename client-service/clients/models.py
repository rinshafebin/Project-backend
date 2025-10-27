from django.db import models

class User(models.Model):
    role = models.CharField(max_length=20)

    class Meta:
        db_table = 'users'
        managed = False


class AdvocateProfile(models.Model):
    class Meta:
        db_table = 'advocate_profile'
        managed = False
