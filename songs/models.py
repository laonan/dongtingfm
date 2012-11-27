# coding=utf-8
import Image 
import tempfile
import string
import StringIO

from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.files import ImageFieldFile
from django.utils.encoding import force_unicode

class SongCoverFieldFile(ImageFieldFile):
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

        image.thumbnail((50,50),Image.ANTIALIAS)
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
        super(SongCoverFieldFile, self).save(name, content2, save)
        
class SongCoverField(models.ImageField):
    attr_class = SongCoverFieldFile
    def __init__(self, verbose_name=None, name=None, width_field=None, 
                 height_field=None,thumbnail_path=None,max_size=(600,600),**kwargs):
        self.width_field, self.height_field = width_field, height_field
        self.thumbnail_path = thumbnail_path
        self.max_width,self.max_height = max_size[0], max_size[1]
        models.ImageField.__init__(self, verbose_name, name, **kwargs)

class SongGenre(models.Model):
    genre_name = models.CharField(max_length=20)
    genre_name_code = models.CharField(max_length=20)
    order_id = models.IntegerField()
    
    def __str__(self):
        return self.genre_name.encode('utf-8')
    def __unicode__(self):
        return force_unicode(self.genre_name)
    class Meta:
        ordering = ['order_id']
    class Admin:
        pass

class Song(models.Model):
    user = models.ForeignKey(User, unique=False)
    genre = models.ForeignKey(SongGenre)

    song_cover_url = models.CharField(max_length=100, null = True, blank=True)#SongCoverField(upload_to='static/song-covers/%Y/%m/%d', max_length=100, blank=True, null = True)
    audio_url = models.URLField(null = True, blank=True)
    vedio_url = models.URLField(null = True, blank=True)
    flash_url = models.URLField(null = True, blank=True)
    flash_width = models.IntegerField(default=0)
    flash_height = models.IntegerField(default=0)
    source = models.CharField(max_length=100, null = True, blank=True)
    title = models.CharField(max_length=40)
    singer = models.CharField(max_length=20, null = True, blank=True)
    composer = models.CharField(max_length=20, null = True, blank=True)
    lyricist = models.CharField(max_length=20, null = True, blank=True)
    intro = models.CharField(max_length=140, null = True, blank=True)
    album = models.CharField(max_length=40, null = True, blank=True)
    digs = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)
    show_media = models.BooleanField(default=True)
    
    post_datetime = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.title.encode('utf-8')
    def __unicode__(self):
        return force_unicode(self.title)
    class Meta:
        ordering = ['-post_datetime']
    class Admin:
        pass

class SongComment(models.Model):
    song = models.ForeignKey(Song, unique=False)
    user = models.ForeignKey(User, unique=False)
    reply_to_user = models.ForeignKey(User, related_name='reply_to_user', unique=False, null=True, blank=True)
    comment = models.TextField(max_length=800, null = True, blank=True)
    comment_datetime = models.DateTimeField(auto_now_add=True)
    #digs could be negative (-)
    digs = models.IntegerField(default=0)
    read_by_owner = models.BooleanField(default=False)
    read_by_reply_user = models.BooleanField(default=False)
    
    def __str__(self):
        return self.comment.encode('utf-8')
    def __unicode__(self):
        return force_unicode(self.comment)
    class Meta:
        ordering = ['-comment_datetime']
    class Admin:
        pass
    
class Artist(models.Model):
    artist_name = models.CharField(max_length=40)
    headshot = SongCoverField(upload_to='song-covers/%Y/%m/%d', max_length=100, blank=True, null = True)
    create_user =  models.ForeignKey(User, unique=False)
    
    def __str__(self):
        return self.artist_name.encode('utf-8')
    def __unicode__(self):
        return force_unicode(self.artist_name)
    class Admin:
        pass
    
class Dig(models.Model):
    user = models.ForeignKey(User, unique=False)
    song = models.ForeignKey(Song, unique=False)
    
    class Meta:
        unique_together = ('user', 'song')
    class Admin:
        pass
    
class Bury(models.Model):
    user = models.ForeignKey(User, unique=False)
    song = models.ForeignKey(Song, unique=False)
    
    class Meta:
        unique_together = ('user', 'song')
    class Admin:
        pass
    
class Favorite(models.Model):
    user = models.ForeignKey(User, unique=False)
    song = models.ForeignKey(Song, unique=False)
    
    class Meta:
        unique_together = ('user', 'song')
    class Admin:
        pass

class Playlist(models.Model):
    user = models.ForeignKey(User, unique=False)
    location = models.URLField()
    creator = models.CharField(max_length=40, null = True, blank=True)
    album = models.CharField(max_length=80, null = True, blank=True)
    title = models.CharField(max_length=40)
    annotation = models.CharField(max_length=140,  null = True, blank=True)
    duration = models.IntegerField(default=0)
    image = models.CharField(max_length=100, null = True, blank=True)
    info = models.CharField(max_length=140, null = True, blank=True)
    link = models.URLField(null = True, blank=True)
    post_datetime = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title.encode('utf-8')
    def __unicode__(self):
        return force_unicode(self.title)
    class Meta:
        ordering = ['-post_datetime']
    class Admin:
        pass

class PlayerLog(models.Model):
    playlist_id = models.IntegerField()
    title = models.CharField(max_length=40)
    message = models.CharField(max_length=200, null = True, blank=True)
    post_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title.encode('utf-8')
    def __unicode__(self):
        return force_unicode(self.title)
    class Meta:
        ordering = ['-post_datetime']
    class Admin:
        pass