from django.shortcuts import render

# Create your views here.
from django.views import View


class IndexView(View):
    '''首页广告'''

    def get(self, request):
        '''返回首页广告页面'''
        return render(request, 'index.html')
