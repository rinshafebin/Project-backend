# advocates/admin.py
from django.contrib import admin
from .models import User, Specialization, AdvocateProfile, AdvocateTeam, TeamMember


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "role")
    search_fields = ("username", "email", "role")
    readonly_fields = ("id", "username", "email", "role")

    def has_add_permission(self, request):
        return False  

    def has_delete_permission(self, request, obj=None):
        return False  


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)



@admin.register(AdvocateProfile)
class AdvocateProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "bar_council_id", "is_verified", "rating", "cases_count", "wins_count")
    search_fields = ("full_name", "user__username", "bar_council_id")
    list_filter = ("is_verified",)
    filter_horizontal = ("specializations",)
    readonly_fields = ("cases_count", "wins_count", "created_at", "updated_at")



class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1  # number of extra forms
    autocomplete_fields = ("user",)


@admin.register(AdvocateTeam)
class AdvocateTeamAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "created_at")
    search_fields = ("lead__username",)
    inlines = [TeamMemberInline]



@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("team", "user", "joined_at")
    search_fields = ("team__lead__username", "user__username")
