# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import force_unicode

class UserFollower(models.Model):
    user = models.ForeignKey(User, unique=False)
    follower = models.ForeignKey(User, related_name='follower', unique=False)
    
    class Meta:
        unique_together = ('user', 'follower')
    class Admin:
        pass
    
class PrivateMailThread(models.Model):
    user = models.ForeignKey(User, unique=False)
    conversational_partner = models.ForeignKey(User, related_name='conversational_partner', unique=False)
    latest_sender = models.ForeignKey(User, related_name='latest_sender', unique=False)
    latest_content = models.CharField(max_length=300, null = False)
    all_read = models.BooleanField(default=False)
    mails = models.IntegerField(default=0)
    latest_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-all_read','-latest_datetime']
    class Admin:
        pass
    
    
class PrivateMail(models.Model):
    user = models.ForeignKey(User, unique=False)
    from_user = models.ForeignKey(User, related_name='from_user', unique=False)
    to_user = models.ForeignKey(User, related_name='to_user', unique=False)
    content = models.CharField(max_length=300, null = False)
    is_read = models.BooleanField(default=False)
    thread = models.ForeignKey(PrivateMailThread, unique=False)
    sent_datetime = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.content.encode('utf-8')
    def __unicode__(self):
        return force_unicode(self.content)
    class Meta:
        ordering = ['-sent_datetime']
    class Admin:
        pass
    
class BlackList(models.Model):
    user = models.ForeignKey(User, unique=False)
    bad_guy = models.ForeignKey(User, related_name='bad_guy', unique=False)
    
    def __str__(self):
        return self.bad_guy.encode('utf-8')
    def __unicode__(self):
        return force_unicode(self.bad_guy)
    class Meta:
        ordering = ['user']
    class Admin:
        pass
