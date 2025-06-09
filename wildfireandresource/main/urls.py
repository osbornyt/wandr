from django.urls import path, include
from django.urls import path, include
from .views import authView, home, logout_user, login_user, dashboard, mysettings, pageholder, fetch_form_data, begin_form_filling, save_form_data, get_form_data_per_page,update_profile,resource_order,delete_RO_form
from .views import upload_RO,fetch_shift_ticket,exhibit_e,generate_exhibit_e,create_resource_order,create_shift_ticket,delete_Shift_ticket
from .views import generate_evaluation_auto,delete_Evaluation,preview_evaluation
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("", home, name="home"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("signup/", authView, name="authView"),
    path("mysettings/", mysettings, name="mysettings"),
    path("update_profile/", update_profile, name="update_profile"),
    path("dashboard/", dashboard, name="dashboard"),
    path("pageholder/", pageholder, name="pageholder"),
    path('fetch_shift_ticket/', fetch_shift_ticket, name="fetch_shift_ticket"),
    path('fetch_form_data/', fetch_form_data, name="fetch_form_data"),
    path('begin_form_filling/', begin_form_filling, name="begin_form_filling"),
    path('save_form_data/', save_form_data, name="save_form_data"),
    path('get_form_data_per_page/', get_form_data_per_page, name="get_form_data_per_page"),
    path('resource_order/', resource_order, name="resource_order"),
    path('delete_RO_form/<int:form_id>/', delete_RO_form, name="delete_RO_form"),
    path('delete_Evaluation/<int:form_id>/', delete_Evaluation, name="delete_Evaluation"),
    
    path('upload_RO/', upload_RO, name="upload_RO"),
    path('exhibit_e/', exhibit_e, name="exhibit_e"),
    path('generate_exhibit_e/', generate_exhibit_e, name="generate_exhibit_e"),
    path('create_resource_order/', create_resource_order, name="create_resource_order"),
    path('create_shift_ticket/', create_shift_ticket, name="create_shift_ticket"),
    path('delete_Shift_ticket/<int:form_id>/', delete_Shift_ticket, name="delete_Shift_ticket"),
    path('generate_evaluation_auto/', generate_evaluation_auto, name="generate_evaluation_auto"),
    path('preview_evaluation/', preview_evaluation, name="preview_evaluation")
    
    
    
    
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)