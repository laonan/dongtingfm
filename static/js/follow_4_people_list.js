$(document).ready(function() {

	$('.link_follow').click(function(){
			var follow_obj_id = $(this).attr('id');
			var following_userid = follow_obj_id.split('_')[3];
			$.ajax({
		                type: 'GET',
		                contentType: 'application/json',
		                url: follow_person_url,
		                data: 'following_userid=' + following_userid,
		                dataType: 'json',
		                beforeSend: function() {
	                    	$('#' + follow_obj_id).attr('disabled',true);
	                    },
		                error: function (XmlHttpRequest, textStatus, errorThrown){
					       alert(errorThrown);
					    }, 
		                success: function(jsonData) {
		                	if(jsonData.excuted ) {
			                	if (jsonData.action == 'follow'){
			                		$('#' + follow_obj_id).text('已关注');
			                		
			                		var fllowing_count = $('#user_box_following_count').text();
			                		$('#user_box_following_count').text(parseInt(fllowing_count, 10) + 1);
			                	}
			                }
		                }
		            });
		});
});