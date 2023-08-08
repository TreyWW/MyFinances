from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path as url
from django.urls import path

from backend.views.core import other, passwords
from backend.views.core.other.index import index

url(r'^ui/static/(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0]})

urlpatterns = [
                  path('', index, name='index'),

                  path('login/', other.login.login_page, name='login'),
                  path('logout/', other.login.logout_view, name='logout'),


                  path('login/set-password/<str:secret>', passwords.view.set_password, name='user set password'),
                  path('login/set-password/<str:secret>/set', passwords.set.set_password_set,
                       name='user set password set'),
                  path('login/reset-password/', passwords.generate.password_reset, name='user set password reset'),

                  path('admin/generate-password', passwords.generate.set_password_generate,
                       name='admin set password generate'),
              ] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

handler500 = "backend.views.core.other.errors.universal"
handler404 = "backend.views.core.other.errors.universal"
handler403 = "backend.views.core.other.errors.e_403"
