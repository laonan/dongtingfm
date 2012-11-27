#coding=utf-8
__author__ = 'laonan, http://laonan.net'

'''
调用weibo api例子, 将API的“/”变为“__”，并传入关键字参数，但不包括source和access_token参数：
client.get.statuses__user_timeline()

client.post.statuses__update(status=u'测试OAuth 2.0发微博')

f = open('/Users/Alan/Workspace/dongting/static/images/player_bg.png')
client.upload.statuses__upload(status=u'测试OAuth 2.0带图片发微博', pic=f)
f.close()
'''

from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.views import login as auth_login_view
from django.contrib.sites.models import get_current_site
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from accounts.models import UserProfile, WeiboUser
from accounts.forms import RegistrationForm
from accounts.views import _login
from weibo import APIClient


APP_KEY = '3727112766' # app key
APP_SECRET = 'cd1ce0ba3ce8c7e463019c976533af60' # app secret

def weibo_login(request):
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=_get_weibo_callback_url(request))
    url = client.get_authorize_url()
    return HttpResponseRedirect(url)

def weibo_auth(request):

    # 获取URL参数code:

    code = request.GET.get('code')

    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=_get_weibo_callback_url(request))
    token_obj = client.request_access_token(code)
    client.set_access_token(token_obj.access_token, token_obj.expires_in)

    if request.session.has_key('oauth_access_token'):
        del request.session['oauth_access_token']

    request.session['oauth_access_token'] = { 'uid' : token_obj.uid, 'access_token' : token_obj.access_token, 'expires_in' :  token_obj.expires_in}

    oauth_access_token = request.session.get('oauth_access_token', None)

    back_to_url = reverse('songs.views.my_home')

    if token_obj is not None:
        try:
            w_user = WeiboUser.objects.get(weibo_user_id=oauth_access_token['uid'])
            user = authenticate(weibo_user=w_user)
            if user and user.is_active:
                auth_login(request,user)

        except WeiboUser.DoesNotExist:
            back_to_url = reverse('social.views.create_user_from_weibo')

    return HttpResponseRedirect(back_to_url)

# call back url
def _get_weibo_callback_url(request):
    current_site = get_current_site(request)
    domain = current_site.domain
    url = 'http://%s%s' %(domain, reverse('social_weibo_login_done'))
    return url


def create_user_from_weibo(request, template_name='register/create_user_from_weibo.html'):

    oauth_access_token = request.session.get('oauth_access_token', None)

    if request.user.is_authenticated() or oauth_access_token is None:
        return HttpResponseRedirect(reverse('home.views.index'))

    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=_get_weibo_callback_url(request))
    client.set_access_token(oauth_access_token['access_token'], oauth_access_token['expires_in'])

    weibo_user = client.get.users__show(uid=oauth_access_token['uid'])
    weibo_username = weibo_user.screen_name

    template_var = {}
    form = RegistrationForm(initial={'username': weibo_username })
    if request.method == 'POST':
        form = RegistrationForm(request.POST.copy())
        if request.method == 'POST':
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                user = User.objects.create_user(username,email,password)
                user.is_active = True
                user.save()

                profile = UserProfile()
                profile.user = user
                profile.song_ord_filed = 'post_datetime'
                profile.save()

                #weibo信息记录
                w_user = WeiboUser()
                w_user.user = user

                w_user.weibo_user_id = oauth_access_token['uid']
                w_user.weibo_username = weibo_username
                w_user.oauth_access_token = oauth_access_token['access_token']
                w_user.save()

                #发微博提示
                if request.POST.get('update_msg'):
                    msg = request.POST.get('bind_msg')[0:140]
                    client.post.statuses__update(status=msg)

                user = authenticate(username=username, password=password)
                auth_login(request,user)

                return HttpResponseRedirect(reverse('songs.views.my_home'))

    template_var['form'] = form
    template_var['weibo_username'] = weibo_username
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

def bind_weibo_user(request):

    oauth_access_token = request.session.get('oauth_access_token', None)
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=_get_weibo_callback_url(request))
    client.set_access_token(oauth_access_token['access_token'], oauth_access_token['expires_in'])
    weibo_user = client.get.users__show(uid=oauth_access_token['uid'])
    weibo_username = weibo_user.screen_name

    template_var = {}
    template_var['weibo_username'] = weibo_username
    if request.method == 'POST':
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        if _login(request, email, password) == True:

            #weibo信息记录
            w_user = WeiboUser()
            w_user.user = request.user

            w_user.weibo_user_id = oauth_access_token['uid']
            w_user.weibo_username = weibo_username
            w_user.oauth_access_token = oauth_access_token['access_token']
            w_user.save()

            #发微博提示
            if request.POST.get('update_msg'):
                msg = request.POST.get('bind_msg')[0:140]
                client.post.statuses__update(status=msg)

            return HttpResponseRedirect(reverse('songs.views.my_home'))
        else:

            template_var['login_failure'] = True
            template_var['input_email'] = email
            return auth_login_view(request, template_name='register/bind_weibo_user.html', extra_context=template_var)
    else:
        return auth_login_view(request, template_name='register/bind_weibo_user.html', extra_context=template_var)

def _post_weibo(request, msg, url=None):
    oauth_access_token = request.session.get('oauth_access_token', None)
    if oauth_access_token:
        client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=_get_weibo_callback_url(request))
        client.set_access_token(oauth_access_token['access_token'], oauth_access_token['expires_in'])
        if url:
            short_url = client.get.short_url__shorten(url_long=url)['urls'][0]['url_short']
        else:
            short_url = ''

        message = msg + short_url;
        if len(message) > 140:
            msg_count = 140 - len(short_url)
            message = msg[0:msg_count] + short_url

        client.post.statuses__update(status=message)