from django.shortcuts import render,redirect

# Create your views here.
def show_landing(request):
    return render(request, "index.html")

