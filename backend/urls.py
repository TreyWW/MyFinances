from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path as url
from django.urls import path, include

from backend.views.core import other, passwords, api
from backend.views.core.other.index import index, dashboard
# from backend.views.core.api.v1.user import profile

url(r'^ui/static/(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0]})

urlpatterns = [
                  path('', index, name='index'),
                  path('dashboard', dashboard, name='dashboard'),
                  path('login/', other.login.login_page, name='login'),
                  path('logout/', other.login.logout_view, name='logout'),
                  path('login/create_account', other.login.create_account_page, name='login create_account'),
                  path('login/forgot_password', other.login.forgot_password_page, name='login forgot_password'),
                  path('login/reset-password/', passwords.generate.password_reset, name='user set password reset')
                  ,
                  # path('api/v1/user/profile/toggle_theme', api.v1.user.profile.toggle_theme, name='api v1 user toggle_theme'),

                  path('login/set-password/<str:secret>', passwords.view.set_password, name='user set password'),
                  path('login/set-password/<str:secret>/set', passwords.set.set_password_set,
                       name='user set password set'),

                  path('admin/generate-password', passwords.generate.set_password_generate,
                       name='admin set password generate'),
                # path("__reload__/", include("django_browser_reload.urls")),
              ] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

handler500 = "backend.views.core.other.errors.universal"
handler404 = "backend.views.core.other.errors.universal"
handler403 = "backend.views.core.other.errors.e_403"
