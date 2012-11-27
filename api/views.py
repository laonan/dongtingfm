# coding=utf-8
from django.http import HttpResponse

from accounts.views import _login

def android_login(request):
    email = request.GET.get('email', None)
    password = request.GET.get('password', None)
    if _login(request, email, password) == True:
        return_data = '1'
    else:
        return_data = '0'
    
    return HttpResponse(return_data, mimetype="text/plain")