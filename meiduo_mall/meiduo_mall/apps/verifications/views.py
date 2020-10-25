from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from verifications.libs.captcha.captcha import captcha
from . import constants


class ImageCodeView(View):

    def get(self, request, uuid):
        # 生成图片验证码
        text, image = captcha.generate_captcha( )
        # 保存图片验证码
        redis_conn = get_redis_connection('verify_code')
        # redis_conn.setex('img_%s' % uuid,失效时间,text)
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        # 相应图片验证码
        return http.HttpResponse(image, content_type='image/jpg')
