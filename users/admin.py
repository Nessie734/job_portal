from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, JobSeekerProfile, EmployerProfile

class JobSeekerProfileInline(admin.StackedInline):
    model = JobSeekerProfile
    can_delete = False
    verbose_name_plural = 'Job Seeker Profile'
    fk_name = 'user'

class EmployerProfileInline(admin.StackedInline):
    model = EmployerProfile
    can_delete = False
    verbose_name_plural = 'Employer Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture')}),
        (_('User Type'), {'fields': ('user_type',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'password1', 'password2'),
        }),
    )
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        
        if obj.user_type == 'job_seeker':
            return [JobSeekerProfileInline(self.model, self.admin_site)]
        elif obj.user_type == 'employer':
            return [EmployerProfileInline(self.model, self.admin_site)]
        return list()

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'skills_preview', 'experience_preview', 'education_preview')
    list_filter = ('user__date_joined',)
    search_fields = ('user__username', 'user__email', 'skills', 'experience', 'education')
    readonly_fields = ('user',)
    
    def skills_preview(self, obj):
        return obj.skills[:50] + '...' if obj.skills and len(obj.skills) > 50 else obj.skills
    skills_preview.short_description = 'Skills'
    
    def experience_preview(self, obj):
        return obj.experience[:50] + '...' if obj.experience and len(obj.experience) > 50 else obj.experience
    experience_preview.short_description = 'Experience'
    
    def education_preview(self, obj):
        return obj.education[:50] + '...' if obj.education and len(obj.education) > 50 else obj.education
    education_preview.short_description = 'Education'

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'company_website', 'company_size', 'industry')
    list_filter = ('company_size', 'industry', 'user__date_joined')
    search_fields = ('user__username', 'company_name', 'industry', 'company_description')
    readonly_fields = ('user',)
    
    def company_name_preview(self, obj):
        return obj.company_name[:50] + '...' if obj.company_name and len(obj.company_name) > 50 else obj.company_name
    company_name_preview.short_description = 'Company Name'

# Register the custom user model
admin.site.register(CustomUser, CustomUserAdmin)