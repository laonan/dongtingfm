# coding=utf-8
from django.contrib import admin
from songs.models import SongGenre, Song, Artist, Dig, Bury, Favorite, SongComment, Playlist, PlayerLog

class SongGenreAdmin(admin.ModelAdmin):
    list_display = ('pk','genre_name', 'genre_name_code', 'order_id')
    list_filter = ('genre_name_code',)
    ordering = ('order_id',)
    search_fields = ('genre_name',)
admin.site.register(SongGenre, SongGenreAdmin)

class SongAdmin(admin.ModelAdmin):
    list_display = ('pk','title','singer', 'digs','source','user', 'post_datetime')
    list_filter = ('genre',)
    ordering = ('-post_datetime',)
    search_fields = ('title',)
admin.site.register(Song, SongAdmin)

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('pk','artist_name','headshot', 'create_user')
    #list_filter = ('genre',)
    #ordering = ('-pk',)
    search_fields = ('artist_name',)
admin.site.register(Artist, ArtistAdmin)

class DigAdmin(admin.ModelAdmin):
    list_display = ('pk','user','song')
    #list_filter = ('genre',)
    ordering = ('user',)
    search_fields = ('user_username',)
admin.site.register(Dig, DigAdmin)

class BuryAdmin(admin.ModelAdmin):
    list_display = ('pk','user','song')
    #list_filter = ('genre',)
    ordering = ('user',)
    search_fields = ('user',)
admin.site.register(Bury, BuryAdmin)

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk','user','song')
    #list_filter = ('genre',)
    ordering = ('user',)
    search_fields = ('user_username',)
admin.site.register(Favorite, FavoriteAdmin)

class SongCommentAdmin(admin.ModelAdmin):
    list_display = ('pk','song','user','comment_datetime')
    ordering = ('-comment_datetime',)
    search_fields = ('song_title',)
admin.site.register(SongComment, SongCommentAdmin)

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('pk','title','user','post_datetime')
    list_filter = ('user',)
    ordering = ('-post_datetime',)
    search_fields = ('title',)
admin.site.register(Playlist, PlaylistAdmin)

class PlayerLogAdmin(admin.ModelAdmin):
    list_display = ('title','playlist_id','post_datetime')
    ordering = ('-post_datetime',)
    search_fields = ('title',)
admin.site.register(PlayerLog, PlayerLogAdmin)

