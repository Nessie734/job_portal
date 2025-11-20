from django.contrib import admin

# Common app doesn't have models yet, but this file is here for future use
# You can register any common models here when you add them

class CommonAdmin(admin.ModelAdmin):
    """
    Base admin class for common configurations
    """
    list_per_page = 25
    save_on_top = True
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:  # editing an existing object
            return readonly_fields + ('created_at',) if hasattr(obj, 'created_at') else readonly_fields
        return readonly_fields