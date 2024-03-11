from django.urls import path
from member.views import member_dues
urlpatterns = [
    path('member/<int:member_id>/dues', view=member_dues, name='member_dues')
]