from django.contrib import admin
from .models import Company, Job, Application, Category, SavedJob

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'created_at', 'job_count')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'website')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'website', 'logo')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def job_count(self, obj):
        return obj.job_set.count()
    job_count.short_description = 'Total Jobs'

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'employer', 'location', 'job_type', 'experience_level', 'salary', 'is_active', 'created_at')
    list_filter = ('job_type', 'experience_level', 'is_active', 'created_at', 'application_deadline')
    search_fields = ('title', 'description', 'requirements', 'company__name', 'employer__username')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company', 'employer', 'description', 'requirements')
        }),
        ('Job Details', {
            'fields': ('location', 'job_type', 'experience_level', 'salary', 'application_deadline')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company', 'employer')
    
    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = 'Applications'

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'applied_date', 'cover_letter_preview')
    list_filter = ('status', 'applied_date', 'job__company')
    search_fields = ('applicant__username', 'job__title', 'cover_letter', 'notes')
    readonly_fields = ('applied_date',)
    list_editable = ('status',)
    date_hierarchy = 'applied_date'
    
    fieldsets = (
        ('Application Details', {
            'fields': ('job', 'applicant', 'cover_letter', 'resume', 'status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('applied_date',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job', 'applicant', 'job__company')
    
    def cover_letter_preview(self, obj):
        return obj.cover_letter[:50] + '...' if obj.cover_letter and len(obj.cover_letter) > 50 else obj.cover_letter
    cover_letter_preview.short_description = 'Cover Letter'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if obj.description and len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_date')
    list_filter = ('saved_date',)
    search_fields = ('user__username', 'job__title')
    readonly_fields = ('saved_date',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'job')