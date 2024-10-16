from django.contrib import admin
from django.utils import timezone
from .models import Profile, RoleChangeRequest


class ProfileAdmin(admin.ModelAdmin):
    """
    Profile admin display options.
    """
    list_display = ('user', 'role')


class RoleChangeRequestAdmin(admin.ModelAdmin):
    """
    Role change request admin display options.
    Updates RoleChangeRequest objects based on admin's actions.
    Updates user's profile role if approved.
    """
    list_display = (
        'user',
        'charity_name',
        'charity_registration_number',
        'charity_website',
        'charity_description',
        'status'
        )
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        """
        Sets request status to approved and updates user role.
        """
        for request in queryset:
            request.status = 'approved'
            request.save()
            # Update the user's role
            request.user.profile.role = 'shelter_admin'
            request.user.profile.save()

    def reject_requests(self, request, queryset):
        """
        Sets request status to rejected.
        """
        for request in queryset:
            request.status = 'rejected'
            request.save()


admin.site.register(Profile, ProfileAdmin)
admin.site.register(RoleChangeRequest, RoleChangeRequestAdmin)
