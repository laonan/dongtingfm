# coding=utf-8
from django.contrib import admin
from sns.models import UserFollower, PrivateMailThread, PrivateMail, BlackList

class UserFollowerAdmin(admin.ModelAdmin):
    list_display = ('pk','user', 'follower')
    ordering = ('-user',)
    search_fields = ('user__username',)
admin.site.register(UserFollower, UserFollowerAdmin)

class PrivateMailThreadAdmin(admin.ModelAdmin):
    list_display = ('pk','user', 'conversational_partner', 'latest_datetime')
    ordering = ('-latest_datetime',)
    search_fields = ('all_read',)
admin.site.register(PrivateMailThread, PrivateMailThreadAdmin)

class PrivateMailAdmin(admin.ModelAdmin):
    list_display = ('pk','user', 'from_user', 'to_user', 'sent_datetime')
    ordering = ('-sent_datetime',)
    search_fields = ('is_read',)
admin.site.register(PrivateMail, PrivateMailAdmin)

class BlackListAdmin(admin.ModelAdmin):
    list_display = ('pk','user', 'bad_guy')
    ordering = ('user',)
    search_fields = ('user__username',)
admin.site.register(BlackList, BlackListAdmin)

