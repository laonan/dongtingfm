//weibo.com
(function(){
  var _w = 90 , _h = 24;
  var param = {
    url:location.href,
    type:'2',
    count:'1', /**是否显示分享数，1显示(可选)*/
    appkey:'', /**您申请的应用appkey,显示分享来源(可选)*/
    title: encodeURI('推荐一个音乐发现站点'), /**分享的文字内容(可选，默认为所在页面的title)*/
    pic: window.location.protocol + '//' + window.location.host + static_url +  'images/logo.png', /**分享图片的路径(可选)*/
    ralateUid:'', /**关联用户的UID，分享微博会@该用户(可选)*/
    rnd:new Date().valueOf()
  }
  var temp = [];
  for( var p in param ){
    temp.push(p + '=' + encodeURIComponent( param[p] || '' ) )
  }
  document.write('<iframe allowTransparency="true" frameborder="0" scrolling="no" src="http://hits.sinajs.cn/A1/weiboshare.html?' + temp.join('&') + '" width="'+ _w+'" height="'+_h+'"></iframe>')
})();


//qq.com
function postToWb(){
	var _t = encodeURI('推荐一个音乐发现站点');
	var _url = encodeURIComponent(document.location);
	var _appkey = encodeURI("appkey");//你从腾讯获得的appkey
	var _pic = encodeURI(window.location.protocol + '//' + window.location.host + static_url +  'images/logo.png');//（例如：var _pic='图片url1|图片url2|图片url3....）
	var _site = window.location.protocol + '//' + window.location.host;//你的网站地址
	var _assname = '动听FM';
	var _u = 'http://v.t.qq.com/share/share.php?url='+_url+'&appkey='+_appkey+'&site='+_site+'&pic='+_pic+'&title='+_t+'&assname='+_assname;
	window.open( _u,'', 'width=700, height=680, top=0, left=0, toolbar=no, menubar=no, scrollbars=no, location=yes, resizable=no, status=no' );
}