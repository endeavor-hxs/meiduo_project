import re
from django import http
from django.contrib.auth import login
from django.db import DatabaseError
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.views import View
from meiduo_mall.utils.response_code import RETCODE
from users.models import User


class UsernameCountView(View):
    # 用户名重复的校验
    def get(self, request, username):
        count = User.objects.filter(username=username).count( )
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count( )
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class RegisterView(View):

    def get(self, request):
        '''用户注册的接口'''
        return render(request, 'register.html')

    def post(self, request):
        '''用户注册逻辑实现'''
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return HttpResponseForbidden('缺少必传参数！')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9-_]{5,20}$', username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return HttpResponseForbidden('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return HttpResponseForbidden('请勾选用户协议')

        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})
        # 响应注册结果
        # return http.HttpResponse('注册成功，重定向到首页')
        # 状态保持
        login(request, user)

        return redirect(reverse('contents:index'))
