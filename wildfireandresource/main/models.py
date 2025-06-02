from django.db import models

# Create your models here.
from django.utils import timezone
# Create your models here.
from django.contrib.auth.models import User  # Import User model

class Form(models.Model):
    name = models.CharField(max_length=255)
    pdf_location = models.FileField(upload_to='pdfs/')  # Store PDF files in 'pdfs' subdirectory
    json_location = models.FileField(upload_to='json_data/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User model
    about = models.TextField(blank=True, null=True)  # Make 'about' optional
    number_of_fields = models.IntegerField(default=0)
    # The ID field is automatically created by Django (AutoField)

    # class Meta:
    #     # IMPORTANT: Tell Django that this model maps to an existing table
    #     # and that Django should NOT manage its creation or migrations.
    #     managed = False
    #     db_table = 'base_form'
    #     app_label = 'main' # This is the app it lives in for project_beta
               

    def __str__(self):
        return self.name  # Make it easier to see form names in admin

class UserForm(models.Model):
    name = models.CharField(max_length=255)
    form_id = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='fields')
    num_questions = models.IntegerField(blank=False, null=False)
    num_pages = models.IntegerField(blank=False, null=False)
    curr_page = models.IntegerField(blank=False, null=False)
    curr_question = models.IntegerField(blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    # class Meta:
    #     # IMPORTANT: Tell Django that this model maps to an existing table
    #     # and that Django should NOT manage its creation or migrations.
    #     managed = False
    #     db_table = 'base_userform'
    #     app_label = 'main' # This is the app it lives in for project_beta
    

    def __str__(self):
        return self.name

class AnswerField(models.Model):
    userform = models.ForeignKey(UserForm, on_delete=models.CASCADE, related_name='fields')
    answer_type = models.CharField(max_length=20)
    answer = models.TextField(blank=True, null=False)  # Optional description
    question_number = models.IntegerField()
    table_col = models.IntegerField()
    table_row = models.IntegerField()
    question_page = models.IntegerField(blank=True, null=True) # Optional field page
    

    # class Meta:
    #     # IMPORTANT: Tell Django that this model maps to an existing table
    #     # and that Django should NOT manage its creation or migrations.
    #     managed = False
    #     db_table = 'base_answerfield'
    #     app_label = 'main' # This is the app it lives in for project_beta
    

    def __str__(self):
        return f'Q. {self.question_number} | {self.answer}'

class Vendor(models.Model):
    name = models.CharField(max_length=255)
    uei = models.CharField(max_length=255, blank=True, null=True)
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip = models.CharField(max_length=255, blank=True, null=True)
    mailAddress1 = models.CharField(max_length=255, blank=True, null=True)
    mailAddress2 = models.CharField(max_length=255, blank=True, null=True)
    mailCity = models.CharField(max_length=255, blank=True, null=True)
    mailState = models.CharField(max_length=255, blank=True, null=True)
    mailZip = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    phoneAfterHours = models.CharField(max_length=255, blank=True, null=True)
    phoneAlternate = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    userid = models.IntegerField(null=True)
    
    # class Meta:
    #     # IMPORTANT: Tell Django that this model maps to an existing table
    #     # and that Django should NOT manage its creation or migrations.
    #     managed = False
    #     db_table = 'base_vendor'
    #     app_label = 'main' # This is the app it lives in for project_beta
    

    def __str__(self):
        return self.name  # Or a combination of fields, e.g., f"{self.name} ({self.code})"

class ResourceOrder(models.Model):
    agreement_number = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255,blank=True, null=True)
    project_name = models.CharField(max_length=255)
    incident_number = models.CharField(max_length=255)
    request_number = models.CharField(max_length=255)
    make = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    resource_assigned = models.CharField(max_length=255)
    pdf_location = models.FileField(upload_to='ResourceOrders/',null=True)  # Store PDF files in 'pdfs' subdirectory
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User model
    expired = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    # The ID field is automatically created by Django (AutoField)


    # class Meta:
    #     # IMPORTANT: Tell Django that this model maps to an existing table
    #     # and that Django should NOT manage its creation or migrations.
    #     managed = False
    #     db_table = 'base_resourceorder'
    #     app_label = 'main' # This is the app it lives in for project_beta
    


    def __str__(self):
        return self.project_name  # Make it easier to see form names in admin



class Evaluation(models.Model):
    contractor = models.CharField(max_length=255)
    resource = models.CharField(max_length=255)
    fire = models.CharField(max_length=255)
    agreement_number = models.CharField(max_length=255)
    resource_order_number = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    dates_covered = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User model
    created_at = models.DateTimeField(auto_now_add=True)
    # The ID field is automatically created by Django (AutoField)


    # class Meta:
    #     # IMPORTANT: Tell Django that this model maps to an existing table
    #     # and that Django should NOT manage its creation or migrations.
    #     managed = False
    #     db_table = 'base_resourceorder'
    #     app_label = 'main' # This is the app it lives in for project_beta
    


    def __str__(self):
        return self.project_name  # Make it easier to see form names in admin
