from django import forms
from .models import Job, Application, Company, Category
from django.utils import timezone

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'website', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class JobForm(forms.ModelForm):
    application_deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=timezone.now() + timezone.timedelta(days=30)
    )

    def __init__(self, *args, **kwargs):
        self.employer = kwargs.pop('employer', None)
        super(JobForm, self).__init__(*args, **kwargs)
        
        # Filter companies to only show those related to the employer
        if self.employer:
            self.fields['company'].queryset = Company.objects.all()
        else:
            self.fields['company'].queryset = Company.objects.none()

    class Meta:
        model = Job
        fields = [
            'title', 'company', 'description', 'requirements', 
            'location', 'job_type', 'experience_level', 'salary', 
            'application_deadline'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., Nairobi, Remote'}),
            'salary': forms.NumberInput(attrs={'placeholder': 'e.g., 50000'}),
        }

    def clean_application_deadline(self):
        deadline = self.cleaned_data['application_deadline']
        if deadline <= timezone.now():
            raise forms.ValidationError("Application deadline must be in the future.")
        return deadline

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 5, 
                'placeholder': 'Write your cover letter explaining why you are a good fit for this position...'
            }),
        }

class JobSearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search by job title, company, or keywords...'
    }))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'City, state, or remote...'
    }))
    job_type = forms.ChoiceField(required=False, choices=[('', 'All Types')] + Job.JOB_TYPES)
    experience_level = forms.ChoiceField(required=False, choices=[('', 'All Levels')] + Job.EXPERIENCE_LEVELS)

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary and salary < 0:
            raise forms.ValidationError("Salary cannot be negative.")
        return salary