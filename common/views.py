# coding=utf-8
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from common.forms import SingleCaptchaForm

def get_single_captcha(request, template_name):
    template_var={}
    if request.is_ajax():
        form = SingleCaptchaForm()
        template_var["form"] = form
    else:
        form = {}
    return render_to_response(template_name, template_var, context_instance=RequestContext(request))


