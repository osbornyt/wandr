from django.shortcuts import render

# Create your views here.
import os
import json
import csv
import requests
from urllib.parse import quote
from decimal import Decimal
from datetime import datetime
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from django import forms
from django.conf import settings
from django.core import serializers
from .forms import ResourceOrderForm,EvaluationForm
from .forms import SignUpForm, VendorBasicForm, VendorPhysicalForm, VendorMailingForm, VendorContactForm, \
    VendorPhoneForm
from django.db import connection


from .models import Form, UserForm, AnswerField, ResourceOrder, Vendor, Evaluation
from landing_app.views import show_landing
from form_app.utils import mine_RO,populate_evaluation_form

@login_required
def create_shift_ticket(request):
    user = request.user
    first = user.first_name
    last = user.last_name
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('project_id')
            if project_id != "":
                try:
                    ro = ResourceOrder.objects.filter(id=project_id).first()
                    full_name = first + " " + last
                    initials = first[0].upper() + last[0].upper()
                    try:
                        form = Form.objects.first()
                    except Form.DoesNotExist:
                        return JsonResponse({'error': 'Form not found'}, status=404)

                    
                    # Create the UserForm instance
                    user_form = UserForm.objects.create(
                        name=form.name,  # Or a custom name if needed
                        form_id=form,
                        num_questions=form.number_of_fields, # Initialize from form or get from JSON if needed
                        num_pages=0,
                        curr_page=0,
                        curr_question=0,
                        user=request.user
                    )
                    AnswerField.objects.create(userform=user_form,answer_type="text",answer=ro.agreement_number,question_number=1,table_col=0,table_row=0,question_page = 1)
                    AnswerField.objects.create(userform=user_form,answer_type="text",answer=ro.company_name,question_number=2,table_col=0,table_row=0,question_page = 1)
                    AnswerField.objects.create(userform=user_form,answer_type="text",answer=ro.project_name,question_number=3,table_col=0,table_row=0,question_page = 1)
                    AnswerField.objects.create(userform=user_form,answer_type="text",answer=ro.incident_number,question_number=4,table_col=0,table_row=0,question_page = 1)
                    AnswerField.objects.create(userform=user_form,answer_type="text",answer=ro.make,question_number=6,table_col=0,table_row=0,question_page = 2)
                    AnswerField.objects.create(userform=user_form,answer_type="text",answer=ro.model,question_number=7,table_col=0,table_row=0,question_page = 2)
                    AnswerField.objects.create(userform=user_form,answer_type="text",answer=full_name,question_number=17,table_col=0,table_row=0,question_page = 6)
                    AnswerField.objects.create(userform=user_form,answer_type="text",answer=initials,question_number=18,table_col=0,table_row=0,question_page = 6)

                    answer_fields = AnswerField.objects.filter(userform=user_form.id, question_page=1) #Ensure user owns form
                    saved_data = []
                    for field in answer_fields:
                        saved_data.append({
                            'id': field.id, # Include the ID of the AnswerField
                            'answer_type': field.answer_type,
                            'answer': field.answer,
                            'question_number': field.question_number,
                            'table_col': field.table_col,
                            'table_row': field.table_row,
                            'question_page': field.question_page,
                        })
                    
                    return JsonResponse({'message': 'initial', 'user_form_id': user_form.id, 'useranswer': saved_data}, status=201)

                except Form.DoesNotExist:
                    return JsonResponse({'error': 'Form not found'}, status=404)
            else:
                try:
                    form = Form.objects.first()
                except Form.DoesNotExist:
                    return JsonResponse({'error': 'Form not found'}, status=404)

                
                # Create the UserForm instance
                user_form = UserForm.objects.create(
                    name=form.name,  # Or a custom name if needed
                    form_id=form,
                    num_questions=form.number_of_fields, # Initialize from form or get from JSON if needed
                    num_pages=0,
                    curr_page=0,
                    curr_question=0,
                    user=request.user
                )
                return JsonResponse({'message': 'initial', 'user_form_id': user_form.id, 'useranswer': []}, status=201)

            
            # Example: Return a success message

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Error processing data: {e}") # Log the error for debugging.
            return JsonResponse({'error': 'An error occurred while processing the request'}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405) # Only allow POST requests
    

