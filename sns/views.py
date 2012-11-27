# coding=utf-8
import datetime
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _

from accounts.models import UserProfile
from sns.models import UserFollower, BlackList, PrivateMail, PrivateMailThread

@login_required(login_url='/login')
def user_followers(request, uid, template_name):
    
    followers = _get_follows(request, uid, 'get_follower')
    
    profile = request.user.get_profile()
    profile.new_followers = 0
    profile.save()
    
    template_var = {}
    template_var['followers'] = followers
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def user_following(request, uid, template_name):
    followers = _get_follows(request, uid, 'get_following')
    template_var = {}
    template_var['followers'] = followers
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def _get_follows(request, uid, action):
    u = User.objects.get(id=uid)
    if action == 'get_following':
        #followers = UserFollower.objects.select_related().filter(follower=u)
        followers = UserFollower.objects.select_related().extra(select={'follower_userprofile_avatar':'accounts_userprofile.avatar', 'follower_userprofile_city':'accounts_userprofile.city', 'follower_userprofile_intro':'accounts_userprofile.intro'},
                                                                tables=['sns_userfollower','accounts_userprofile'],
                                                                where=['accounts_userprofile.user_id=sns_userfollower.user_id AND sns_userfollower.follower_id=%s' % uid])

    else:
        #followers = UserFollower.objects.select_related().filter(user=u)
        followers = UserFollower.objects.select_related().extra(select={'follower_userprofile_avatar':'accounts_userprofile.avatar', 'follower_userprofile_city':'accounts_userprofile.city', 'follower_userprofile_intro':'accounts_userprofile.intro'},
                                                                tables=['sns_userfollower','accounts_userprofile'],
                                                                where=['accounts_userprofile.user_id=sns_userfollower.follower_id AND sns_userfollower.user_id=%s' % uid])
        
    paginator = Paginator(followers, 15)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    try:
        followers = paginator.page(page)
    except (EmptyPage, InvalidPage):
        followers = paginator.page(paginator.num_pages)
        
    return followers;

@login_required(login_url='/login')
def follow_user(request):
    jsonData = None
    if request.is_ajax():
        u_id = request.GET.get('following_userid', -1)
        if u_id == -1:
            return HttpResponse('{"excuted": false}')
        
        u = User.objects.get(id=u_id)
        followers = UserFollower.objects.filter(user=u, follower = request.user)
           
        if not followers:
            my_blacklist = BlackList.objects.filter(user=request.user, bad_guy=u)
            target_blacklist = BlackList.objects.filter(user=u, bad_guy=request.user)
                
            if my_blacklist or target_blacklist:
                return HttpResponse('{"excuted": false}')
                
            user_profile =  u.get_profile()
            user_profile.followers = user_profile.followers + 1
            user_profile.new_followers = user_profile.new_followers + 1
            user_profile.save()
                
            
            my_profile = request.user.get_profile()
            my_profile.following = my_profile.following +1    
            my_profile.save()
                
            user_follower = UserFollower()
            user_follower.user = u
            user_follower.follower = request.user
            user_follower.save()
                
            jsonData = '{"excuted": true, "action": "follow", "followers": %s}' % user_profile.followers
        else:
            #取消关注
            user_profile =  u.get_profile()
            user_profile.followers = user_profile.followers - 1
            user_profile.save()
                
            my_profile = request.user.get_profile()
            my_profile.following = my_profile.following - 1
            my_profile.save()
                
            followers[0].delete()
                
            jsonData = '{"excuted": true, "action": "unfollow", "followers": %s}' % user_profile.followers
            
    return HttpResponse(jsonData)

@login_required(login_url='/login')
def remove_follower(request):
    jsonData = '{"excuted": false}'
    if request.is_ajax():
        u_id = request.GET.get('follower_userid', -1)
        if u_id != -1:
            u = User.objects.get(id=u_id)
            following = UserFollower.objects.filter(user=request.user, follower = u )
            if following:
                
                user_profile =  u.get_profile()
                user_profile.following = user_profile.following - 1
                user_profile.save()
                
                my_profile = request.user.get_profile()
                my_profile.followers = my_profile.followers - 1
                my_profile.save()
              
                following[0].delete()
                
                jsonData = '{"excuted": true, "action": "removefollower"}'
            
    return HttpResponse(jsonData)

