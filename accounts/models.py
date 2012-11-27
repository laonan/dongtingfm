# coding=utf-8
import Image 
import tempfile
import StringIO

from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.files import ImageFieldFile
from django.utils.encoding import force_unicode

class AvatarFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        # Repopulate the image dimension cache.      
        temp_file = tempfile.TemporaryFile()
        f = StringIO.StringIO(content.read())
        image = Image.open(f)
        #取得指定的图像最大尺寸
        max_width,max_height = self.field.max_width,self.field.max_height
        
        import os, time, random
        #文件扩展名
        ext = os.path.splitext(name)[1]
        #文件目录
        d = os.path.dirname(name)
        #定义文件名，年月日时分秒随机数
        fn = time.strftime('%Y%m%d%H%M%S')
        fn = fn + '-%d' % random.randint(0,100)
        #重写合成文件名
        name = os.path.join(d, fn + ext)

        image.thumbnail((45,45),Image.ANTIALIAS)
        if ext.upper() == '.JPG' or ext.upper() == '.JPEG':  
            image.save(temp_file,'JPEG')
        
        if ext.upper() == '.GIF':
            image.save(temp_file,'GIF')
        
        if ext.upper() == '.PNG':
            image.save(temp_file,'PNG')
        
        temp_file.seek(0)
        content2 = ContentFile(temp_file.read())
        content.close()
        temp_file.close()
        super(AvatarFieldFile, self).save(name, content2, save)
        
class AvatarField(models.ImageField):
    attr_class = AvatarFieldFile
    def __init__(self, verbose_name=None, name=None, width_field=None, 
                 height_field=None,thumbnail_path=None,max_size=(600,600),**kwargs):
        self.width_field, self.height_field = width_field, height_field
        self.thumbnail_path = thumbnail_path
        self.max_width,self.max_height = max_size[0], max_size[1]
        models.ImageField.__init__(self, verbose_name, name, **kwargs)

class UserProfile(models.Model):
    # This is the only required field
    user = models.ForeignKey(User, unique=True)

    avatar = AvatarField(upload_to='avatars/%Y/%m/%d', max_length=100, blank=True, null = True) #use 'tmp' insead of '/tmp' , then the file was added successfully.
    website = models.URLField(null = True, blank=True)
    city = models.CharField(max_length=200, null = True, blank=True)
    qq = models.CharField(max_length=20, null = True, blank=True)
    msn = models.CharField(max_length=20, null = True, blank=True)
    intro = models.TextField(max_length=140, null = True, blank=True)
    following = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)
    new_followers = models.IntegerField(default=0)
    song_ord_filed = models.CharField(max_length=20, null = True, blank=True)
    songs = models.IntegerField(default=0)
    point = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.username.encode('utf-8')
    def __unicode__(self):
        return force_unicode(self.user.username)
    class Admin:
        pass
    
class WeiboUser(models.Model):
     user = models.ForeignKey(User, unique=True)
     weibo_user_id = models.BigIntegerField()
     weibo_username = models.CharField(max_length=20)
     create_datetime = models.DateTimeField(auto_now_add=True)
     oauth_access_token = models.CharField(max_length=200)
     
     def __str__(self):
        return self.user.username.encode('utf-8')
     def __unicode__(self):
        return force_unicode(self.user.username)
     class Admin:
         pass
