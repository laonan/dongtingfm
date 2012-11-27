# coding=utf-8
import datetime
from django.utils.timezone import utc
from django import template

register = template.Library()

#人性化的时间：2008-01-27 08:37:29
def friendly_time(ts):
   delta = datetime.datetime.utcnow().replace(tzinfo=utc) - ts
   if delta.days >= 365:
       return ts.strftime(u'%Y-%m-%d')
       #return ts.strftime("%Y-%m-%d %p  %H:%M:%S %A")
   elif delta.days >= 30:
       return u'%d 个月前' % (delta.days / 30)
   elif delta.days > 0:
       return u'%d 天前' % delta.days
   elif delta.seconds < 60:
       return u'%d 秒前' % delta.seconds
   elif delta.seconds < 60 * 60:
       return u'%d 分钟前' % (delta.seconds / 60)
   else:
       return u'%d 小时前' % (delta.seconds / 60 / 60)
register.filter(friendly_time)

def format_comment(str):
    str = str.replace(' ','&nbsp;')
    str = str.replace('<', '&lt;')
    str = str.replace('>', '&gt;')
    str = str.replace('\n', '<br>')
    
    return str
register.filter(format_comment)