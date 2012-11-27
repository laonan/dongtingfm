$(document).ready(function() {
    $('#settings_form').validationEngine({scroll:false});
    $('#change_pwd_form').validationEngine({scroll:false});
    
    $('#tab_options li').click(function() {
    	$('#tab_options li').each(function(){
    		$(this).removeClass('c_tab');
    		$(this).addClass('o_tab');
    	});
    	
    	var className = $(this).attr('class');
    	if(className == 'o_tab') {
    		$(this).removeClass('o_tab');
    		$(this).addClass('c_tab');
    	}
    	
    	var liId = $(this).attr('id');
    	if(liId == 'li_cpwd') {
    		$('#settings_tab1').hide();
    		$('#settings_tab2').fadeIn();
    	} else {
    		$('#settings_tab2').hide();
    		$('#settings_tab1').fadeIn();
    	}
    	
    	$('#settings_form').validationEngine('hideAll');
    	$('#change_pwd_form').validationEngine('hideAll');
    });
    
    var options = { 
        target: '#add_music_msg', 
        dataType: 'json', 
        beforeSubmit: showChangePasswordRequest, 
        success: showChangePasswordResponse 
    }; 

	$('#change_pwd_form').submit(function() { 
	    $(this).ajaxSubmit(options); 
	    return false; 
	}); 
    
   	function showChangePasswordRequest(formData, jqForm, options) {
   		var ret = true;
   		
    	$('#change_pwd_form .fieldWrapper input').each(function(){
    		if(jQuery('#change_pwd_form').validationEngine('validateField', '#' + $(this).attr('id'))) {
    			ret = false;
    		}
    	});
    	
    	if(ret) {
    		$('#btn_cpwd').attr('disabled',true);
    	}
    	
    	return ret;
	} 
 
	// post-submit callback 
	function showChangePasswordResponse(jsonData, statusText)  { 
		var msgClassName = $('#cpwd_msg').attr('class');
		$('#cpwd_msg').removeClass(msgClassName);
		if(jsonData.changed) {
			$('#cpwd_msg').addClass('success');
			$('#cpwd_msg').text('密码修改成功。')
		} else {
			$('#cpwd_msg').addClass('error');
			$('#cpwd_msg').text('密码修改失败：' + jsonData.msg);
		}
		$('#btn_cpwd').attr('disabled',false);
    }
 });