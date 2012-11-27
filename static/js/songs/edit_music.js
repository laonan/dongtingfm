$(document).ready(function() {
	$('#edit_music_form').validationEngine({
    	scroll:false
    });
    
    var original_audio_url = $('#id_audio_url').val();
    var original_flash_url = $('#id_flash_url').val();
    if(original_audio_url == '' && original_flash_url != '') {
		$('ul.tabs li').removeClass('active'); 
		$('ul.tabs li:last').addClass('active'); 
		$('.tab_content').hide(); 

		var activeTab = $('ul.tabs li:last').find('a').attr('href'); //Find the href attribute value to identify the active tab + content
		$(activeTab).fadeIn(); //Fade in the active ID content
    }
    
	$('#btn_close').click(function() {
    	tb_remove();
    	$('#edit_music_form').validationEngine('hideAll');
    });
    
    var options = { 
        //target: '#add_music_msg', 
        dataType: 'json', 
        beforeSubmit: showRequest, 
        success: showResponse 
    }; 

	$('#edit_music_form').submit(function() { 
	    $(this).ajaxSubmit(options); 
	    return false; 
	}); 
    
   	function showRequest(formData, jqForm, options) {
   		return true;
	} 
 
	// post-submit callback 
	function showResponse(jsonData, statusText)  {
		if(jsonData.edited)
			window.location.href = window.location.href;
    } 
});