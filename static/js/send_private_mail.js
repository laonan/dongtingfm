$(document).ready(function() {
	$('#send_form').validationEngine({
    	scroll:false
    });
    
    $('#id_to_user').focus(function(){
    	if($(this).val() == '请输入昵称...')
    		$(this).val('');
    });
    
    
    $('#btn_cancel_send').click(function(){
    	$('#send_form').validationEngine('hideAll');
    	tb_remove();
    });
    
    var options = { 
        target: '#private_mail_info', 
        dataType: 'json', 
        beforeSubmit: showRequest, 
        success: showResponse 
    }; 

	$('#send_form').submit(function() { 
	    $(this).ajaxSubmit(options); 
	    return false; 
	}); 
    
   	function showRequest(formData, jqForm, options) {
   		var ret_to_user = jQuery('#send_form').validationEngine('validateField', '#id_to_user');
   		var ret_content = jQuery('#send_form').validationEngine('validateField', '#id_mail_content');
   		if(ret_to_user || ret_content)
		{
			return false;
		}
		else
		{
	 		$('#btn_send').attr('disabled',true);
	    	return true; 
    	}
	} 
 
   	var SysSecond;
   	var timeID;
   	
	// post-submit callback 
	function showResponse(jsonData, statusText)  { 
		if(jsonData.sent) {
			SysSecond = 3;
			timeID = window.setInterval(SetRemainTime, 1000);
			$('#id_to_user').attr('disabled',true);
			$('#id_mail_content').attr('disabled',true);
			$('.private_mail_info').html('<span style="color:green;font-weight: bold;">私信发送成功！窗口将在</span><em style="color:#ff0000;font-weight: bold;" id="em_secs">' + SysSecond + '</em><span style="color:green;font-weight: bold;">秒内关闭。</span>');
			//$('.private_mail_info').effect("highlight", {}, 1000, afterHighlight);
		} else {
			$('.private_mail_info').html('<span style="color:red;font-weight: bold;">' + jsonData.msg + '</span>');
			$('.private_mail_info').effect("highlight", {}, 3000);
			$('#btn_send').attr('disabled',false);
		}
    }
    
    /*function afterHighlight() {
    	InterValOb = window.setInterval(SetRemainTime, 1000);
    }*/
    
	function SetRemainTime(){
    	if (SysSecond > 0) {
            //alert(SysSecond);
            SysSecond = SysSecond - 1;
            $('#em_secs').text(SysSecond);
    	} else {
    		window.clearInterval(timeID);
    		tb_remove();
    	}
    }
});