# coding=utf-8
import json
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from accounts.models import UserProfile
from sns.models import UserFollower, BlackList
from songs.models import SongGenre,Song, Artist, Dig, Bury, Favorite, SongComment, Playlist, PlayerLog
from songs.mp3helper.views import downloadMp3
from songs.forms import ArtistForm, AddMusicForm, _get_swf_size, _add_to_playlist

@login_required(login_url='/login')
def add_music(request, template_name):
    if request.method == 'POST':
        jsonData = '{"saved": false}'
        form = AddMusicForm(request.POST)
        if form.is_valid():
            song_exist = request.POST.get('song_exist_ret','False')
            save_now = False;
            if song_exist == 'False':
                songs = Song.objects.filter(title__iexact=request.POST.get('title',None), singer__iexact=request.POST.get('singer',None))[:1]
                if songs:
                    song = songs[0]
                    song_url = reverse('songs.views.song_details',args=(song.id,))
                    jsonData = '{"saved" : false, "validated": true, "title": "%s", "singer": "%s", "intro": "%s", "song_cover_url": "%s", "user": "%s", "post_datetime": "%s", "id": %s, "song_url": "%s"}' % tuple([song.title, song.singer, song.intro, song.song_cover_url, song.user.username, song.post_datetime, song.id, song_url])
                else:
                    save_now = True
            else:
                save_now = True;
                
            if save_now == True:
                opts = {'request': request,}
                form.save(**opts)
                jsonData = '{"saved": true}'
            
        else:
            jsonData = '{"saved": false, "validated": false}'
        
        return HttpResponse(jsonData)
    else:
        template_var={}
        template_var['form'] = AddMusicForm(initial = { 'song_cover_url': 'images/artist.png' } )
        
        #检测是不是新浪微博主
        access_token = request.session.get('oauth_access_token', None)
        if access_token:
            template_var['weibo_user_ret'] = True
            
        return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def song_details(request, song_id, template_name):
    template_var={}
    
    s_list = Song.objects.select_related().filter(id=song_id)[:1]
    if s_list:
        song_detail = s_list[0]
        
        comments = SongComment.objects.select_related().extra(select={'comment_user_avatar':'accounts_userprofile.avatar'},
                                                              tables=['accounts_userprofile'],
                                                              where=['songs_songcomment.user_id=accounts_userprofile.user_id AND songs_songcomment.song_id=%s' % song_id])
                
        if request.user.is_authenticated() and request.user == song_detail.user:
            SongComment.objects.filter(song__id=song_id).update(read_by_owner=True)
        
        page = 1
        
        if request.is_ajax():
            query = request.GET.get('page')
            if query:
                page = query
        else:
            try:
                user_profile = song_detail.user.get_profile()
                template_var['user_profile'] = user_profile
            except UserProfile.DoesNotExist:
                user_profile = UserProfile()
                user_profile.user = song_detail.user
                template_var['user_profile'] = user_profile
                
            if request.user.is_authenticated():
                user_followers = UserFollower.objects.select_related().filter(user=song_detail.user, follower=request.user)
                if user_followers:
                    template_var['user_follower'] = user_followers[0]
                    
                my_blacklist = BlackList.objects.select_related().filter(user=request.user, bad_guy=song_detail.user)
                if my_blacklist:
                    template_var['in_my_blacklist'] = True
               
        
        paginator = Paginator(comments, 15)
        try:
            comments = paginator.page(page)
        except (EmptyPage, InvalidPage):
            comments = paginator.page(paginator.num_pages)
            
        digs = Dig.objects.select_related().extra(select={'dig_user_avatar':'accounts_userprofile.avatar', 'dig_user_name':'auth_user.username'},
                                 tables=['songs_song', 'songs_dig','auth_user','accounts_userprofile'],
                                 where=['songs_song.id=songs_dig.song_id AND songs_dig.user_id=accounts_userprofile.user_id AND accounts_userprofile.user_id=auth_user.id AND songs_dig.song_id=%s' % song_id]).order_by('?')[:12].values('id','user_id','dig_user_avatar','dig_user_name')
        

        if 'HTTP_USER_AGENT' in request.META:
                ipad = (lambda x:'iPad' in x or False)(request.META['HTTP_USER_AGENT'])
                template_var['ipad'] = ipad

        #检测是不是新浪微博主
        access_token = request.session.get('oauth_access_token', None)
        if access_token is not None:
            template_var['weibo_user_ret'] = True

        template_var['favorite_action'] = 'add'
        template_var['song'] = song_detail
        template_var['comments'] = comments
        template_var['digs'] = digs
        template_var['all_show_media'] = settings.ALL_SHOW_MEDIA
        
    else:
        template_var['song'] = None
        
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def song_edit(request, song_id, template_name):
    jsonData = '{"edited": false}'
    if request.user.is_authenticated():
        song = Song.objects.get(id=song_id)
        if request.user.id == song.user.id:
            
            if  request.method == 'POST':
                audio_url = request.POST.get('audio_url')
                flash_url = request.POST.get('flash_url')
                intro = request.POST.get('intro_edit')
                
                old_audio_url = song.audio_url
                
                if audio_url:
                    song.audio_url = audio_url
                    song.flash_url = None
                    
                    domain_name = audio_url.split('/')
                    if len(domain_name) >= 2:
                        song.source = domain_name[2]
                    
                    #更新电台链接
                    if old_audio_url:
                        playlist = Playlist.objects.filter(location=old_audio_url)
                        for p in playlist:
                            p.location = audio_url
                            p.save()
                        
                    
                else:
                    song.flash_url = flash_url
                    song.audio_url = None
                    domain_name = flash_url.split('/')
                    
                    if len(domain_name) >= 2:
                        song.source = domain_name[2]
                        swf_size = _get_swf_size(song.source)
                        song.flash_width = swf_size[0]
                        song.flash_height = swf_size[1]
                    
                song.intro = intro
                song.save()
            
                jsonData = '{"edited": true}'
                
                return HttpResponse(jsonData)
            else:
                template_var = {}
                template_var['song'] = song
                return render_to_response(template_name, template_var, context_instance=RequestContext(request))
        else:
            return HttpResponse('') 
    else:
        return HttpResponse('')

