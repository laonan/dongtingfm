# coding=utf-8
import urllib
from django import forms
from django.core.urlresolvers import reverse
from django.contrib.sites.models import get_current_site
from django.forms import widgets

from accounts.models import UserProfile
from songs.models import Artist, SongGenre, Song, Playlist

class ArtistForm(forms.Form):
    artist_name = forms.CharField(max_length = 40, required=False)
    headshot = forms.ImageField(required=False)
    
    def save(self,request):
        if request.FILES.get('id_headshot', None):
            if request.POST.get('id_artist_name'):
                artists = Artist.objects.filter(artist_name__iexact=request.POST.get('id_artist_name'), create_user=request.user)
                if not artists:
                    artist = Artist()
                else:
                    artist = artists[0]
                    
                artist.artist_name = request.POST.get('id_artist_name')
                
                #删除掉原头像
                import os
                if artist.headshot and os.path.exists(artist.headshot.path):
                    os.remove(artist.headshot.path)
                    
                artist.headshot = request.FILES.get('id_headshot', None)
                artist.create_user = request.user
                artist.save()


SongGenres = SongGenre.objects.all()
GENRE_CHOICES = []
GENRE_CHOICES.append(['','------'])
for genre in SongGenres:
    GENRE_CHOICES.append([genre.id, genre.genre_name])
             
class AddMusicForm(forms.Form):
    audio_url = forms.URLField(required=False, widget = widgets.TextInput(attrs={'class': 'validate[custom[longUrl]] url-input'}))
    vedio_url = forms.URLField(required=False, widget = widgets.TextInput(attrs={'class': 'validate[custom[longUrl]] url-input'}))
    flash_url = forms.URLField(required=False, widget = widgets.TextInput(attrs={'class': 'validate[custom[longUrl]] url-input'}))
    title = forms.CharField(max_length = 40, widget = widgets.TextInput(attrs={'class': 'validate[required] text-input'}))
    singer = forms.CharField(max_length = 20, required=False, widget = widgets.TextInput())
    album = forms.CharField(max_length = 20,  required=False, widget = widgets.TextInput())
    genre = forms.CharField(widget=forms.Select(attrs={'class': 'validate[required] text-input'}, choices=GENRE_CHOICES))
    song_cover_url = forms.CharField(max_length = 100, widget = widgets.HiddenInput())
    intro = forms.CharField(max_length = 140,  required=False,  widget=forms.Textarea(attrs={'class': 'validate[maxSize[140]]'}))
    
    def save(self, request):
       
        song = Song()
        song.user =  request.user
        
        domain_name = ''
        if self.cleaned_data['audio_url']:
            domain_name = self.cleaned_data['audio_url'].split('/')
            song.audio_url = self.cleaned_data['audio_url']                
            
        if self.cleaned_data['vedio_url']:
            domain_name = self.cleaned_data['vedio_url'].split('/')
            song.vedio_url = self.cleaned_data['vedio_url']
            
        if self.cleaned_data['flash_url']:
            domain_name = self.cleaned_data['flash_url'].split('/')
            song.flash_url = self.cleaned_data['flash_url']
            
        if len(domain_name) >= 2:
            song.source = domain_name[2]
            if song.flash_url:
                s_size = _get_swf_size(song.source)
                song.flash_width = s_size[0]
                song.flash_height = s_size[1]
            
        song.title = self.cleaned_data['title']
        song.singer = self.cleaned_data['singer']
        song.album = self.cleaned_data['album']
        song.genre = SongGenre.objects.get(id=self.cleaned_data['genre'])
        if self.cleaned_data['song_cover_url'].find('images/artist.png') == -1:
            song.song_cover_url = self.cleaned_data['song_cover_url']
        song.intro = self.cleaned_data['intro']
        song.show_media = True
        
        #当链接是百度那个下载链接（但不能在线引用播放）时，转成flash
        if song.audio_url and song.audio_url.find('zhangmenshiting') != -1 and song.audio_url.find('baidu') != -1:
            song.audio_url = None
            m = {'artist' : song.singer, 'name' : song.title, }
            song.flash_url = 'http://box.baidu.com/widget/flash/mbsong.swf?%s' % (urllib.urlencode(m))
            song.flash_width = 400
            song.flash_height = 95
        
        song.save()

        #加入电台播放
        if song.audio_url and request.POST.get('add_to_playlist'):
            _add_to_playlist(song, request.user)

        #发布到新浪微博
        if (request.POST.get('share_swf_to_weibo') and song.flash_url) or (request.POST.get('share_to_weibo') and song.audio_url):

            current_site = get_current_site(request)

            domain = current_site.domain
            public_radio_url = reverse('songs.views.public_radio',args=(song.id,))

            from social.views import _post_weibo
            s_url = 'http://%s%s' % (domain, public_radio_url)
            msg = '[%s-%s]%s' %(song.title, song.singer, song.intro)
            _post_weibo(request, msg, s_url)

        request.user.get_profile()
        request.user.get_profile().songs = request.user.get_profile().songs + 1
        request.user.get_profile().save()

            
def _get_swf_size(song_source):
    swf_size = (400,100)
    
    if song_source.find('baidu.com') != -1:
        swf_size = (400, 95)
    elif song_source.find('xiami.com') != -1:
        swf_size = (257, 33)
    elif song_source.find('flamesky.com') != -1:
        swf_size = (300, 36)
    elif song_source.find('youku.com') != -1:
        swf_size = (480, 400)
    elif song_source.find('tudou.com') != -1:
        swf_size = (480, 400)
    elif song_source.find('ku6.com') != -1:
        swf_size = (480, 400)
    elif song_source.find('sohu.com') != -1:
        swf_size = (480, 400)
    elif song_source.find('sina.com') != -1:
        swf_size = (480, 370)
    elif song_source.find('56.com') != -1:
        swf_size = (480, 405)
    elif song_source.find('kugou.com') != -1:
        swf_size = (205, 40)
    
    return swf_size;

def _add_to_playlist(song, usr):
    # url validating sometimes could be failed?
    if song.audio_url and song.audio_url.find('<') == -1 and song.audio_url.find('>') == -1:
        audio_url = Playlist.objects.filter(location__iexact=song.audio_url, user=usr)
        if audio_url:
            playlist = Playlist()
            playlist.user = usr
            playlist.location = song.audio_url
            playlist.creator = song.singer
            playlist.album = song.album
            playlist.title = song.title
            playlist.annotation = song.comments
            playlist.image = song.song_cover_url
            playlist.info = song.comments
            playlist.link = song.source
            playlist.save()
    
    