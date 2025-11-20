from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('<int:job_id>/save/', views.save_job, name='save_job'),
    path('<int:job_id>/unsave/', views.unsave_job, name='unsave_job'),
    path('create/', views.create_job, name='create_job'),
    path('<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('<int:job_id>/toggle-status/', views.toggle_job_status, name='toggle_job_status'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('companies/manage/', views.manage_companies, name='manage_companies'),# Add this line

#adding applicant_notification urls
path('job/<int:job_id>/applicants/', views.view_applicants, name='view_applicants'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('application/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('employer/notifications/', views.employer_notifications, name='employer_notifications'),
    path('notification/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),

]