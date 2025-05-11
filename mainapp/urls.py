
from django.urls import path

import mainapp.views as mainapp
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap


app_name = 'mainapp'

urlpatterns = [
    path('', mainapp.index, name='index'),
    path('events/', mainapp.event_list, name='event_list'),
    path('events/<int:event_id>/', mainapp.event_detail, name='event_detail'),
    path('events/<int:event_id>/tasks/', mainapp.task_detail, name='task_detail'),
    path('events/create/', mainapp.create_event, name='create_event'),
    path('events/<int:event_id>/tasks/create/', mainapp.create_task, name='create_task'),

    path('update/<int:event_id>/', mainapp.update_event, name='update_event'),
    path('delete/<int:event_id>/', mainapp.delete_event, name='delete_event'),
    path('task/update_status/<int:task_id>/', mainapp.update_task_status, name='update_task_status'),
    path('task/edit/<int:task_id>/', mainapp.edit_task, name='edit_task'),
    path('task/delete/<int:task_id>/', mainapp.delete_task, name='delete_task'),
    path('invite/', mainapp.send_invitation, name='send_invitation'),
    path('invitations/confirm/<uuid:confirmation_link>/', mainapp.confirm_invitation, name='confirm_invitation'),
    path('invitations/', mainapp.invitation_list, name='invitation_list'),
    path('invitations/edit/<int:invitation_id>/', mainapp.edit_invitation, name='edit_invitation'),
    path('invitations/delete/<int:invitation_id>/', mainapp.delete_invitation, name='delete_invitation'),
    path('budget/', mainapp.budget_list, name='budget_list'),
    path('add_expense/<int:event_id>/', mainapp.add_expense, name='add_expense'),
    path('add_income/<int:event_id>/', mainapp.add_income, name='add_income'),
    path('add_budget/<int:event_id>/', mainapp.add_budget, name='add_budget'),
    path('edit_budget/<int:event_id>/', mainapp.edit_budget, name='edit_budget'),
    path('delete_data/<int:event_id>/', mainapp.delete_data, name='delete_data'),
    path('support/', mainapp.support_view, name='support'),
    path('all_answers', mainapp.all_faqs_view, name='all_answers'),
    path('review/', mainapp.write_review, name='write_review'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
