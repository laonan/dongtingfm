var timeout = 500;
var closetimer = 0;
var ddmenuitem = 0;

function ddm_open() {	
	ddm_canceltimer();
	ddm_close();
	ddmenuitem = $(this).find('div').eq(0).css('display', 'block');
}

function ddm_close() {
	if(ddmenuitem)
		ddmenuitem.css('display', 'none');
}

function ddm_timer() {	
	closetimer = window.setTimeout(ddm_close, timeout);
}

function ddm_canceltimer() {	
	if(closetimer) {
		window.clearTimeout(closetimer);
		closetimer = null;
	}
}

$(document).ready(function() {
	$('#nav_ul > li').bind('mouseover', ddm_open);
	$('#nav_ul > li').bind('mouseout',  ddm_timer);
});