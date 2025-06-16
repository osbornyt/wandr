from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

from main.models import Vendor


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


from .models import ResourceOrder, User 

class ResourceOrderForm(forms.ModelForm):
    company_name = forms.CharField(max_length=255, required=True)

    class Meta:
        model = ResourceOrder
        fields = [
            'agreement_number',
            'company_name',
            'project_name',
            'incident_number',
            'resource_assigned',
            'make',
            'model',
            'request_number',
            
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'
            
            
    def clean(self):
        cleaned_data = super().clean()
        agreement_number = cleaned_data.get('agreement_number')
        project_name = cleaned_data.get('project_name')

        # Example: Ensure combination of agreement number and project name is unique
        if agreement_number and project_name:
            if self.instance and self.instance.agreement_number == agreement_number and self.instance.project_name == project_name:
                # If updating and these fields haven't changed, no validation needed
                pass
            elif ResourceOrder.objects.filter(agreement_number=agreement_number, project_name=project_name).exists():
                raise forms.ValidationError("A Resource Order with this Agreement Number and Project Name already exists.")
        return cleaned_data
    

from .models import Evaluation 

class EvaluationForm(forms.ModelForm):
    start_date = forms.DateField(
        label='Start Date of Evaluation',
        widget=forms.DateInput(attrs={'type': 'date'}), # HTML5 date input
        required=True
    )
    end_date = forms.DateField(
        label='End Date of Evaluation',
        widget=forms.DateInput(attrs={'type': 'date'}), # HTML5 date input
        required=True
    )

    class Meta:
        model = Evaluation
        fields = [
            'contractor',
            'resource',
            'fire',
            'agreement_number',
            'resource_order_number',
            'name',
            
        ]
        labels = {
            'contractor': 'Contractor/Company Name',
            'resource': 'Resource Type and Equipment ID', # Example: You might want to rename this too
            'fire': 'Fire Name and Number',     # Example: You might want to rename this too
            'agreement_number': 'Agreement Number',
            'resource_order_number': 'Equipment Resource Order #',
            'name': 'Contracting Officer Name', # Assuming 'name' is the evaluator's name
            'dates_covered': 'Evaluation Period (Dates Covered)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'
        if self.instance and self.instance.dates_covered:
            try:
                # Assuming dates_covered format is "YYYY-MM-DD to YYYY-MM-DD"
                parts = self.instance.dates_covered.split(' to ')
                if len(parts) == 2:
                    from datetime import datetime
                    self.initial['start_date'] = datetime.strptime(parts[0], '%Y-%m-%d').date()
                    self.initial['end_date'] = datetime.strptime(parts[1], '%Y-%m-%d').date()
            except (ValueError, IndexError):
                # Handle cases where the format might be unexpected
                pass

            
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # 1. Validate the two date fields
        if start_date and end_date:
            if start_date > end_date:
                # Add a form-level error (non-field error)
                self.add_error(None, "End Date cannot be earlier than Start Date.")
            
            # 2. Combine the dates into the 'dates_covered' format
            #    This is the value that will be saved to the model's 'dates_covered' field
            cleaned_data['dates_covered'] = f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
        
        
        agreement_number = cleaned_data.get('agreement_number')
        project_name = cleaned_data.get('project_name')

        # Example: Ensure combination of agreement number and project name is unique
        if agreement_number and project_name:
            if self.instance and self.instance.agreement_number == agreement_number and self.instance.project_name == project_name:
                # If updating and these fields haven't changed, no validation needed
                pass
            elif ResourceOrder.objects.filter(agreement_number=agreement_number, project_name=project_name).exists():
                raise forms.ValidationError("A Resource Order with this Agreement Number and Project Name already exists.")
        return cleaned_data

        

from django import forms
from .models import Vendor


class VendorBasicForm(forms.ModelForm):
    form_name = forms.CharField(widget=forms.HiddenInput(), initial='basic')

    class Meta:
        model = Vendor
        fields = ['name', 'uei']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'uei': forms.TextInput(attrs={'class': 'form-control'}),
        }


class VendorPhysicalForm(forms.ModelForm):
    form_name = forms.CharField(widget=forms.HiddenInput(), initial='physical')

    class Meta:
        model = Vendor
        fields = ['address1', 'address2', 'city', 'state', 'zip']
        widgets = {
            'address1': forms.TextInput(attrs={'class': 'form-control'}),
            'address2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip': forms.TextInput(attrs={'class': 'form-control'}),
        }


class VendorMailingForm(forms.ModelForm):
    form_name = forms.CharField(widget=forms.HiddenInput(), initial='mailing')

    class Meta:
        model = Vendor
        fields = ['mailAddress1', 'mailAddress2', 'mailCity', 'mailState', 'mailZip']
        widgets = {
            'mailAddress1': forms.TextInput(attrs={'class': 'form-control'}),
            'mailAddress2': forms.TextInput(attrs={'class': 'form-control'}),
            'mailCity': forms.TextInput(attrs={'class': 'form-control'}),
            'mailState': forms.TextInput(attrs={'class': 'form-control'}),
            'mailZip': forms.TextInput(attrs={'class': 'form-control'}),
        }


class VendorContactForm(forms.ModelForm):
    form_name = forms.CharField(widget=forms.HiddenInput(), initial='contact')

    class Meta:
        model = Vendor
        fields = ['contact', 'email']
        widgets = {
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class VendorPhoneForm(forms.ModelForm):
    form_name = forms.CharField(widget=forms.HiddenInput(), initial='phone')

    class Meta:
        model = Vendor
        fields = ['phone', 'phoneAfterHours', 'phoneAlternate', 'fax']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'phoneAfterHours': forms.TextInput(attrs={'class': 'form-control'}),
            'phoneAlternate': forms.TextInput(attrs={'class': 'form-control'}),
            'fax': forms.TextInput(attrs={'class': 'form-control'}),
        }
