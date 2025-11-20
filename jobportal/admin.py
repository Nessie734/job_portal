from django.contrib import admin
from django.utils.translation import gettext_lazy as _

class JobPortalAdminSite(admin.AdminSite):
    site_header = _("JobPortal Administration")
    site_title = _("JobPortal Admin")
    index_title = _("Welcome to JobPortal Administration")
    
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request)
        
        # Custom ordering for apps
        app_ordering = {
            'auth': 1,  # Users and groups first
            'users': 2,  # Custom users next
            'jobs': 3,   # Jobs and applications
        }
        
        # Sort apps based on custom ordering
        app_list.sort(key=lambda x: app_ordering.get(x['app_label'], 999))
        
        # Sort models within each app
        for app in app_list:
            if app['app_label'] == 'auth':
                app['models'].sort(key=lambda x: 1 if x['object_name'] == 'User' else 2)
            elif app['app_label'] == 'users':
                app['models'].sort(key=lambda x: 1 if x['object_name'] == 'CustomUser' else 2)
            elif app['app_label'] == 'jobs':
                model_ordering = {'Company': 1, 'Job': 2, 'Application': 3, 'Category': 4, 'SavedJob': 5}
                app['models'].sort(key=lambda x: model_ordering.get(x['object_name'], 999))
        
        return app_list

# If you want to use the custom admin site, uncomment below and update urls.py
# admin_site = JobPortalAdminSite(name='jobportal_admin')