@login_required
def begin_form_filling(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form_id = data.get('form_id')
            if not form_id:
                return JsonResponse({'error': 'User ID and Form ID are required'}, status=400)

            # Check if a UserForm already exists for this user and form
            existing_user_form = UserForm.objects.filter(user=request.user, id=form_id).first()
            if existing_user_form:
                try:
                    answer_fields = AnswerField.objects.filter(userform=existing_user_form.id, question_page=1) #Ensure user owns form
                    data = []
                    for field in answer_fields:
                        data.append({
                            'id': field.id, # Include the ID of the AnswerField
                            'answer_type': field.answer_type,
                            'answer': field.answer,
                            'question_number': field.question_number,
                            'table_col': field.table_col,
                            'table_row': field.table_row,
                            'question_page': field.question_page,
                        })
                    return JsonResponse({'message': 'data', 'useranswer': data, 'user_form_id': existing_user_form.id}, status=200)

                except AnswerField.DoesNotExist:
                    return JsonResponse({'message': 'empty','useranswer': []}, status=200) #Return empty list if no answers
                except Exception as e:
                    return JsonResponse({'error': 'An error occurred while retrieving form data'}, status=500)

            # Create the UserForm instance
            user_form = UserForm.objects.create(
                name=form.name,  # Or a custom name if needed
                form_id=form,
                num_questions=form.number_of_fields, # Initialize from form or get from JSON if needed
                num_pages=0,
                curr_page=0,
                curr_question=0,
                user=request.user
            )

            return JsonResponse({'message': 'initial', 'user_form_id': user_form.id, 'useranswer': []}, status=201)

            # Example: Return a success message

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Error processing data: {e}") # Log the error for debugging.
            return JsonResponse({'error': 'An error occurred while processing the request'}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405) # Only allow POST requests
    


def get_form_data_per_page(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_form_id = data.get('user_form_id')
            page = data.get('page')  # Get the page number

            if not user_form_id or not page:
                return JsonResponse({'error': 'User form ID and page is required'}, status=400)

            try:
                answer_fields = AnswerField.objects.filter(userform_id=user_form_id, question_page=page) #Ensure user owns form
                
                data = []
                for field in answer_fields:
                    data.append({
                        'id': field.id, # Include the ID of the AnswerField
                        'answer_type': field.answer_type,
                        'answer': field.answer,
                        'question_number': field.question_number,
                        'table_col': field.table_col,
                        'table_row': field.table_row,
                        'question_page': field.question_page,
                    })

                return JsonResponse({'form_data': data}, status=200)

            except AnswerField.DoesNotExist:
                return JsonResponse({'form_data': []}, status=200) #Return empty list if no answers
            except Exception as e:
                print(f"Error getting form data: {e}")
                return JsonResponse({'error': 'An error occurred while retrieving form data'}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Error saving form data: {e}") # Log the error for debugging.
            return JsonResponse({'error': 'An error occurred while saving form data'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def save_form_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_form_id = data.get('user_form_id')
            form_data = data.get('form_data') # This will contain the answers
            currpage = data.get('currpage')
            if not user_form_id or not form_data or not currpage:
                return JsonResponse({'error': 'User form ID and form data are required'}, status=400)
            try:
                user_form = UserForm.objects.get(pk=user_form_id, user=request.user) # Ensure user owns the form
            except UserForm.DoesNotExist:
                return JsonResponse({'error': 'User form not found or you do not have permission to access it.'}, status=404)
            # Delete existing AnswerFields for this userform (if any) to avoid duplicates
            # AnswerField.objects.filter(userform=user_form).delete()
            # Create AnswerField instances
            for question_data in form_data:
                AnswerField.objects.filter(userform=user_form, question_number=question_data.get('No'), table_col=question_data.get('Col'), table_row=question_data.get('Row')).delete()
                answer_field = AnswerField.objects.create(
                    userform=user_form,
                    answer_type=question_data.get('Answer_Type'),
                    answer=question_data.get('Answer'),
                    question_number=question_data.get('No'),
                    table_col=question_data.get('Col'),
                    table_row=question_data.get('Row'),
                    question_page = question_data.get('Page')
                )

            # Fetch data for next page if exists
            try:
                answer_fields = AnswerField.objects.filter(userform=user_form.id, question_page=currpage) #Ensure user owns form
                saved_data = []
                for field in answer_fields:
                    saved_data.append({
                        'id': field.id, # Include the ID of the AnswerField
                        'answer_type': field.answer_type,
                        'answer': field.answer,
                        'question_number': field.question_number,
                        'table_col': field.table_col,
                        'table_row': field.table_row,
                        'question_page': field.question_page,
                    })
                return JsonResponse({'message': 'data', 'useranswer': saved_data}, status=200)

            except AnswerField.DoesNotExist:
                return JsonResponse({'message': 'empty','useranswer': []}, status=200) #Return empty list if no answers
            except Exception as e:
                print(f"Error getting form data: {e}")
                return JsonResponse({'error': 'An error occurred while retrieving form data'}, status=500)

        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Error saving form data: {e}") # Log the error for debugging.
            return JsonResponse({'error': 'An error occurred while saving form data'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


    
#@login_required
def home(request):
    user = request.user
    if user.is_authenticated:
        return redirect("main:dashboard")
    #return render(request, "registration/login.html", {})
    return redirect("landing_app:landing")

def mysettings(request):
    user = request.user
    if user.is_authenticated:
        vendor = Vendor.objects.filter(userid=user.id).first()

        if not vendor:
            vendor = Vendor.objects.create(userid=user.id, name=user.first_name + " " + user.last_name)

        if request.method == 'POST':
            form_name = request.POST.get('form_name')

            form_classes = {
                'basic': VendorBasicForm,
                'physical': VendorPhysicalForm,
                'mailing': VendorMailingForm,
                'contact': VendorContactForm,
                'phone': VendorPhoneForm,
            }

            success_messages = {
                'basic': 'Basic Info changes saved successfully.',
                'physical': 'Physical Address changes saved successfully.',
                'mailing': 'Mailing Address changes saved successfully.',
                'contact': 'Contact Info changes saved successfully.',
                'phone': 'Phone Numbers changes saved successfully.',
            }

            form_class = form_classes.get(form_name)

            if form_class:
                form = form_class(request.POST, instance=vendor)
                if form.is_valid():
                    form.save()
                    messages.success(request, success_messages.get(form_name))
                    return redirect("main:mysettings")  # Replace with your own
        else:
            context = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'initials': user.first_name[0].upper() + user.last_name[0].upper(),
                'basic_form': VendorBasicForm(instance=vendor),
                'physical_form': VendorPhysicalForm(instance=vendor),
                'mailing_form': VendorMailingForm(instance=vendor),
                'contact_form': VendorContactForm(instance=vendor),
                'phone_form': VendorPhoneForm(instance=vendor),
            }
            return render(request, 'profile.html', context)
    return redirect("main:login")

def update_profile(request):
    user = request.user
    if user.is_authenticated:
        if user.is_staff:
            if request.method == 'POST':
                username = request.POST.get('username', '')
                email = request.POST.get('email', '')
                first_name = request.POST.get('first_name', '')
                last_name = request.POST.get('last_name', '')
                password = request.POST.get('password', '')

                if username and username != '':
                    user.username = username
                if email and email != '':
                    user.email = email
                if first_name and first_name != '':
                    user.first_name = first_name
                if last_name and last_name != '':
                    user.last_name = last_name
                if password and password != '':
                    user.set_password(password)
                user.save()
                return redirect("main:mysettings")
            return redirect("main:mysettings")
        return render(request, "approval.html")    
    return redirect("main:login")


def dashboard(request):
    user = request.user
    if user.is_authenticated:
        first = user.first_name
        last = user.last_name
        initials = ""
        if first and last:
            initials = first[0].upper() + last[0].upper()
            username = user.username
            first = user.first_name
            last = user.last_name
            form = Form.objects.get(id=1)
            context = {
                'first_name': first,
                'last_name': last,
                'username': username,
                'initials': initials,
                'form': form
            }
            return render(request, "dashboard.html", context)    
    
    
    return redirect("main:login")

def upload_RO(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'POST':
            company = request.POST.get('company')
            agreement_number = request.POST.get('agreementNumber') 
            resource_file = request.FILES.get('resourceFile')   
            summary = mine_RO(resource_file)
            new_RO = ResourceOrder(
                agreement_number = agreement_number,
                company_name = company,
                project_name = summary['project_name'],
                incident_number = summary['incident_number'],
                request_number = summary['request_number'],
                make = summary['make'],
                model = summary['model'],
                resource_assigned = summary['resource_assigned'],
                pdf_location = resource_file,
                user = user,
                expired = "No"
            )
            new_RO.save()
    return redirect("main:resource_order")


@login_required
def create_resource_order(request):
    if request.method == 'POST':
        form = ResourceOrderForm(request.POST, request.FILES)
        if form.is_valid():
            resource_order = form.save(commit=False) 
            resource_order.user = request.user 
            resource_order.expired = "No"
            resource_order.pdf_location = None
            resource_order.save() 

            #messages.success(request, 'Resource Order created successfully!')
    return redirect("main:resource_order") 
    

def resource_order(request):
    user = request.user
    
    if user.is_authenticated:
        first = user.first_name
        last = user.last_name
        initials = ""
        if first and last:
            initials = first[0].upper() + last[0].upper()
            username = user.username
            first = user.first_name
            last = user.last_name
            user_uploaded_forms = ResourceOrder.objects.filter(user=user)
            form = ResourceOrderForm()
            context = {
                'first_name': first,
                'last_name': last,
                'username': username,
                'initials': initials,
                'uploaded_forms': user_uploaded_forms,
                'form': form,
            }
            return render(request, "resource_order.html", context)    
    
    
    return redirect("main:login")

@login_required
def generate_exhibit_e(request):
    if request.method == 'POST':
        form = EvaluationForm(request.POST, request.FILES)
        if form.is_valid():
            evaluation = form.save(commit=False) 
            evaluation.user = request.user 
            evaluation.save() 

            #messages.success(request, 'Resource Order created successfully!')
    return redirect("main:exhibit_e") 
    
def generate_evaluation_auto(request):
    user = request.user
    if user.is_authenticated:
        first = user.first_name
        last = user.last_name
        if request.method == 'POST':
            start = request.POST.get('start')
            end = request.POST.get('end') 
            project = request.POST.get('project')
            ro = ResourceOrder.objects.filter(id=project).first()
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
            dates_covered = f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
            new_evaluation = Evaluation(
                contractor = ro.company_name,
                resource = ro.make,
                fire = ro.project_name + "/" + ro.incident_number,
                agreement_number = ro.agreement_number,
                resource_order_number = ro.request_number,
                name = first + " " + last,
                dates_covered = dates_covered,
                user = user
            )
            new_evaluation.save()

           
    return redirect("main:exhibit_e")



def exhibit_e(request):
    user = request.user
    
    if user.is_authenticated:
        first = user.first_name
        last = user.last_name
        initials = ""
        if first and last:
            initials = first[0].upper() + last[0].upper()
            username = user.username
            first = user.first_name
            last = user.last_name
            user_uploaded_forms = Evaluation.objects.filter(user=user)
            projects = ResourceOrder.objects.filter(user=user).values('id', 'project_name').order_by('-id')

            form = EvaluationForm()
            context = {
                'first_name': first,
                'last_name': last,
                'username': username,
                'initials': initials,
                'uploaded_forms': user_uploaded_forms,
                'form': form,
                'projects': projects,
            }
            return render(request, "exhibit_e.html", context)    
    
    
    return redirect("main:login")

@login_required
def delete_RO_form(request, form_id):
    """
    Deletes a specific Resource Order Form and its associated file.
    Ensures that only the owner can delete their forms.
    """
    ro_form = get_object_or_404(ResourceOrder, id=form_id, user=request.user)

    if request.method == 'POST':
        try:
            ro_form.delete()
            messages.success(request, 'Resource Order Form deleted successfully.')
        except Exception as e:
            messages.error(request, f"Error deleting form: {e}")
            print(f"Error deleting RO form {form_id}: {e}")
        return redirect('main:upload_RO')
    
    messages.error(request, 'Invalid request for deletion. Please use the delete button.')
    return redirect('main:upload_RO')

@login_required
def delete_Shift_ticket(request, form_id):
    """
    Deletes a specific Resource Order Form and its associated file.
    Ensures that only the owner can delete their forms.
    """
    form = get_object_or_404(UserForm, id=form_id, user=request.user)

    if request.method == 'POST':
        try:
            form.delete()
            messages.success(request, 'Resource Order Form deleted successfully.')
        except Exception as e:
            messages.error(request, f"Error deleting form: {e}")
            print(f"Error deleting RO form {form_id}: {e}")
        return redirect('main:fetch_shift_ticket')
    
    messages.error(request, 'Invalid request for deletion. Please use the delete button.')
    return redirect('main:fetch_shift_ticket')

@login_required
def delete_Evaluation(request, form_id):
    """
    Deletes a specific Resource Order Form and its associated file.
    Ensures that only the owner can delete their forms.
    """
    form = get_object_or_404(Evaluation, id=form_id, user=request.user)

    if request.method == 'POST':
        try:
            form.delete()
            messages.success(request, 'Resource Order Form deleted successfully.')
        except Exception as e:
            messages.error(request, f"Error deleting form: {e}")
            print(f"Error deleting RO form {form_id}: {e}")
        return redirect('main:upload_RO')
    
    messages.error(request, 'Invalid request for deletion. Please use the delete button.')
    return redirect('main:upload_RO')

@login_required
def preview_evaluation(request):
    form_id = request.GET.get('id')
    print(form_id)
    form = get_object_or_404(Evaluation, id=form_id, user=request.user)
    prefill = {
        "ContractorCompany Name": form.contractor,
        "Resource Type and Equipment ID EngineDozerWater Tenderetc": form.resource,
        "Fire Name and Number": form.fire,
        "Equipment Resource Order": form.resource_order_number,
        "Agreement Number": form.agreement_number,
        "Contracting Officer Name": form.name,
    }
    try:
        # Get the PDF content as bytes from your function
        pdf_content = populate_evaluation_form(prefill)

        # Set the Content-Type header to application/pdf
        response = HttpResponse(pdf_content, content_type='application/pdf')

        # Set Content-Disposition header to control how the browser handles the file
        # 'inline' will try to display the PDF in the browser
        # 'attachment' will prompt the user to download the file
        filename = f"Evaluation_{form.resource_order_number}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response

    except Exception as e:
        messages.error(request, f"An error occurred while generating the PDF: {e}")
        return redirect('your_app_name:evaluation_list') # Redirect on error

# def form_display(request, form_id):
#     form = get_object_or_404(Form, pk=form_id)
#     context = {
#         'form': form
#     }
#     return render(request, 'form_display.html', context)

def pageholder(request):
    return render(request, "createnew.html", {})

def fetch_shift_ticket(request):
    user = request.user
    if user.is_authenticated:
        first = user.first_name
        last = user.last_name
        initials = ""
        if first and last:
            initials = first[0].upper() + last[0].upper()
            username = first #user.username
            # first = user.first_name
            # last = user.last_name
            userid = user.id
            
            user_uploaded_forms = UserForm.objects.filter(user=user).order_by('-id')
            projects = ResourceOrder.objects.filter(user=user).values('id', 'project_name').order_by('-id')

            context = {
                'first_name': first,
                'last_name': last,
                'username': username,
                'initials': initials,
                "user_id": userid,
                "form_id": 1,
                "user_form_id": "1",
                'uploaded_forms': user_uploaded_forms,
                'projects': projects,
            }
            return render(request, "shift_ticket.html", context)
    return redirect("main:login")

def get_vendor(request):
    api_url = "https://colorcountrycontracting.com/api/all/" + request.user.username + "/"
    api_username = "admin"
    api_password = "validform"

    try:
        response = requests.get(
            api_url,
            auth=(api_username, api_password),
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching data from VIPR API: {e}"
        context = {'error': error_message}
        return context

def get_agreement(agreement):
    api_url = "https://colorcountrycontracting.com/api/agreement/" + quote(agreement) + "/"
    print(api_url)
    api_username = "admin"
    api_password = "validform"

    try:
        response = requests.get(
            api_url,
            auth=(api_username, api_password),
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        return [data['resource'],data['number']]

    except requests.exceptions.RequestException as e:
        return None

def get_resource(resource):
    api_url = "https://colorcountrycontracting.com/api/resource/" + resource + "/"
    api_username = "admin"
    api_password = "validform"

    try:
        response = requests.get(
            api_url,
            auth=(api_username, api_password),
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        return [data['vin'],data['clin'],data['make'],data['model']]

    except requests.exceptions.RequestException as e:
        return None


def fetch_form_data(request):
    # user = request.user
    # first = user.first_name
    # last = user.last_name
    file_path = os.path.join(settings.MEDIA_ROOT, "json_data", "shiftticket_json.json")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # ro = ResourceOrder.objects.filter(user=user).first()
            # prefill = {
            #     'agreement': ro.agreement_number,
            #     'project': ro.project_name,
            #     'incident': ro.incident_number,
            #     'request': ro.request_number,
            #     'make': ro.make,
            #     'model': ro.model,
            #     'name': first + " " + last,
            #     'initials': first[0].upper() + last[0].upper()
            # }
            # data['prefill'] = prefill

        return JsonResponse(data)
    except FileNotFoundError:
        return HttpResponse("Template not found", status=404)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON in template file", status=500)
    except Exception as e:
        return HttpResponse("Error reading template data", status=500)


def authView(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(email=email).exists():
            messages.success(request, ("A user with the email already exists"))
            return render(request, "register.html")
        User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name, password=password)
        user = authenticate(username=email, password=password)
        full_name = first_name + " " + last_name
        new_vendor = Vendor(name=full_name, email=email,userid=user.id)
        new_vendor.save()
        login(request, user)
        return redirect("main:dashboard")
        
    return render(request, "register.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("main:dashboard")
        
        messages.success(request, ("Email does not match password"))
        return render(request, "login.html", {})
    else:
        return render(request, "login.html", {})

def logout_user(request):
    logout(request)
    #messages.success(request, ("You have Successfully Logged Out "))
    return redirect('/landing')


