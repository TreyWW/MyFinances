from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path as url
from django.urls import path, include

from backend.views.core import other, passwords, api, settings as settings_v, invoices
from backend.views.core.other.index import index, dashboard

# from backend.views.core.api.v1.user import settings

url(r'^frontend/static/(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0]})

urlpatterns = [
                  path('', index, name='index'),
                  path('dashboard', dashboard, name='dashboard'),
                  path('dashboard/settings', settings_v.view.settings_page, name='user settings'),
                  path('dashboard/profile/change_password', settings_v.view.change_password, name='user settings change_password'),
                  path('dashboard/invoices/', invoices.dashboard.invoices_dashboard, name='invoices dashboard'),
                  path('dashboard/invoices/create/', invoices.dashboard.invoices_dashboard, name='invoices dashboard create'),
                  path('dashboard/invoices/<str:id>', invoices.dashboard.invoices_dashboard_id, name='invoices dashboard edit'),

                  path('social-auth/', include('social_django.urls', namespace='social')),
                  # path('dashboard/invoices/<str:id>/edit', invoices.dashboard.invoices_dashboard_id, name='invoices dashboard'),

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
              ] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

handler500 = "backend.views.core.other.errors.universal"
handler404 = "backend.views.core.other.errors.universal"
handler403 = "backend.views.core.other.errors.e_403"
