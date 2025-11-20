from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from .models import Job, Application, Company, SavedJob
from .forms import JobForm, ApplicationForm, CompanyForm, JobSearchForm

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Notification

# All your view functions remain the same, they'll automatically use the custom user model

def job_list(request):
    jobs = Job.objects.filter(is_active=True, application_deadline__gt=timezone.now())
    
    # Search and filtering
    form = JobSearchForm(request.GET or None)
    if form.is_valid():
        query = form.cleaned_data.get('query')
        location = form.cleaned_data.get('location')
        job_type = form.cleaned_data.get('job_type')
        experience_level = form.cleaned_data.get('experience_level')
        
        if query:
            jobs = jobs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(company__name__icontains=query) |
                Q(requirements__icontains=query)
            )
        if location:
            jobs = jobs.filter(location__icontains=location)
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        if experience_level:
            jobs = jobs.filter(experience_level=experience_level)
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'search_query': request.GET.get('query', ''),
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    has_applied = False
    is_saved = False
    
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
        is_saved = SavedJob.objects.filter(job=job, user=request.user).exists()
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'is_saved': is_saved,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if user is job seeker
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Only job seekers can apply for jobs.')
        return redirect('job_detail', job_id=job_id)
    
    # Check if already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', job_id=job_id)
    
    # Check if deadline passed
    if job.is_expired():
        messages.error(request, 'The application deadline for this job has passed.')
        return redirect('job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('job_detail', job_id=job_id)
    else:
        form = ApplicationForm()
    
    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'jobs/apply_job.html', context)

@login_required
def create_job(request):
    if request.user.user_type != 'employer':
        messages.error(request, 'Only employers can post jobs.')
        return redirect('home')
    
    # Check if employer has a company, if not create one
    if not hasattr(request.user, 'employerprofile'):
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('profile')
    
    # Get or create company for the employer
    company, created = Company.objects.get_or_create(
        name=request.user.employerprofile.company_name,
        defaults={
            'description': request.user.employerprofile.company_description or f"Company profile for {request.user.employerprofile.company_name}",
            'website': request.user.employerprofile.company_website or '',
        }
    )
    
    if request.method == 'POST':
        form = JobForm(request.POST, employer=request.user)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('employer_dashboard')
    else:
        # Pre-fill the company field
        form = JobForm(employer=request.user)
        form.fields['company'].initial = company
    
    context = {
        'form': form,
        'title': 'Post New Job',
        'company': company,
    }
    return render(request, 'jobs/job_form.html', context)

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job, employer=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('employer_dashboard')
    else:
        form = JobForm(instance=job, employer=request.user)
    
    context = {
        'form': form,
        'title': 'Edit Job',
        'job': job,
    }
    return render(request, 'jobs/job_form.html', context)

@login_required
def toggle_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    job.is_active = not job.is_active
    job.save()
    
    status = "activated" if job.is_active else "deactivated"
    messages.success(request, f'Job {status} successfully!')
    return redirect('employer_dashboard')

@login_required
def employer_dashboard(request):
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    jobs = Job.objects.filter(employer=request.user).order_by('-created_at')
    total_applications = Application.objects.filter(job__employer=request.user).count()
    active_jobs = jobs.filter(is_active=True, application_deadline__gt=timezone.now()).count()
    
    context = {
        'jobs': jobs,
        'total_applications': total_applications,
        'active_jobs': active_jobs,
    }
    return render(request, 'jobs/employer_dashboard.html', context)

@login_required
def my_applications(request):
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    applications = Application.objects.filter(applicant=request.user).select_related('job', 'job__company')
    
    context = {
        'applications': applications,
    }
    return render(request, 'jobs/my_application.html', context)

@login_required
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Only job seekers can save jobs.')
        return redirect('job_detail', job_id=job_id)
    
    saved_job, created = SavedJob.objects.get_or_create(job=job, user=request.user)
    
    if created:
        messages.success(request, 'Job saved successfully!')
    else:
        messages.info(request, 'Job already saved.')
    
    return redirect('job_detail', job_id=job_id)

