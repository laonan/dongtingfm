$(document).ready(function() {
	$(document).ajaxError(function(ev,xhr,o,err) {
	    $('#btn_submit_add').attr('disabled',false);
	    $('#btn_upload').attr('disabled',false);
	    //$('.add_music_msg').html('<span>请求失败，请刷新页面重试。err:' + err +'</span>');
	    //$('.add_music_msg span').attr('style','color:red; font-weight:bold;');
        //$('.add_music_msg').effect("highlight", {}, 3000);
	    if (window.console && window.console.log) console.log(err);
	});
	
	var song_details_url = null;
	
    $('#add_music_form').validationEngine({
    	scroll:false
    });
    
    $('#upload_headshot_form').validationEngine({
    	scroll:false
    });
    
    $('#btn_cancel_add').click(function() {
        $('#add_music_form').validationEngine('hideAll');
    	tb_remove();
    	if($.browser.msie)//变态的IE
    		$('#TB_overlay').remove();
    });
    
    $('#link_add_artist_headshot').click(function() {
    	$('#add_music_basic_info').hide();
    	$('#add_music_artist_headshot').show();
    	$('#upload_headshot_form').show();
    	$('.add_music_msg').html('上传艺术家头像(50*50 像素，最大2MB，只支持JPG,GIF和PNG格式)');
    	var a_name = $('#id_singer').val();
    	$('#id_artist_name').val(a_name);
    	$('#add_music_form').validationEngine('hideAll');
    	$('#img_musician_1').attr('src',$('#img_musician').attr('src'));
    });
    
    $('#btn_continue').click(function(){
    	$('#link_back').trigger("click");
    });
    
    $('#btn_continue').click(function(){
    	$('#song_exist_ret').val('True');
    	$('#btn_submit_add').val('继续发布');
    });
    
    $('#btn_song_detail').click(function(){
    	 if(song_details_url != null)
    	 	window.open(song_details_url,'_blank');
    });
    
    $('#btn_close').click(function() {
    	tb_remove();
    	if($.browser.msie)//变态的IE
    		$('#TB_overlay').remove();
    });
    
   	var options = { 
        target: '#add_music_msg', 
        dataType: 'json', 
        beforeSubmit: showUploadRequest, 
        success: showUploadResponse 
    }; 

	$('#upload_headshot_form').submit(function() { 
	    $(this).ajaxSubmit(options); 
	    return false; 
	}); 
    
   	function showUploadRequest(formData, jqForm, options) {
   		var ret_name = jQuery('#upload_headshot_form').validationEngine('validateField', '#id_artist_name');
   		var ret_file = jQuery('#upload_headshot_form').validationEngine('validateField', '#id_headshot');
		if(ret_name || ret_file)
		{
			return false;
		}
		else
		{
	 		$('#img_musician_1').attr('src',static_url + 'images/loading_1.gif');
	 		$('#btn_upload').attr('disabled',true);
	    	return true; 
    	}
	} 
 
	// post-submit callback 
	function showUploadResponse(jsonData, statusText)  { 
		$('#img_musician_1').attr('src',jsonData.url);
		$('#btn_upload').attr('disabled',false);
    } 
    
    var AddOptions = { 
		target: '#add_music_msg', 
		dataType: 'json', 
		beforeSubmit: showAddRequest, 
		success: showAddResponse 
	}; 
		
	$('#add_music_form').submit(function() { 
		$(this).ajaxSubmit(AddOptions); 
		return false; 
	}); 
		    
	function showAddRequest(formData, jqForm, options) {
		if(validateAddForm() == false) {
			$('#btn_submit_add').attr('disabled',true);
			return true;
		}
		else {
			return false;
		} 
	} 
		 
	function showAddResponse(jsonData, statusText)  { 
		if(!jsonData.saved) {
			if(jsonData.validated) {
			
				song_details_url = jsonData.song_url;
				
				$('.add_music_msg').html('<span>已经有人添加类似音乐！</span>');
	            $('.add_music_msg span').attr('style','color:red; font-weight:bold;');
	            
	            var html_song_info = '<div class="exist_field"><label>歌名：</label>' + jsonData.title + '</div>';
	            html_song_info += '<div class="exist_field"><label>艺术家：</label>' + ((jsonData.singer == '' || jsonData.singer == null) ? '&nbsp;' : jsonData.singer) + '</div>';
	            html_song_info += '<div class="exist_field"><label>发布者：</label>' + jsonData.user + '</div>';
	            html_song_info += '<div class="exist_field"><label>发布时间：</label>' + jsonData.post_datetime + '</div>';
	            
	            $('#exist_song_content').html(html_song_info);
	            
	            $('#add_music_basic_info').hide();
	            $('#exist_song').show();
	            $('#link_show_exist_song').trigger("click");
            } else {
            	$('.add_music_msg').html('<span>输入错误，可能是链接不符合要求，请检查！</span>');
            	$('.add_music_msg').effect("highlight", {}, 3000);
            }
		}
		else {
			$('#song_exist_ret').val('False');
			$('#add_music_form input').each(function(){
				if($(this).attr('type') == 'text') {
					$(this).val('');
				}
			});
			$('#id_intro').val('');
			$('#id_genre').val('');
			$('#id_song_cover_url').val('images/artist.png');
			$('#img_musician').attr('src',static_url + 'images/artist.png');
			
			$('.add_music_msg').html('<span>发布成功 :)</span>');
			$('#update_msg').slideDown();
        	$('.add_music_msg span').attr('style','color:green; font-weight:bold;');
        	$('.add_music_msg').effect("highlight", {}, 3000);
		}
		
		$('#btn_submit_add').attr('disabled',false);
		$('#btn_submit_add').val('继续发布');
	}
	
	function validateAddForm() {
    	var ret = false;
    	$('.add_music_field input').each(function(){
    		if(jQuery('#add_music_form').validationEngine('validateField', '#' + $(this).attr('id')))
    		{
    			ret = true;
    		}
    	});
    	if(jQuery('#add_music_form').validationEngine('validateField', '#id_intro'))
    	{
    		ret = true;
    	}
    	if(jQuery('#add_music_form').validationEngine('validateField', '#id_genre'))
    	{
    		ret = true;
    	}
    	
    	return ret;
    }
    
    $('#btn_back').click(function() {
    	$('#link_back').trigger("click");
    });
    
    $('#link_back').click(function() {
    	$('.add_music_msg').html('1、输入歌曲链接时请注意空格和折行等问题。<br>2、带星号为必填项。');
    	$('#upload_headshot_form').validationEngine('hideAll');
    	$('#img_musician').attr('src', $('#img_musician_1').attr('src'));
    	$('#id_song_cover_url').val($('#img_musician_1').attr('src').replace(media_url,''));
    	if($('#id_singer').val().length == 0) {
    	    $('#id_singer').val($('#id_artist_name').val());
    	}
    	$('#add_music_artist_headshot').hide();
    	$('#upload_headshot_form').hide();
    	$('#exist_song').hide();
    	$('#exist_song_content').hide();
    	$('#exist_seprator').hide();
    	$('#exist_buttons').hide();
    	
    	$('#add_music_basic_info').show();
    });
    
    $('#link_show_exist_song').click(function(){
    	$('#exist_song').show();
    	$('#exist_song_content').show();
    	$('#exist_seprator').show();
    	$('#exist_buttons').show();
    });
    
    $('#id_singer').blur(function() {
    	getArtistHeadshot();
    });
    
    function getArtistHeadshot() {
    	var artist_name = $('#id_singer').val();
    	get_url = get_song_cover_url;
    	if(artist_name != null && artist_name != '') {
	    	$.ajax({
	                type: 'GET',
	                contentType: 'application/json',
	                url: get_url,
	                data: 'artist=' + encodeURIComponent(artist_name),
	                dataType: 'json',
	                error: function (XmlHttpRequest, textStatus, errorThrown){
				       $('#img_musician').attr('src',static_url + 'images/artist.png')
				    }, 
	                success: function(jsonData) {
	                	if(jsonData.avatar_url.indexOf('artist.png') == -1)
	                	{
	                    	$('#img_musician').attr('src', media_url + jsonData.avatar_url);
	                    	$('#id_song_cover_url').val(jsonData.avatar_url);
	                    }
	                    else
	                    {
	                    	$('#img_musician').attr('src',jsonData.avatar_url);
	                    }
	                }
	            });
        }
    }
    
    
    $('#id_audio_url').blur(function() {
    	var ret = jQuery('#add_music_form').validationEngine('validateField', '#id_audio_url');
    	var mp3_url = $('#id_audio_url').val();
    	if(ret == false && mp3_url != '') {
    		$.ajax({
                    type: 'POST',
                    contentType: 'application/json',
                    url: get_mp3_info_url,
                    data: 'id_audio_url=' + encodeURI(mp3_url),
                    dataType: 'json',
                    beforeSend: function() {
                    	disabledInputs(true,false);
                    },
                    error: function (XmlHttpRequest, textStatus, errorThrown){
			            disabledInputs(false,false);
			            $('#id_title').val('');
                    	$('#id_singer').val('');
                    	$('#id_album').val('');
			        }, 
                    success: function(result) {
                    	$('#id_title').val(result.title);
                    	$('#id_singer').val(result.artist);
                    	$('#id_album').val(result.album);
                    	disabledInputs(false,true);
                    	
                    	if(result.artist != null && result.artist != undefined && result.artist != '') {
                    		getArtistHeadshot();
                    	}
                    }
            });
            
            function disabledInputs(ret, returnRet) {
            
            	$('#add_music_form input').each( function() {
            		$(this).attr('disabled', ret);
            	});
            	
            	$('#btn_cancel_add').attr('disabled', false);
            	
            	if(ret)
            	{
            		$('.add_music_msg').html('<img src="' + static_url + 'images/loading_icon_small.gif"> 正在分析链接，可能需要点时间，请稍候...');
            	}
            	else
            	{
            		if(returnRet)
            		{
            			$('.add_music_msg').html('<span>请核对自动获取的音乐文件信息，可以修改。</span>');
            			$('.add_music_msg span').attr('style','color:green; font-weight:bold;');
            		}
            		else
            		{
            			$('.add_music_msg').html('<span>请在下面添加歌曲的必要信息。</span>');
            			$('.add_music_msg span').attr('style','font-weight:bold;');
            		}
            		$('.add_music_msg').effect("highlight", {}, 3000);
            	}
            }
    	}
    });
    
     
});