@login_required(login_url='/login')    
def song_list(request, genre_code, template_name):
    genre_name = None
    ord_field = request.user.get_profile().song_ord_filed
    if genre_code:
        g_code = genre_code
        try:
            g = SongGenre.objects.get(genre_name_code=genre_code)
            
            s_list = Song.objects.select_related('genre__genre_name', 'genre__genre_name_code', 'user__username').extra(where=['songs_song.genre_id=%s AND songs_song.id NOT IN (SELECT song_id FROM songs_bury WHERE user_id=%s)' % (g.id,request.user.id)]).order_by('-%s' % ord_field)
                        
            genre_name = g.genre_name
        except SongGenre.DoesNotExist:
            s_list = None
    else:
        g_code = 'all'
        s_list = Song.objects.select_related('genre__genre_name', 'genre__genre_name_code', 'user__username').extra(where=['songs_song.id NOT IN(SELECT song_id FROM songs_bury WHERE user_id=%s)' % request.user.id]).order_by('-%s' % ord_field)
            
    paginator = Paginator(s_list, 20)
   
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        songs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        songs = paginator.page(paginator.num_pages)
        
    template_var = {}
    template_var['g_code'] = g_code
    template_var['genre_name'] = genre_name
    template_var['favorite_action'] = 'add'
    template_var['square_radio'] = True
    template_var['songs'] = songs
    

    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def search(request, template_name):
    query = request.GET.get('q', '')
    if query:
        qset = (
            Q(title__icontains=query) |
            Q(singer__icontains=query) |
            Q(album__icontains=query)
            #Q(user__username__icontains=query)
        )
        songs = Song.objects.select_related('genre__genre_name', 'genre__genre_name_code', 'user__username').filter(qset).distinct()    
    else:
        songs = []
        
    paginator = Paginator(songs, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    try:
        songs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        songs = paginator.page(paginator.num_pages)
        
    template_var = {}
    template_var['favorite_action'] = 'add'
    template_var['current_tabnav'] = 'search'
    template_var['search_key'] = query
    template_var['songs'] = songs
    
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def song_digs(request, song_id, template_name):
    digs = Dig.objects.select_related().extra(select={'dig_user_avatar':'accounts_userprofile.avatar', 'dig_user_name':'auth_user.username'},
                                              tables=['songs_song', 'songs_dig','auth_user','accounts_userprofile'],
                                              where=['songs_song.id=songs_dig.song_id AND songs_dig.user_id=accounts_userprofile.user_id AND accounts_userprofile.user_id=auth_user.id AND songs_dig.song_id=%s' % song_id]).values('id','user_id','dig_user_avatar','dig_user_name')
        
    page = request.GET.get('page', 1)
        
    paginator = Paginator(digs, 32)
    try:
        digs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        digs = paginator.page(paginator.num_pages)
        
    template_var = {}
    template_var['digs'] = digs
    template_var['song_id'] = song_id
        
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))
 

