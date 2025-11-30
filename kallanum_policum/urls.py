from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from game import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('test-guide/', TemplateView.as_view(template_name='test_guide.html'), name='test_guide'),
    path('room/<str:room_code>/', views.room, name='room'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
