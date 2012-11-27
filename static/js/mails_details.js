var del_mail_id;
function del_mail(mail_id) {
	del_mail_id = mail_id;
	$('#link_del_mail_dialog').trigger('click');
}

$(document).ready(function() {
	$('#send_form').validationEngine({
    	scroll:false
    });
    
    var options = { 
        //target: '#add_music_msg', 
        dataType: 'json', 
        beforeSubmit: showRequest, 
        success: showResponse 
    }; 

	$('#send_form').submit(function() { 
	    $(this).ajaxSubmit(options); 
	    return false; 
	}); 
    
   	function showRequest(formData, jqForm, options) {
   		var ret = jQuery('#send_form').validationEngine('validateField', '#id_mail_content');
   		if(ret)
   			return false;
   		else
   			return true;
	} 
 
	// post-submit callback 
	function showResponse(jsonData, statusText)  {
		if(jsonData.sent) {
			window.location.href = window.location.href; 
		} else {
			$('.xMailContent').validationEngine('showPrompt', jsonData.msg, '', 'topLeft', false);
			setTimeout(function() {  
				$('.xMailContent').validationEngine('hide');  
			}, 2000);
		}
    } 
});