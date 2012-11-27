$(document).ready(function() {
	
});

var unblock_userid;
var unblock_username;
function unblock(bad_guy_id, bad_guy_name) {
	unblock_userid = bad_guy_id;
	unblock_username = bad_guy_name;
	$('#link_unblock_user').trigger('click');
}