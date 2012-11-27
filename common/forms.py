# coding=utf-8
from django import forms
from captcha.fields import CaptchaField

class SingleCaptchaForm(forms.Form):
    captcha = CaptchaField()