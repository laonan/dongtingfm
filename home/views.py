# coding=utf-8
from accounts.views import sign_in
from songs.views import song_list

def index(request, template_name):
    if request.user.is_authenticated():
        return song_list(request, None, template_name)      
    else:
        return sign_in(request)      