@login_required(login_url='/login')
def get_blacklist(request, template_name):
    #blacklist = BlackList.objects.select_related().filter(user=request.user)
    blacklist = BlackList.objects.select_related().extra(select={'blacklist_userprofile_avatar':'accounts_userprofile.avatar', 'blacklist_userprofile_city':'accounts_userprofile.city'},
                                                         tables=['accounts_userprofile'],
                                                         where=['accounts_userprofile.user_id=sns_blacklist.bad_guy_id AND sns_blacklist.user_id=%s' % request.user.id])
   
    paginator = Paginator(blacklist, 15)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    try:
        blacklist = paginator.page(page)
    except (EmptyPage, InvalidPage):
        blacklist = paginator.page(paginator.num_pages)
        
    template_var = {}
    template_var['blacklist'] = blacklist
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def bad_guy(request):
    if request.is_ajax():
        uid = request.GET.get('uid', -1)
        try:
            bad_guy = User.objects.get(id=uid)
            
            black_list = BlackList.objects.filter(user=request.user, bad_guy=bad_guy)
            if black_list:
                black_list[0].delete()

                jsonData = '{"excuted": true, "action": "delete"}'
            else:
                black_list = BlackList()
                black_list.user = request.user
                black_list.bad_guy = bad_guy
                black_list.save()
                
                #移除关注和被关注
                follower = UserFollower.objects.filter(user=request.user, follower=bad_guy)
                if follower:
                    follower[0].delete()
                    my_profile = request.user.get_profile()
                    my_profile.followers = my_profile.followers -1
                    my_profile.save()
                    
                    target_profile = bad_guy.get_profile()
                    target_profile.following = target_profile.following -1
                    target_profile.save()
                
                following = UserFollower.objects.filter(user=bad_guy, follower=request.user)
                if following:
                    following[0].delete()
                    my_profile = bad_guy.get_profile()
                    my_profile.followers = my_profile.followers -1
                    my_profile.save()
                    
                    target_profile = request.user.get_profile()
                    target_profile.following = target_profile.following -1
                    target_profile.save()
                
                jsonData = '{"excuted": true, "action": "add"}'
            
        except User.DoesNotExist:
            jsonData = u'{"excuted": false, "msg": "用户不存在"}'
            
        return HttpResponse(jsonData)
    else:
        return HttpResponse('')

@login_required(login_url='/login')
def private_mails(request, template_name):
    threads = PrivateMailThread.objects.extra(select={'partner_avatar':'SELECT avatar FROM accounts_userprofile WHERE user_id=sns_privatemailthread.conversational_partner_id', 'partner_username':'SELECT username FROM auth_user WHERE id=sns_privatemailthread.conversational_partner_id'},
                                              tables=['sns_privatemailthread','auth_user','accounts_userprofile'],
                                              where=['sns_privatemailthread.user_id = auth_user.id AND auth_user.id=accounts_userprofile.user_id AND sns_privatemailthread.user_id=%s' % request.user.id]).order_by('all_read', '-latest_datetime')
    
    paginator = Paginator(threads, 15)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    try:
        threads = paginator.page(page)
    except (EmptyPage, InvalidPage):
        threads = paginator.page(paginator.num_pages)
    
    template_var = {}
    template_var['threads'] = threads
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

def mails_details(request, thread_id, template_name):
     ts = PrivateMailThread.objects.select_related('userprofile__avatar','user__username').filter(user=request.user.id, id=thread_id)
     ts.update(all_read = True)
     
     template_var = {}
     if ts:
        t = ts[0]
        template_var['thread'] = ts[0];
        template_var['current_user_avatar'] = request.user.get_profile().avatar
        template_var['partner_avatar'] = t.conversational_partner.get_profile().avatar
        template_var['partner_username'] = t.conversational_partner.username
     
    
        in_my_blacklist = BlackList.objects.filter(user=request.user,bad_guy__id=t.conversational_partner_id)
        in_target_blacklist = BlackList.objects.filter(user__id=t.conversational_partner_id,bad_guy=request.user)
     
        if in_my_blacklist:
            template_var['in_blacklist'] = True
            template_var['blacklist_msg'] = u'不能跟对方对话，你已经把对方拉黑。'
         
        if in_target_blacklist:
            template_var['in_blacklist'] = True
            template_var['blacklist_msg'] = u'不能跟对方对话，对方已经把你拉黑。'
     
     mails = PrivateMail.objects.filter(thread__id = thread_id, user=request.user)
        
     if mails:
        mails.update(is_read=True) 
        
        paginator = Paginator(mails, 15)
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
            
        try:
            mails = paginator.page(page)
        except (EmptyPage, InvalidPage):
            mails = paginator.page(paginator.num_pages)
            
        template_var['mails'] = mails
         
    
     return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def send_private_mail(request, template_name):
    
    if request.method == 'POST' and request.user.is_authenticated() and request.is_ajax():
        user_name = request.POST.get('to_user',None)
        content = request.POST.get('mail_content',None).strip()
        if content == '' or content == None:
            return HttpResponse(u'{"sent": false, "msg": "内容为空!"}')
            
        if user_name == request.user.username:
            return HttpResponse(u'{"sent": false, "msg": "请不要给自己发私信。"}')
            
        try:
            to_user = User.objects.get(username=user_name)
                    
            #check it if it's in blacklist
            my_bad_guy = BlackList.objects.filter(user=request.user,bad_guy=to_user)
            target_bad_guy = BlackList.objects.filter(user=to_user,bad_guy=request.user)
                    
            if my_bad_guy:
                return HttpResponse(u'{"sent": false, "msg": "发送失败，你已经把对方拉黑!"}')
                    
            if target_bad_guy:
                return HttpResponse(u'{"sent": false, "msg": "发送失败，对方已经把你拉黑!"}')
                    
            # from user's thread
            threads = PrivateMailThread.objects.filter(user=request.user, conversational_partner=to_user)
            if threads:
                thread = threads[0]
                thread.mails = thread.mails + 1
            else:
                thread = PrivateMailThread()
                thread.user = request.user
                thread.conversational_partner = to_user
                thread.mails = 1
                thread.all_read = True
                    
            thread.latest_sender = request.user
            thread.latest_content = content
            thread.latest_datetime = datetime.datetime.now()
            thread.save()
                    
            mail = PrivateMail()
            mail.user = request.user
            mail.from_user = request.user
            mail.to_user = to_user
            mail.content = content
            mail.thread = thread
            mail.is_read = True
            mail.save()
            
            # to user thread  
            threads1 = PrivateMailThread.objects.filter(user=to_user, conversational_partner=request.user)
            if threads1:
                thread1 = threads1[0]
                thread1.mails = thread1.mails + 1
            else:
                thread1 = PrivateMailThread()
                thread1.user = to_user
                thread1.conversational_partner = request.user
                thread1.mails = 1
                    
            thread1.all_read = False
            thread1.latest_sender = request.user
            thread1.latest_content = content
            thread1.latest_datetime = datetime.datetime.now()
            thread1.save()
                    
            mail1 = PrivateMail()
            mail1.user = to_user
            mail1.from_user = request.user
            mail1.to_user = to_user
            mail1.content = content
            mail1.thread = thread1
            mail1.save()
                    
            jsonData = '{"sent": true}'
        except User.DoesNotExist:
            jsonData = u'{"sent": false, "msg": "用户不存在，请重新输入，一次只能给一个人发送私信。"}'
            
        return HttpResponse(jsonData);
    else:
        uid = request.GET.get('to_uid', -1)
        template_var = {}
        try:
            u = User.objects.get(id=uid)
            template_var['to_username'] = u.username
        except User.DoesNotExist:
            template_var['to_username'] = u'请输入昵称...'
        return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def del_private_mail_thread(request):
    if request.is_ajax() and request.user.is_authenticated():
        thread_id = request.GET.get('thread_id', -1)
        try:
            thread = PrivateMailThread.objects.get(id=thread_id)
            if thread.user == request.user:
                thread.delete()
                jsonData = '{"deleted": true}'
            else:
                jsonData = '{"deleted": false}'
            
        except PrivateMailThread.DoesNotExist:
            jsonData = '{"deleted": false}'
            
        return HttpResponse(jsonData)
    else:
        return HttpResponse('')