@login_required
def unsave_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    SavedJob.objects.filter(job=job, user=request.user).delete()
    messages.success(request, 'Job removed from saved jobs.')
    return redirect('job_detail', job_id=job_id)

@login_required
def saved_jobs(request):
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job', 'job__company')
    
    context = {
        'saved_jobs': saved_jobs,
    }
    return render(request, 'jobs/saved_jobs.html', context)

@login_required
def manage_companies(request):
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    companies = Company.objects.all()  # In a real app, you'd filter by employer
    
    # Count stats for the dashboard
    active_jobs_count = Job.objects.filter(employer=request.user, is_active=True).count()
    total_applications = Application.objects.filter(job__employer=request.user).count()
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            messages.success(request, f'Company "{company.name}" created successfully!')
            return redirect('manage_companies')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CompanyForm()
    
    context = {
        'companies': companies,
        'form': form,
        'active_jobs_count': active_jobs_count,
        'total_applications': total_applications,
    }
    return render(request, 'jobs/manage_companies.html', context)





@login_required
def view_applicants(request, job_id):
    """View all applicants for a specific job"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    applications = Application.objects.filter(job=job).select_related('applicant', 'applicant__jobseekerprofile')
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        applications = applications.filter(
            Q(applicant__username__icontains=search_query) |
            Q(applicant__email__icontains=search_query) |
            Q(cover_letter__icontains=search_query)
        )
    
    context = {
        'job': job,
        'applications': applications,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'jobs/view_applicants.html', context)

@login_required
def update_application_status(request, application_id):
    """Update application status and notify applicant"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    application = get_object_or_404(Application, id=application_id, job__employer=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        employer_notes = request.POST.get('employer_notes', '')
        notify_applicant = request.POST.get('notify_applicant') == 'on'
        
        if new_status in dict(Application.STATUS_CHOICES):
            old_status = application.status
            application.status = new_status
            application.employer_notes = employer_notes
            application.save()
            
            # Create notification for employer
            Notification.objects.create(
                user=request.user,
                notification_type='application_status',
                title=f'Application Status Updated',
                message=f'You updated {application.applicant.username}\'s application status from {old_status} to {new_status} for {application.job.title}.',
                related_application=application
            )
            
            # Notify applicant if requested
            if notify_applicant:
                send_application_status_email(application, old_status, new_status)
                application.mark_as_notified()
                
                # Create notification for applicant
                Notification.objects.create(
                    user=application.applicant,
                    notification_type='application_status',
                    title=f'Application Status Update - {application.job.title}',
                    message=f'Your application status has been updated to {new_status}.',
                    related_application=application
                )
                
                messages.success(request, f'Application status updated and applicant notified!')
            else:
                messages.success(request, f'Application status updated!')
            
            return redirect('view_applicants', job_id=application.job.id)
    
    return redirect('view_applicants', job_id=application.job.id)

def send_application_status_email(application, old_status, new_status):
    """Send email notification to applicant about status change"""
    subject = f'Application Status Update - {application.job.title}'
    
    context = {
        'applicant': application.applicant,
        'job': application.job,
        'old_status': old_status,
        'new_status': new_status,
        'application': application,
        'company': application.job.company,
    }
    
    html_message = render_to_string('emails/application_status_update.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email='noreply@jobportal.com',
            recipient_list=[application.applicant.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

@login_required
def application_detail(request, application_id):
    """View detailed application information"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    application = get_object_or_404(
        Application, 
        id=application_id, 
        job__employer=request.user
    )
    
    context = {
        'application': application,
    }
    return render(request, 'jobs/application_details.html', context)

@login_required
def employer_notifications(request):
    """View employer notifications"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    application_updates_count = notifications.filter(notification_type='application_status').count()
    system_count = notifications.filter(notification_type='system').count()
    
    # Mark as read if specified
    if request.GET.get('mark_read') == 'all':
        notifications.update(is_read=True)
        messages.success(request, 'All notifications marked as read!')
        return redirect('employer_notifications')
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'application_updates_count': application_updates_count,
        'system_count': system_count,
    }
    return render(request, 'jobs/employer_notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('HTTP_REFERER'):
        return redirect(request.headers.get('HTTP_REFERER'))
    return redirect('employer_notifications')