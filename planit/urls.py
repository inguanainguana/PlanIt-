from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django.contrib.sitemaps.views import sitemap

from mainapp.sitemaps import StaticViewSitemap, EventSitemap, BudgetSitemap, TaskSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'events': EventSitemap,
    'budget': BudgetSitemap,
    'tasks': TaskSitemap,
}
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mainapp.urls', namespace='mainapp')),
    path('authapp/', include('authapp.urls', namespace='authapp')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