@login_required(login_url='/login')
def del_mail(request):
    if request.is_ajax() and request.user.is_authenticated():
        mail_id = request.GET.get('mail_id', -1)
        try:
            mail = PrivateMail.objects.get(id=mail_id)
            if mail.user == request.user:
                mail.thread.mails = mail.thread.mails - 1 
                mail.thread.save()
                if mail.thread.mails == 0:
                    mail.thread.delete()
                    jsonData = '{"deleted": true, "del_thread": true}'
                else:
                    mail.delete()
                    jsonData = '{"deleted": true, "del_thread": false}'
            else:
                jsonData = '{"deleted": false}'
        except PrivateMail.DoesNotExist:
            jsonData = '{"deleted": false}'
            
        return HttpResponse(jsonData)
    else:
        return HttpResponse('')

@login_required(login_url='/login')
def private_mails_count(request):
    if request.is_ajax() and request.user.is_authenticated():
        all_mails = PrivateMail.objects.filter(user=request.user).count()
        unread_mails = PrivateMail.objects.filter(user=request.user, is_read=False).count()
        
        jsonData = '{"all_mails": %s, "unread_mails": %s}' % (all_mails, unread_mails)
        return HttpResponse(jsonData)
    else:
        return HttpResponse('')
    
@login_required(login_url='/login')
def get_people_list(request, template_name):
    
    user_profiles = UserProfile.objects.select_related().exclude(user=request.user).order_by('?')
    
    paginator = Paginator(user_profiles, 15)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    try:
        user_profiles = paginator.page(page)
    except (EmptyPage, InvalidPage):
        user_profiles = paginator.page(paginator.num_pages)
        
    template_var = {}
    template_var['people'] = user_profiles
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def invite_people_by_email(request, template_name):
    
    sent_mails = 0
    failed_mails = 0
    ret = False
    if request.method == 'POST':
        mails = request.POST.get('mails_content').split(';')
        
        from django.core.mail import send_mail
        email_template_name = 'sns/invite_email.html'
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        use_https = False
       
        t = loader.get_template(email_template_name)
        c = {
            'domain': domain,
            'site_name': site_name,
            'user': request.user,
            'protocol': use_https and 'https' or 'http',
            }
      
        for mail in mails:
            try:
                send_mail(_(u'您的朋友%s邀请您加入%s') % (request.user.username, site_name),
                          t.render(Context(c)), None, [mail])
                sent_mails = sent_mails + 1
            except:
                failed_mails = failed_mails + 1
                
        ret = True
            
    template_var = {}
    template_var['ret'] = ret
    template_var['msg'] = u'发送邀请邮件成功%s，失败%s。' % (sent_mails, failed_mails)
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))