# coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.forms import widgets
from django.template import Context, loader
from django.utils.http import int_to_base36
from django.utils.translation import ugettext_lazy as _

from accounts.models import UserProfile
from captcha.fields import CaptchaField


class RegistrationForm(forms.Form):
    email = forms.EmailField( max_length = 30, widget = widgets.TextInput(attrs={'class': 'validate[required,custom[email],ajax[ajaxEmailCall]] text-input'}))
    password = forms.CharField( max_length = 30, widget = widgets.PasswordInput(attrs={'class': 'validate[required,minSize[6]] text-input'}))
    password1 = forms.CharField( max_length = 30, widget = widgets.PasswordInput(attrs={'class': 'validate[required,equals[id_password]] text-input'}))
    username = forms.CharField( max_length = 30, widget = widgets.TextInput(attrs={'class': 'validate[required,minSize[2],ajax[ajaxUserCall]] text-input'}))
    captcha = CaptchaField()
    
    def clean_username(self):
        '''验证重复昵称'''
        users = User.objects.filter(username__iexact=self.cleaned_data["username"])
        if not users:
            return self.cleaned_data["username"]
        raise forms.ValidationError(_(u"此昵称已被注册"))
        
    def clean_email(self):
        '''验证重复email'''
        emails = User.objects.filter(email__iexact=self.cleaned_data["email"])
        if not emails:
            return self.cleaned_data["email"]
        raise forms.ValidationError(_(u"此邮箱已经被注册"))
    
    def clean(self):
        password = self.cleaned_data.get('password', '').strip()
        password1 = self.cleaned_data.get('password1','').strip()
        if password and password1 and password != password1:
            del self.cleaned_data["password1"]
            raise forms.ValidationError(_(u"两次密码输入不一致"))
        return self.cleaned_data
    
class UserSettingsForm(forms.Form):
    original_username = forms.CharField(widget=forms.HiddenInput())
    username = forms.CharField( max_length = 30, widget = widgets.TextInput(attrs={'class': 'validate[required,minSize[2],ajax[ajaxAnotherUserCall]] text-input'}))
    city = forms.CharField( max_length = 30, required=False)
    website = forms.URLField( max_length = 200, required=False, widget = widgets.TextInput(attrs={'class': 'validate[custom[url]] text-input'}))
    intro = forms.CharField( max_length = 140, required=False, widget=forms.Textarea(attrs={'class': 'validate[maxSize[140]]'}))
    qq = forms.CharField( max_length = 30, required=False)
    msn = forms.EmailField( max_length = 30, required=False, widget = widgets.TextInput(attrs={'class': 'validate[custom[email]] text-input'}))
    avatar = forms.ImageField(required=False)
    
    def clean_avatar(self):
          f = self.cleaned_data["avatar"]
          if f:
              if f.content_type != 'image/jpeg' and f.content_type != 'image/gif' and f.content_type != 'image/png':
                  raise forms.ValidationError(u'图片格式错误，只支持JPG, GIF和PNG格式的图片。')
                
              if f.size > 2000*1024:
                  raise forms.ValidationError(u'图片太大，最多只允许上传2MB的图片文件。')
          
          return self.cleaned_data["avatar"]
    
    def clean_username(self):
        original_username = self.cleaned_data.get('original_username', '').strip()
        username = self.cleaned_data.get('username', '').strip()
        users = User.objects.filter(username__iexact=username)
        if users and users[0].username != original_username:
            del self.cleaned_data['username']
            raise forms.ValidationError(_(u'该用户名已被占用，请换一个用户名'))
        else:
            return self.cleaned_data['username']
    
    def save(self,request):
        if self.cleaned_data['city'] or self.cleaned_data['website'] or self.cleaned_data['intro'] or self.cleaned_data['qq'] or self.cleaned_data['msn'] or self.cleaned_data['avatar']:
           
            current_user = request.user
           
            try:
                profile = current_user.get_profile()
            except UserProfile.DoesNotExist:
                profile = None
            
            if not profile:
                profile = UserProfile()
                profile.user = current_user
                profile.song_ord_filed = 'post_datetime'
                
            profile.city = self.cleaned_data['city']
            profile.website = self.cleaned_data['website']
            profile.intro = self.cleaned_data['intro']
            profile.qq = self.cleaned_data['qq']
            profile.msn = self.cleaned_data['msn']
            if 'avatar' in request.FILES:
                
                #删除掉原头像
                import os
                if profile and profile.avatar and os.path.exists(profile.avatar.path):
                    os.remove(profile.avatar.path)
                                 
                profile.avatar = self.cleaned_data['avatar']#request.FILES["avatar"]
            profile.save()
            
            if self.cleaned_data['username'] != current_user.username:
                current_user.username = self.cleaned_data['username']
                current_user.save()
    
class ReactiveForm(forms.Form):
    email = forms.EmailField(label=_("E-mail"), max_length=75)

    def clean_email(self):
        """
        Validates that an active user exists with the given e-mail address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = User.objects.filter(
                                email__iexact=email,
                                is_active=False
                            )
        if len(self.users_cache) == 0:
            raise forms.ValidationError(_("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
        return email

    def save(self, domain_override=None, email_template_name='register/activation_email.html',
             use_https=False, token_generator=default_token_generator, from_email=None, request=None):
        from django.core.mail import send_mail
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        use_https = False
        user = self.users_cache[0]
               
        t = loader.get_template(email_template_name)
        c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
        send_mail(_(u'%s：激活账户') % site_name,
                  t.render(Context(c)), None, [user.email])