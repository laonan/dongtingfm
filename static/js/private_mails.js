var del_thread_id;
var del_conversational_partner;
function del_thread(thread_id, conversational_partner) {
	del_thread_id = thread_id;
	del_conversational_partner = conversational_partner;
	$('#link_del_thread_dialog').trigger('click');
}