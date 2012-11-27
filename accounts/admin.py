# coding=utf-8
from django.contrib import admin
from accounts.models import UserProfile, WeiboUser
#admin.site.register(UserProfile)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('pk','user', 'avatar', 'website', 'qq', 'msn')
    list_filter = ('city',)
    ordering = ('-user',)
    search_fields = ('user__username',)
admin.site.register(UserProfile, UserProfileAdmin)

class WeiboUserAdmin(admin.ModelAdmin):
    list_display = ('pk','user', 'weibo_username', 'weibo_user_id', 'create_datetime')
    list_filter = ('weibo_username',)
    ordering = ('-create_datetime',)
    search_fields = ('user__username',)
admin.site.register(WeiboUser, WeiboUserAdmin)
