from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from jobs.models import Job, Application, SavedJob, Company,Notification
from django.contrib.auth import get_user_model

User = get_user_model()

def home(request):
    # Show recent jobs on home page
    recent_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:6]
    context = {'recent_jobs': recent_jobs}
    return render(request, 'common/home.html', context)

@login_required
def dashboard(request):
    user_type = request.user.user_type
    context = {'user_type': user_type}
    
    if user_type == 'job_seeker':
        # Job seeker dashboard
        applications = Application.objects.filter(applicant=request.user).select_related('job').order_by('-applied_date')[:5]
        saved_jobs_count = SavedJob.objects.filter(user=request.user).count()
        context.update({
            'recent_applications': applications,
            'saved_jobs_count': saved_jobs_count,
        })
        template = 'common/job_seeker_dashboard.html'
    elif user_type == 'employer':
        # Employer dashboard
        jobs = Job.objects.filter(employer=request.user).order_by('-created_at')
        recent_jobs = jobs[:5]
        total_applications = Application.objects.filter(job__employer=request.user).count()
        active_jobs = jobs.filter(is_active=True).count()
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        # Add applicant statistics
        applicant_stats = Application.objects.filter(
            job__employer=request.user
        ).values('status').annotate(count=Count('status'))
        
        context.update({
            'recent_jobs': recent_jobs,
            'total_applications': total_applications,
            'active_jobs': active_jobs,
            'applicant_stats': applicant_stats,
            'unread_count': unread_count,
        })
        template = 'common/employer_dashboard.html'
    else:  # admin
        # Admin dashboard statistics
        today = timezone.now()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Basic counts
        total_users = User.objects.count()
        total_jobs = Job.objects.count()
        total_applications = Application.objects.count()
        total_companies = Company.objects.count()
        
        # User statistics
        job_seekers = User.objects.filter(user_type='job_seeker').count()
        employers = User.objects.filter(user_type='employer').count()
        admins = User.objects.filter(user_type='admin').count()
        
        # Recent activity
        new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
        new_jobs_week = Job.objects.filter(created_at__gte=week_ago).count()
        new_applications_week = Application.objects.filter(applied_date__gte=week_ago).count()
        
        # Job statistics
        active_jobs = Job.objects.filter(is_active=True).count()
        expired_jobs = Job.objects.filter(application_deadline__lt=today).count()
        
        # Application status breakdown
        application_status = Application.objects.values('status').annotate(count=Count('status'))
        
        # Recent users (last 5)
        recent_users = User.objects.select_related('jobseekerprofile', 'employerprofile').order_by('-date_joined')[:5]
        
        # Recent jobs (last 5)
        recent_jobs = Job.objects.select_related('company', 'employer').order_by('-created_at')[:5]
        
        # Recent applications (last 5)
        recent_applications = Application.objects.select_related('job', 'applicant').order_by('-applied_date')[:5]
        
        # System health (placeholder values)
        system_status = 'Healthy'
        database_size = '2.5 MB'
        uptime = '99.8%'
        
        context.update({
            # Basic counts
            'total_users': total_users,
            'total_jobs': total_jobs,
            'total_applications': total_applications,
            'total_companies': total_companies,
            
            # User breakdown
            'job_seekers': job_seekers,
            'employers': employers,
            'admins': admins,
            
            # Recent activity
            'new_users_week': new_users_week,
            'new_jobs_week': new_jobs_week,
            'new_applications_week': new_applications_week,
            
            # Job statistics
            'active_jobs': active_jobs,
            'expired_jobs': expired_jobs,
            
            # Application statistics
            'application_status': application_status,
            
            # Recent data
            'recent_users': recent_users,
            'recent_jobs': recent_jobs,
            'recent_applications': recent_applications,
            
            # System info
            'system_status': system_status,
            'database_size': database_size,
            'uptime': uptime,
            'today': today,
        })
        template = 'common/admin_dashboard.html'
    
    return render(request, template, context)