from django import http
from django.shortcuts import render
import random, logging
# Create your views here.
from django.views import View

from django_redis import get_redis_connection
from meiduo_mall.utils.response_code import RETCODE
from verifications.libs.captcha.captcha import captcha
from . import constants
from verifications.libs.yuntongxun.ccp_sms import CCP

# 创建日志输出器
logger = logging.getLogger('django')


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


class SMSCodeView(View):

    def get(self, request, mobile):

        # 接收参数
        image_code_client = request.GET.get("image_code")
        uuid = request.GET.get('uuid')
        # 校验参数
        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})
        # 判断用户是否频繁接收验证码
        redis_conn = get_redis_connection('verify_code')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # 提取服务器图形验证码
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server == None:
            # 图形验证码失效或者不存在
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})
        # 删除图形验证码
        redis_conn.delete('img_%s' % uuid)

        # 对比验证码
        image_code_server = image_code_server.decode( )
        if image_code_server.lower( ) != image_code_client.lower( ):
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码不一致'})

        # 生成短信验证码：生成6位数验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger(sms_code)
        # 创建Redis管道
        pl = redis_conn.pipeline( )
        # 将Redis请求添加到队列
        # 保存短信验证码
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存短信验证码的标记
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行请求
        pl.execute( )

        # 发送短信验证码
        CCP( ).send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                 constants.SEND_SMS_TEMPLATE_ID)
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})
