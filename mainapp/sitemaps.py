from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from mainapp.models import Event, Budget, Task


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return ['index', 'event_list', 'support', 'all_answers', 'write_review']

    def location(self, item):
        return reverse('mainapp:' + item)


class EventSitemap(Sitemap):
    priority = 0.7
    changefreq = 'daily'

    def items(self):
        return Event.objects.filter(deadline_date__gte="2025-01-01")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('mainapp:event_detail', kwargs={'event_id': obj.id})


class BudgetSitemap(Sitemap):
    priority = 0.4
    changefreq = 'daily'

    def items(self):
        return Budget.objects.filter(event__deadline_date__gte="2025-01-01")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('mainapp:budget_list')


class TaskSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return Task.objects.filter(
            event__deadline_date__gte="2025-01-01")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('mainapp:task_detail', kwargs={'event_id': obj.event.id})
