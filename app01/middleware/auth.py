from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class Middleware(MiddlewareMixin):
    def process_request(self, request):
        # 排除不需要登录就能访问的界面
        if request.path_info == "/login/":
            return
        # 读取当前访问的session
        info_dict = request.session.get('info')
        if info_dict:
            return
        # 没有登录过返回登入界面
        return redirect('/login/')
