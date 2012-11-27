$(document).ready(function() {

});

var remove_follow_id;
var remove_follow_username;
var remove_follow_type;
function remove_follow(follow_id, follow_username, remove_type) {
	remove_follow_id = follow_id;
	remove_follow_username = follow_username;
	remove_follow_type = remove_type;
	$('#link_remove_follow_dialog').trigger('click');
}