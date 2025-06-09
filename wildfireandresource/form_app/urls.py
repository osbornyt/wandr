from django.urls import path
from form_app import views

urlpatterns = [
    path('shift-ticket/<int:user_form_id>/', views.generate_shift_ticket_form, name='generate_shift_ticket_form'),
    path('check-filled/<int:user_form_id>/', views.are_filled_check, name='check_filled'),
    path('evaluation/<int:user_form_id>/', views.generate_evaluation_form, name='generate_evaluation_form'),
]