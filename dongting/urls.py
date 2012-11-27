# coding=utf-8
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import login, password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from django.views.generic import RedirectView
from django.views import generic
from django.views.generic import TemplateView

from home.views import index
from accounts.views import register, register_complete, check_email, check_user, check_another_user, ajax_login, active_user, reactive, reactive_done, sign_in, sign_out, user_settings, change_password, set_songs_ord
from common.views import get_single_captcha
from sns.views import follow_user, remove_follower, user_followers, user_following, bad_guy, get_blacklist, private_mails, send_private_mail, del_private_mail_thread, private_mails_count, mails_details, del_mail, get_people_list, invite_people_by_email
from songs.views import add_music, get_mp3_info, get_song_cover, upload_artist_headshot, song_details, song_edit, song_list, dig, bury, comment, del_comment, comments, get_unread_comments, favorite, my_home, my_songs, my_favorites, songs_by_user, song_digs, search, radio, public_radio, radio_dig
from api.views import android_login

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^dongting/', include('dongting.foo.urls')),

    #Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^hello-dongting-fm/', include(admin.site.urls)),
    
    url(r'^favicon\.ico$', RedirectView.as_view(url= '/static/images/favicon.ico')),
    
    url(r'^$', index, { 'template_name' : 'p_home.html'}),
    url(r'^my-home/$', my_home, { 'template_name' : 'p_home.html'}),
    url(r'^search$', search, { 'template_name' : 'p_home.html'}),
    
    url(r'^accounts/register/$', register, { 'template_name' : 'register/p_register.html'}),
    url(r'^accounts/register-complete/$', register_complete, { 'template_name' : 'register/p_register_complete.html'}),
    url(r'^login$',  sign_in, name='sign_in'),
    url(r'^accounts/login/$',  login, { 'template_name' : 'register/login.html'}),
    url(r'^accounts/ajax-login/$', ajax_login),
    url(r'^accounts/logout/$', sign_out, { 'template_name' : 'register/logged_out.html'}),
    url(r'^profile/settings/$', user_settings),
    url(r'^accounts/password-reset/$', password_reset, { 'template_name' : 'register/password_reset_form.html'}),
    url(r'^accounts/password-reset/done/$', password_reset_done, { 'template_name' : 'register/password_reset_done.html'}),
    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, { 'template_name' : 'register/password_reset_confirm.html'}),
    url(r'^accounts/reset/done/$', password_reset_complete, { 'template_name' : 'register/password_reset_complete.html'}),
    url(r'^accounts/active/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', active_user, { 'template_name' : 'register/activation_confirm.html'}),
    url(r'^accounts/reactive/$', reactive, { 'template_name' : 'register/activation_reset_form.html'}),
    url(r'^accounts/reactive/done/$', reactive_done, { 'template_name' : 'register/activation_reset_done.html'}),
    url(r'^change-password$', change_password),
    url(r'^emailexists$', check_email),
    url(r'^userexists$', check_user),
    url(r'^another-user-exists$', check_another_user),
    url(r'^set-songs-ord$', set_songs_ord),
    
    #apis
    url(r'^api/login/android$', android_login),
    
    url(r'^follow$', follow_user),
    url(r'^remove-follower$', remove_follower),
    url(r'^(?P<uid>\d+)/followers/$', user_followers, { 'template_name' : 'sns/follower_list.html'}),
    url(r'^(?P<uid>\d+)/following/$', user_following, { 'template_name' : 'sns/following_list.html'}),
     
    url(r'^song/(?P<song_id>\d+)/$', song_details, { 'template_name' : 'songs/song_details.html'}),
    url(r'^song/(?P<song_id>\d+)/edit/$', song_edit, { 'template_name' : 'songs/song_edit.html'}),
    
    url(r'^radio/(?P<uid>\d+)/$', radio, { 'template_name' : 'songs/radio.html'}),
    url(r'^radio/$', radio, { 'template_name' : 'songs/radio.html'}),
    url(r'^selected-song/(?P<song_id>\d+)/$', public_radio, { 'template_name' : 'songs/public_radio.html'}),
    url(r'^people/(?P<uid>\d+)/$', songs_by_user, { 'template_name' : 'p_home.html'}),
    url(r'^people$', get_people_list, { 'template_name' : 'sns/people_list.html'}),
    url(r'^invite-friends/$', invite_people_by_email, { 'template_name' : 'sns/invite_friends.html'}),
    
    url(r'^songs/(?P<genre_code>[\w|-]+)/$', song_list, { 'template_name' : 'p_home.html'}),
    url(r'^my-songs/$', my_songs, { 'template_name' : 'p_home.html'}),
    url(r'^my-favorites/$', my_favorites, { 'template_name' : 'p_home.html'}),
    url(r'^add-music/$', add_music, { 'template_name' : 'songs/add_music.html'}),
    url(r'^get-mp3-info$', get_mp3_info),
    url(r'^get-song-cover$', get_song_cover),
    url(r'^upload-artist-headshot$', upload_artist_headshot),
    url(r'^song-digs/(?P<song_id>\d+)/$', song_digs, { 'template_name' : 'songs/song_digs.html'}),
    url(r'^dig$', dig),
    url(r'^radio-dig$', radio_dig),
    url(r'^bury$', bury),
    url(r'^favorite/(?P<action_name>\w+)/$', favorite),
    url(r'^comment/$', comment),
    url(r'^comments/', comments, { 'template_name' : 'songs/comments.html'}),
    url(r'^del-comment$', del_comment),
    url(r'^get-unread-comments$', get_unread_comments),
    
    url(r'^captcha/', include('captcha.urls')),
    url(r'^singlecaptcha$', get_single_captcha, { 'template_name' : 'ajax_captcha.html'}),

    url(r'^dialog/del-private-mail-thread/$', TemplateView.as_view(template_name='dialog/del_private_mail_thread.html'), name='del_mail_thread_dialog'),
    url(r'^dialog/add-to-blanklist/$', TemplateView.as_view(template_name='dialog/add_to_blacklist.html'), name='add_to_blacklist'),
    url(r'^dialog/del-comment/$', TemplateView.as_view(template_name='dialog/del_comment.html'), name='del_comment'),
    url(r'^dialog/del-mail/$', TemplateView.as_view(template_name='dialog/del_mail.html'), name='del_mail'),
    url(r'^dialog/remove-follow/$', TemplateView.as_view(template_name='dialog/remove_follow.html'), name='remove_follow'),
    url(r'^dialog/remove-from-blacklist/$', TemplateView.as_view(template_name='dialog/remove_from_blacklist.html'), name='remove_from_blacklist'),

    url(r'^send-private-mail', send_private_mail, { 'template_name' : 'sns/send_private_mail.html'}),
    url(r'^del-mail-thread', del_private_mail_thread),
    url(r'^del-mail', del_mail),
    url(r'^private-mails-count', private_mails_count),
    url(r'^private-mails/$', private_mails, { 'template_name' : 'sns/private_mails.html'}),
    url(r'^mails/(?P<thread_id>\d+)/', mails_details, { 'template_name' : 'sns/mails_details.html'}),
    
    url(r'^bad-guy/$', bad_guy),
    url(r'^blacklist/$', get_blacklist, { 'template_name' : 'sns/blacklist.html'}),
    url(r'^ie6/$', generic.TemplateView.as_view(template_name='ie6.html'),name='ie6-page'),

    url(r'^player-logs/$', 'songs.views.player_logs', name="record_player_logs"),
    url(r'^radio-song/$', 'songs.views.get_random_song', name='public_radio_song'),
    url(r'^radio-song/(?P<user_id>\d+)/$', 'songs.views.get_random_song', name='user_radio_song'),
)

urlpatterns += staticfiles_urlpatterns()

#weibo.com oauth2.0
urlpatterns += patterns('social.views',
    url(r'^weibo/login/$', 'weibo_login', name='social_weibo_login'),
    url(r'^weibo/login/done/$', 'weibo_auth', name='social_weibo_login_done'),
    url(r'^weibo/user/creat/$', 'create_user_from_weibo', name='create_user_from_weibo'),
    url(r'^weibo/user/bind/$', 'bind_weibo_user', name='bind_weibo_user'),
)

#在生产环境 中，static和media都应该直接在apache里配置好
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )