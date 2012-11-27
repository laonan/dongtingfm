# coding=utf-8
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import login

from django.contrib.sites.models import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.http import int_to_base36, base36_to_int
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView

from accounts.conf import settings as accounts_settings
from accounts.models import UserProfile
from accounts.forms import RegistrationForm, ReactiveForm, UserSettingsForm


def register(request,template_name='register/p_register.html'):
    
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('views.home'))
    
    template_var={}
    form = RegistrationForm()    
    if request.method == 'POST':
        form = RegistrationForm(request.POST.copy())
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username,email,password)
            if accounts_settings.USER_ACTIVE_BY_EMAIL == True:
                user.is_active = False
            user.save()
            if accounts_settings.USER_ACTIVE_BY_EMAIL == False:
                #if it's unnecessary to active by email, login directly.
                _login(request, email, password) 
                return HttpResponseRedirect(reverse('views.home'))
            else:
                """
                Generates a one-use only link for activation and sends to the user
                """
                from django.core.mail import send_mail
                email_template_name = 'register/activation_email.html'
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
                use_https = False
               
                t = loader.get_template(email_template_name)
                c = {
                    'email': user.email,
                    'domain': domain,
                    'site_name': site_name,
                    'uid': int_to_base36(user.id),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                    'protocol': use_https and 'https' or 'http',
                    }
                
                try:
                    send_mail(_(u'%s：激活账户') % site_name,
                              t.render(Context(c)), None, [user.email])
                    return HttpResponseRedirect(reverse('accounts.views.register_complete'))
                except:
                    user.delete()
                    return TemplateView.as_view(template_name='register/register_fail.html')
                    
            
    template_var['form'] = form
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

def register_complete(request, template_name):
     template_var={}
     return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@csrf_protect
@never_cache
def active_user(request, uidb36=None, token=None,
                         template_name='register/activation_confirm.html',
                         token_generator=default_token_generator,
                         current_app=None, extra_context=None):
    """
    View that checks the hash in a active user link and make user to be active
    """
    assert uidb36 is not None and token is not None # checked by URLconf
   
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        user.is_active = True
        user.save()
        
        #初始化userprofile
        profile_count = UserProfile.objects.filter(user=user).count()
        if profile_count == 0:
            profile = UserProfile()
            profile.user = user
            profile.song_ord_filed = 'post_datetime'
            profile.save()
    else:
        validlink = False
    context = {
        'validlink': validlink,
    }
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))
    
@csrf_protect
def reactive(request, is_admin_site=False,
                   template_name='register/activation_reset_form.html',
                   email_template_name='register/activation_email.html',
                   reactive_form=ReactiveForm,
                   token_generator=default_token_generator,
                   post_reactive_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None):
    if post_reactive_redirect is None:
        post_reactive_redirect = reverse('accounts.views.reactive_done')
    if request.method == "POST":
        form = reactive_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.META['HTTP_HOST'])
            form.save(**opts)
            return HttpResponseRedirect(post_reactive_redirect)
    else:
        form = reactive_form()
    context = {
        'form': form,
    }
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))

def reactive_done(request,
                        template_name='register/activation_reset_done.html',
                        current_app=None, extra_context=None):
    context = {}
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))

