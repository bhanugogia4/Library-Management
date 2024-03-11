from datetime import datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from rest_framework import status

from circulation.models import Event, EventTypeEnum
from member.models import Member


# Create your views here.
@require_http_methods('GET')
def member_dues(request, member_id):
    try:
        member = Member.objects.filter(id=member_id).last()
        if member is None:
            return JsonResponse(data={"message": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        due_date = datetime.now()-timedelta(days=7)
        due_checkout_events = Event.objects.filter(member_id=member_id, event_type=EventTypeEnum.CHECKOUT, returned=False, date__lt=due_date).all()
        response = []
        # Pagination can be implemented here
        for event in due_checkout_events:
            event_dict = {
                "book_id": event.book_id,
                "date": event.date,
                "due": (due_date - event.date.replace(tzinfo=None)).days*50
            }
            response.append(event_dict)
        return JsonResponse(data=response, status=status.HTTP_200_OK, safe=False)
    except Exception as e:
        return JsonResponse(data={"error": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
