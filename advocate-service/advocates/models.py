# advocates/models.py
from django.db import models
from django.utils import timezone

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20)

    class Meta:
        db_table = "users"
        managed = False

    def __str__(self):
        return f"{self.username} ({self.role})"



class Specialization(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        db_table = "advocate_specialization"

    def __str__(self):
        return self.name


class AdvocateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="advocate_profile")
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    bar_council_id = models.CharField(max_length=100, unique=True)
    enrollment_year = models.IntegerField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    languages = models.CharField(max_length=255, blank=True, null=True)  # comma separated
    specializations = models.ManyToManyField(Specialization, related_name="advocates", blank=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    state = models.CharField(max_length=120, blank=True, null=True)
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

    def __str__(self):
        return f"{self.full_name or self.user.username}"


class AdvocateTeam(models.Model):
    lead = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lead_teams")
    members = models.ManyToManyField(User, related_name="teams", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "advocate_team"

    def __str__(self):
        return f"Team led by {self.lead.username}"


class TeamMember(models.Model):
    team = models.ForeignKey(AdvocateTeam, on_delete=models.CASCADE, related_name="team_memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "team_member"
        unique_together = ("team", "user")




