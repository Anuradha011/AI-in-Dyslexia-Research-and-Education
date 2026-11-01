from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StudentProfile, ParentStudentRequest

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username','email','role','is_approved','created_at']
    list_filter = ['role']
    fieldsets = UserAdmin.fieldsets + (('Extra', {'fields': ('role','institution','phone','is_approved','preferred_language','profile_pic')}),)

admin.site.register(StudentProfile)


@admin.register(ParentStudentRequest)
class ParentStudentRequestAdmin(admin.ModelAdmin):
    list_display = ['parent', 'student', 'status', 'created_at', 'reviewed_by', 'reviewed_at']
    list_filter = ['status']
    search_fields = ['parent__username', 'student__username']
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for req in queryset.filter(status='pending'):
            req.status = 'approved'
            req.reviewed_by = request.user
            req.reviewed_at = timezone.now()
            req.save()
            profile, _ = StudentProfile.objects.get_or_create(user=req.student)
            profile.parent = req.parent
            profile.save()
            updated += 1
        self.message_user(request, f"{updated} request(s) approved.")
    approve_requests.short_description = "Approve selected parent requests"

    def reject_requests(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for req in queryset.filter(status='pending'):
            req.status = 'rejected'
            req.reviewed_by = request.user
            req.reviewed_at = timezone.now()
            req.save()
            updated += 1
        self.message_user(request, f"{updated} request(s) rejected.")
    reject_requests.short_description = "Reject selected parent requests"