def sign_in(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        remember_me = request.POST.get('remember_me', None)
        if _login(request, email, password) == True:
            
            #如果没选择记住登录状态，则设置session一退出浏览器便过期
            if not remember_me:
                request.session.set_expiry(0)

            next_url = request.GET.get('next', reverse('songs.views.my_home'))
            return HttpResponseRedirect(next_url)
        else:
            template_var = {}
            template_var['login_failure'] = True
            template_var['input_email'] = email
            return login(request, template_name='register/sign_in.html', extra_context=template_var)
    else:
        template_var={}
        return login(request, template_name='register/sign_in.html', extra_context=template_var)
            
def sign_out(request, template_name):
     #用户登出，直接删除access_token
    auth_logout(request)
    access_token = request.session.get('oauth_access_token', None)
    if access_token is not None:
        del request.session['oauth_access_token']
    template_var = {}
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def user_settings(request, template_name='profile/user_settings.html'):
    '''edit user's profile view'''
    template_var={}
    form = UserSettingsForm()
    avatar_url = None
    if request.method == 'POST':
        form = UserSettingsForm(request.POST.copy(), request.FILES)
        if form.is_valid():
            opts = {
                      'request': request,
                   }
            form.save(**opts)
            avatar_url = request.user.get_profile().avatar
    else:
        current_user = request.user
        
        try:
            current_profile = current_user.get_profile()#UserProfile.objects.get( user__exact = current_user )
            avatar_url = current_profile.avatar
        except UserProfile.DoesNotExist:
            current_profile = None
            
        initial_dict = { 'original_username': current_user.username,
                         'username': current_user.username,
                         'city':  None if current_profile==None else current_profile.city,
                         'avatar':  None if current_profile==None else current_profile.avatar,
                         'website':  None if current_profile==None else current_profile.website,
                         'qq':  None if current_profile==None else current_profile.qq,
                         'msn':  None if current_profile==None else current_profile.msn,
                         'intro':  None if current_profile==None else current_profile.intro
                       }
            
        form = UserSettingsForm(initial = initial_dict)
        
    template_var['form'] = form
    template_var['avatar_url'] = avatar_url
    #检测是不是新浪微博主
    access_token = request.session.get('oauth_access_token', None)
    if access_token is not None:
        template_var['weibo_user_ret'] = True
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))
    

def ajax_login(request):
    if request.is_ajax():
        email = request.GET.get('email', None)
        password = request.GET.get('password', None)
        remember_me = request.GET.get('remember_me', None)
        if _login(request, email, password) == True:
            
            #如果没选择记住登录状态，则设置session一退出浏览器便过期
            if not remember_me:
                request.session.set_expiry(0)
                
            return_data = '[true]'
        else:
            return_data = '[false]'
    else:
        return_data = ''
    
    return HttpResponse(return_data, mimetype="text/plain")

#inner methods
def _login(request,email,password):
    user = authenticate(email=email, password=password)
    ret = False
    if user and user.is_active:
        auth_login(request,user)
        ret = True

    return ret

def check_email(request):
    if request.is_ajax():
        fieldId = request.GET.get('fieldId', None)
        email = request.GET.get('fieldValue', None)
        emails = User.objects.filter( email__iexact = email )
        if not emails:
            data = '["%s",true]' %fieldId
        else:
            data = '["%s",false]' %fieldId
    else:
        data = ''
    return HttpResponse(data)

def check_user(request):
    if request.is_ajax():
        fieldId = request.GET.get('fieldId', None)
        username = request.GET.get('fieldValue', None)
        users = User.objects.filter( username__iexact = username )
        if not users:
            data = '["%s",true]' %fieldId
        else:
            data = '["%s",false]' %fieldId
    else:
        data = ''
    return HttpResponse(data)

def check_another_user(request):
    if request.is_ajax():
        fieldId = request.GET.get('fieldId', None)
        username = request.GET.get('fieldValue', None)
        users = User.objects.filter( username__iexact = username )
        if users and users[0].username != request.user.username:
            data = '["%s",false]' %fieldId
        else:
            data = '["%s",true]' %fieldId
    else:
        data = ''
    return HttpResponse(data)

@login_required(login_url='/login')
def change_password(request):
    data = ''
    if request.is_ajax():
        old_password = request.POST.get('old_password', None)
        if old_password:
            user = authenticate(username=request.user.username, password=old_password)
            if user:
                new_password = request.POST.get('new_password', None)
                user.set_password(new_password)
                user.save()
                data = '{"changed": true}'
            else:
                data = u'{"changed" : false, "msg" : "原密码错误"}'
        else:
            data = u'{"changed" : false, "msg" : "请输入原密码"}' 
    
    return HttpResponse(data)

@login_required(login_url='/login')
def set_songs_ord(request):
    data = '{"saved": false}'
    if request.is_ajax():
        ord_field = request.POST.get('rd_ord',None)
        if ord_field:
            profile = request.user.get_profile()
            profile.song_ord_filed = ord_field
            profile.save()
            
            data = '{"saved": true}'
            
    return HttpResponse(data)
                
                
        