@login_required(login_url='/login')
def my_home(request, template_name):
    ord_field = request.user.get_profile().song_ord_filed
    #除了自己发布的，还有自己所关注的人发布的歌曲
    songs = Song.objects.select_related('genre__genre_name', 'genre__genre_name_code', 'user__username').extra(where=['songs_song.id NOT IN (SELECT song_id FROM songs_bury WHERE user_id=%s) AND (songs_song.user_id=%s OR songs_song.user_id IN (SELECT user_id FROM sns_userfollower WHERE follower_id=%s))' % (request.user.id,request.user.id,request.user.id)]).order_by('-%s' % ord_field)
       
    paginator = Paginator(songs, 20)
   
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        songs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        songs = paginator.page(paginator.num_pages)
        
    template_var = {}
    template_var['favorite_action'] = 'add'
    template_var['current_tabnav'] = 'my_home'
    template_var['songs'] = songs
                
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

    

@login_required(login_url='/login')
def my_songs(request, template_name):
    ord_field = request.user.get_profile().song_ord_filed
    songs = Song.objects.select_related().filter(user=request.user).order_by('-%s' % ord_field)
    
    paginator = Paginator(songs, 20)
   
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        songs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        songs = paginator.page(paginator.num_pages)
        
    template_var = {}
    template_var['favorite_action'] = 'none'
    template_var['current_tabnav'] = 'my_songs'
    template_var['songs'] = songs
                
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def my_favorites(request, template_name):
    ord_field = request.user.get_profile().song_ord_filed
    songs = Song.objects.select_related().extra(tables=['songs_favorite'],
                                                where=['songs_song.id=songs_favorite.song_id AND songs_favorite.user_id=%s' % request.user.id]).order_by('-%s' % ord_field)
    paginator = Paginator(songs, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        songs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        songs = paginator.page(paginator.num_pages)
        
    template_var = {}
    template_var['favorite_action'] = 'remove'
    template_var['current_tabnav'] = 'my_favorites'
    template_var['songs'] = songs
                
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def songs_by_user(request, uid, template_name):
    if long(uid) == request.user.id:
        return my_songs(request, template_name)
    else:
        user_profile = None
        u = None
        template_var = {}
        try:
            u = User.objects.get(id=uid)
            songs = Song.objects.select_related().filter(user=u)
            try:
                user_profile = u.get_profile()
            except UserProfile.DoesNotExist:
                user_profile = UserProfile()
                user_profile.user = u
                user_profile.save()
                
            if request.user.is_authenticated():
                my_blacklist = BlackList.objects.filter(user=request.user, bad_guy=u)
                if my_blacklist:
                    template_var['in_my_blacklist'] = True
        except User.DoesNotExist:
            songs = None
        
       
        try:
            if request.user.is_authenticated():
                user_follower = UserFollower.objects.get(user=u, follower=request.user)
                template_var['user_follower'] = user_follower
        except UserFollower.DoesNotExist:
            template_var['user_follower'] = None
            
        paginator = Paginator(songs, 20)
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
    
        try:
            songs = paginator.page(page)
        except (EmptyPage, InvalidPage):
            songs = paginator.page(paginator.num_pages)
            
        template_var['favorite_action'] = 'add'
        template_var['current_tabnav'] = 'user_songs'
        template_var['user_profile'] = user_profile
        template_var['songs'] = songs
        
        return render_to_response(template_name, template_var, context_instance=RequestContext(request))

def get_random_song(request, user_id=None):
    if user_id:
        u = User.objects.get(id=user_id)
        songs_count = Playlist.objects.filter(user=u).count()
        if songs_count > 0:
            songs = Playlist.objects.filter(user=u).order_by('?')[:1]
        else:
            songs = Playlist.objects.all().order_by('?')[:1]
    else:
        songs = Playlist.objects.all().order_by('?')[:1]
    song = songs[0]
    dict_song = {'id' : song.id, 'title' : song.title, 'url' : song.location, 'username' : song.user.username }
    return HttpResponse(json.dumps(dict_song, ensure_ascii=False))

def player_logs(request):
    if request.is_ajax() and request.method == 'POST':
        log = PlayerLog();
        log.title = request.POST.get('title')
        log.playlist_id = request.POST.get('playlist_id')
        log.message = request.POST.get('msg')
        log.save()
        return HttpResponse('{"saved" : true}')
    else:
        return HttpResponse('{"saved" : false}')


def radio(request, template_name, uid=None):
    if uid == None:
        user = None
        songs = Song.objects.select_related().filter(intro__isnull=False).exclude(intro='')[:10]
    else:
        user = User.objects.get(id=uid)
        songs = Song.objects.select_related().filter(user=user,intro__isnull=False).exclude(intro='')[:10]
    
    current_site = get_current_site(request)
    domain = current_site.domain
    template_var = {}
    template_var['radio_user'] = user
    template_var['radio_user_songs'] = songs
    template_var['curr_url'] = 'http://' + domain + request.get_full_path()
    if user:
        template_var['radio_user_profile'] = user.get_profile();
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

def public_radio(request, song_id, template_name):
    template_var = {}
    song = Song.objects.filter(id=song_id)
    if song:
        template_var['song'] = song[0]
        
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

@login_required(login_url='/login')
def get_mp3_info(request):
    json_data = '{false}'
    if request.user.is_authenticated() and request.is_ajax():
        mp3_url = request.POST.get('id_audio_url', None)
        if mp3_url and downloadMp3(request,mp3_url):
            from mutagen.easyid3 import EasyID3
            from mutagen.mp3 import MP3
            audio = MP3('tmp/temp.mp3', ID3=EasyID3)
            title = audio.get('title', [''])[0].encode('ISO-8859-1')
            artist = audio.get('artist', [''])[0].encode('ISO-8859-1')
            album = audio.get('album', [''])[0].encode('ISO-8859-1')
            bitrate = audio.info.bitrate
            filesize = round(audio.info.length)
        
            mp3_info = [title, artist, album]
            json_data = '{"title" : "%s", "artist" : "%s", "album" : "%s"}' % tuple(mp3_info)
    else:
        json_data = '{%s}' % getattr(settings,'DOMAIN_NAME',None)
    return HttpResponse(json_data)

@login_required(login_url='/login')
def get_song_cover(request):
    img_url = '%simages/artist.png' % settings.STATIC_URL
    if request.user.is_authenticated() and request.is_ajax():
        user_artists = Artist.objects.filter(artist_name__icontains=request.GET.get('artist'), create_user=request.user)[:1]
        if user_artists:
            img_url = user_artists[0].headshot
        else:
            all_artists = Artist.objects.filter(artist_name__icontains=request.GET.get('artist'))[:1]
            if all_artists:
                img_url =  all_artists[0].headshot
    jsonData = '{"avatar_url": "%s"}' % img_url
    return HttpResponse(jsonData)

@login_required(login_url='/login')
def upload_artist_headshot(request):
    img_url = '{"url": "%simages/artist.png"}' % settings.STATIC_URL
    if request.user.is_authenticated():
        form = ArtistForm(request.POST, request.FILES)
        if request.method == 'POST' and form.is_valid(): #why can't request.is_ajax()?
            opts = {'request': request,}
            form.save(**opts)
            
            artists = Artist.objects.filter(artist_name__icontains=request.POST.get('id_artist_name'), create_user=request.user)[:1]
            if artists:
                img_url = '{"url": "%s"}' % artists[0].headshot.url
                
       
    return HttpResponse(img_url)

@login_required(login_url='/login')
def dig(request):
    if request.is_ajax():
        jsonData = '{"dug": false, "msg": "song id is none"}'
        song_id = request.GET.get('song_id', 0)
        if song_id != 0:
            dig_song = Song.objects.get(id=song_id)
            try:
                dig_exist = Dig.objects.get(user=request.user, song=dig_song)
                jsonData = '{"dug": false, "exist": true, "msg": "has dug"}'
            except Dig.DoesNotExist:
                d = Dig()
                d.user = request.user
                d.song = dig_song
                d.save()
                
                dig_song.digs = dig_song.digs + 1
                dig_song.save()
                
                jsonData = '{"dug": true, "digs": %s}' % dig_song.digs
            
            _add_to_playlist(dig_song, request.user)
            
        return HttpResponse(jsonData)
    else:
        return HttpResponse('')

@login_required(login_url='/login') 
def radio_dig(request):
    if request.is_ajax():
        jsonData = '{"dug": false, "msg": "song id is none"}'
        dig_title = request.GET.get('title', None)
        if dig_title:
            dig_songs = Song.objects.filter(title=dig_title)
            for s in dig_songs:
                digs_count = Dig.objects.filter(user=request.user, song=s).count()
                if digs_count == 0:
                    d = Dig()
                    d.user = request.user
                    d.song = s
                    d.save()
                    
                    s.digs = s.digs + 1
                    s.save()
                    
                    _add_to_playlist(s, request.user)
                    
                    jsonData = '{"dug": true}'
                    
        return HttpResponse(jsonData)
    else:
        return HttpResponse('')
                        
        
@login_required(login_url='/login')   
def bury(request):
    if request.is_ajax():
        jsonData = '{"buried": false, "msg": "song id is none"}'
        song_id = request.GET.get('song_id', 0)
        if song_id != 0:
            bury_song = Song.objects.get(id=song_id)
            try:
                bury_exist = Bury.objects.get(user=request.user, song=bury_song)
                jsonData = '{"buried": false, "exist": true, "msg": "has buried"}'
            except Bury.DoesNotExist:
                b = Bury()
                b.user = request.user
                b.song = bury_song
                b.save()
                
                jsonData = '{"buried": true}'
            
        return HttpResponse(jsonData)
    else:
        return HttpResponse('')

@login_required(login_url='/login')
def favorite(request, action_name):
    if request.is_ajax():
        jsonData = '{"excuted": false, "action": "%s", "msg": "song id is none"}' % action_name
        song_id = request.GET.get('song_id', 0)
        if song_id != 0:
            favorite_song = Song.objects.get(id=song_id)
            try:
                favorite_exist = Favorite.objects.get(user=request.user, song=favorite_song)
                if action_name == 'remove':
                    favorite_exist.delete()
                    jsonData = '{"excuted": true, "action": "%s"}' % action_name
                else:
                    jsonData = '{"excuted": false, "action": "%s", "existBefore": true}' % action_name
            except Favorite.DoesNotExist:
                f = Favorite()
                f.user = request.user
                f.song = favorite_song
                f.save()
                
                jsonData = '{"excuted": true, "action": "%s", "existBefore": false}' % action_name
            
        return HttpResponse(jsonData)
    else:
        return HttpResponse('')

@login_required(login_url='/login')
def comment(request):
    if request.is_ajax() and request.method == 'POST':
        song_id = request.POST.get('song_id')
        comment_content = request.POST.get('comment')
        reply_to_user = request.POST.get('reply_to_user')
        
        comment_song = Song.objects.get(id=song_id)
        comment_song.comments = comment_song.comments + 1
        comment_song.save()
        
        c = SongComment()
        c.song = comment_song
        c.user = request.user
        c.comment = comment_content
        
        if comment_song.user != request.user:
            c.read_by_owner = False
        else:
            c.read_by_owner = True
            
        if reply_to_user:
            c.reply_to_user = User.objects.get(id=reply_to_user)
        
        c.save()

        #发微博
        if request.POST.get('share_to_weibo') == 'true':
            current_site = get_current_site(request)

            domain = current_site.domain
            public_radio_url = reverse('songs.views.public_radio',args=(comment_song.id,))

            from social.views import _post_weibo
            s_url = 'http://%s%s' % (domain, public_radio_url)
            msg = '[%s-%s]%s' %(comment_song.title, comment_song.singer, comment_content)
            _post_weibo(request, msg, s_url)

        jsonData = '{"commented": true, "comments_count": %s}' % comment_song.comments
        return HttpResponse(jsonData)
    else:
        return HttpResponse('{}')

@login_required(login_url='/login')
def del_comment(request):
    if request.is_ajax() and request.user.is_authenticated():
        jsonData = '{"deleted": false}'
        song_comment_id = request.GET.get('song_comment_id')
        song_comment = SongComment.objects.get(id=song_comment_id)
        
        user_id = song_comment.user.id
        song_user_id = song_comment.song.user.id
        
        if request.user.id == user_id or request.user.id == song_user_id:
            song_comment.song.comments = song_comment.song.comments - 1
            comments = song_comment.song.comments
            
            song_comment.song.save()
            song_comment.delete()
            
            jsonData = '{"deleted": true, "comments": %s}' % comments
            
        else:
            jsonData = '{"deleted": false, "msg": "not allowed"}'
        
        return HttpResponse(jsonData)
    else:
        return HttpResponse('')
   
@login_required(login_url='/login')
def comments(request, template_name):
    
    comments = SongComment.objects.extra(select={'songcomment_song_title':'songs_song.title', 'songcomment_userprofile_avatar':'accounts_userprofile.avatar', 'songcomment_user_username':'auth_user.username'},
                                         tables=['songs_song', 'songs_songcomment', 'auth_user', 'accounts_userprofile'],
                                         where=['songs_song.id=songs_songcomment.song_id AND songs_songcomment.user_id=auth_user.id AND auth_user.id = accounts_userprofile.user_id AND (songs_song.user_id=%s OR songs_songcomment.reply_to_user_id=%s)' % (request.user.id, request.user.id)])
    #comments.update(read_by_owner=True)
    update_sql = 'UPDATE songs_songcomment SET read_by_owner=1 WHERE song_id IN (SELECT id FROM songs_song WHERE user_id=%s) AND read_by_owner=0'
    update_reply_sql = 'UPDATE songs_songcomment SET read_by_reply_user=1 WHERE reply_to_user_id=%s AND read_by_reply_user=0'
    cursor = connection.cursor()    
    cursor.execute(update_sql, [request.user.id])
    cursor.execute(update_reply_sql, [request.user.id])
    
    page = request.GET.get('page', 1)
    paginator = Paginator(comments, 15)
    try:
        comments = paginator.page(page)
    except (EmptyPage, InvalidPage):
        comments = paginator.page(paginator.num_pages)
    
    template_var = {}
    template_var['comments'] = comments
    
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))
            
@login_required(login_url='/login')
def get_unread_comments(request):
    if request.is_ajax() and request.user.is_authenticated():
        cursor = connection.cursor() 
        cursor.execute('SELECT count(*) FROM songs_song,songs_songcomment WHERE songs_song.id=songs_songcomment.song_id AND ((songs_songcomment.read_by_owner=0 AND songs_song.user_id=%s) OR (songs_songcomment.read_by_reply_user=0 AND songs_songcomment.reply_to_user_id=%s))', [request.user.id, request.user.id]) 
        row = cursor.fetchone() 
        return HttpResponse('{"unread_comments": %s}' % row[0])
    else:
        return HttpResponse('')