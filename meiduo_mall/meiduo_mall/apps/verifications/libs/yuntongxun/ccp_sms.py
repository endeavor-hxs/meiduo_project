# -*- coding:utf-8 -*-

# import ssl
# ssl._create_default_https_context =ssl._create_stdlib_context # 解决Mac开发环境下，网络错误的问题

from verifications.libs.yuntongxun.CCPRestSDK import REST

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountSid = '8a216da8757784cd017593ce2b660c43'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = '4bb18004ced24784aebbf44a6f4dc955'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8a216da8757784cd017593ce2c2d0c4a'

# 说明：请求地址，生产环境配置成app.cloopen.com
_serverIP = 'sandboxapp.cloopen.com'

# 说明：请求端口 ，生产环境为8883
_serverPort = "8883"

# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'


# 云通讯官方提供的发送短信代码实例
# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id


class CCP(object):
    '''发送短信验证码的单例类'''

    def __new__(cls, *args, **kwargs):
        """
        定义单例类的初始化方法
        """
        # 判断单例是否存在，_instance类对象存放的就是单例
        if not hasattr(cls, '_instance'):
            # 如果单例不存在返回初始化方法
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._instance.rest = REST(_serverIP, _serverPort, _softVersion)
            cls._instance.rest.setAccount(_accountSid, _accountToken)
            cls._instance.rest.setAppId(_appId)
        # 返回单例
        return cls._instance

    def send_template_sms(self, to, datas, tempId):
        """
        发送模板短信单例方法
        :param to: 注册手机号
        :param datas: 模板短信内容数据，格式为列表，例如：['123456', 5]，如不需替换请填 ''
        :param temp_id: 模板编号，默认免费提供id为1的模板
        :return: 发短信结果
        """
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        if result.get("statusCode") == "00000":
            return 0
        else:
            return -1


if __name__ == '__main__':
    # 注意： 测试的短信模板编号为1
    CCP( ).send_template_sms('18696799134', ['123456', 5], 1)
