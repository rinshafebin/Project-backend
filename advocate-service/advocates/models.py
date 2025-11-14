from django.db import models
from django.conf import settings
from django.utils import timezone

class UserProxy(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=150)
    email = models.EmailField()
    role = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = "users"
        managed = False
        

class AdvocateProfile(models.Model):
    user = models.OneToOneField(UserProxy, on_delete=models.CASCADE, related_name="advocate_profile")
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    bar_council_id = models.CharField(max_length=100, unique=True)
    enrollment_year = models.IntegerField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    languages = models.CharField(max_length=255, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to="advocates/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    cases_count = models.IntegerField(default=0)
    wins_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "advocate_profile"
        indexes = [models.Index(fields=["bar_council_id"]), models.Index(fields=["user"])]
        
        def __str__(self):
            return self.full_name or str(self.user.username)


class Specialization(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        db_table = "advocate_specialization"

        def __str__(self):
            return self.name

class AdvocateSpecialization(models.Model):
    advocate = models.ForeignKey(AdvocateProfile, on_delete=models.CASCADE, related_name="specializations")
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)

    class Meta:
        db_table = "advocate_advocatespecialization"
        unique_together = ("advocate", "specialization")


class AdvocateTeam(models.Model):
    lead = models.ForeignKey(AdvocateProfile, on_delete=models.CASCADE, related_name="lead_teams")
    members = models.ManyToManyField(AdvocateProfile, related_name="teams", blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "advocate_team"

        def __str__(self):
            return f"Team led by {self.lead.full_name}"


class TeamMember(models.Model):
    team = models.ForeignKey(AdvocateTeam, on_delete=models.CASCADE, related_name="team_members")
    advocate = models.ForeignKey(AdvocateProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default="Junior")

    class Meta:
        db_table = "advocate_team_member"
        unique_together = ("team", "advocate")

        def __str__(self):
            return f"{self.advocate} in {self.team} as {self.role}"



