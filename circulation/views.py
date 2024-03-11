from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.parsers import JSONParser
from rest_framework import status
from circulation.models import Event, EventTypeEnum, ReservationQueue
from book.models import Book
from member.models import Member


# Create your views here.
@csrf_exempt
@require_http_methods("POST")
def checkout_book(request: HttpRequest, book_id):
    try:
        request_data = JSONParser().parse(request)
        member_id = request_data.get('member_id')
        if member_id is None:
            raise Exception("member_id is required")
        member = Member.objects.filter(id=member_id).last()
        if member is None:
            return JsonResponse(data={"message": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        book = Book.objects.filter(id=book_id).last()
        if book is None:
            return JsonResponse(data={"message": "book_id is invalid"}, status=status.HTTP_404_NOT_FOUND)
        event = Event.objects.filter(member_id=member_id, book_id=book_id, event_type=EventTypeEnum.CHECKOUT, returned=False).last()
        if event is not None:
            return JsonResponse(data={"message": f'This book is already checked out by the user event_id - {event.id}'}, status=status.HTTP_403_FORBIDDEN)
        if book.available_copies > 0:
            with transaction.atomic():
                event = Event.objects.create(
                   book_id=book_id,
                   member_id=member_id,
                    event_type=EventTypeEnum.CHECKOUT,
                    returned = False
                )
                book.available_copies -= 1
                book.save()
                return JsonResponse(data={"message": f'book_id - {book_id} checked out by member - {member_id} with event_id - {event.id}'}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(data={"message": f'book_id - {book_id} not available now. You can reserve and add to waitlist'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse(data={"error": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@require_http_methods("POST")
def return_book(request: HttpRequest):
    try:
        request_data = JSONParser().parse(request)
        member_id = request_data.get('member_id')
        book_id = request_data.get('book_id')
        if member_id is None:
            raise Exception("member_id is required")
        if book_id is None:
            raise Exception("book_id is required")
        member = Member.objects.filter(id=member_id).last()
        if member is None:
            return JsonResponse(data={"message": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        book = Book.objects.filter(id=book_id).last()
        if book is None:
            return JsonResponse(data={"message": "book_id is invalid"}, status=status.HTTP_404_NOT_FOUND)
        event = Event.objects.filter(member_id=member_id, book_id=book_id, event_type=EventTypeEnum.CHECKOUT, returned=False).last()
        if event is None:
            return JsonResponse(data={"message": "No such checkout created"}, status=status.HTTP_404_NOT_FOUND)
        else:
            with transaction.atomic():
                Event.objects.create(
                    member_id=member_id,
                    book_id=book_id,
                    event_type = EventTypeEnum.RETURN
                )
                event.returned = True
                event.save()
                reservation_queue_obj = ReservationQueue.objects.filter(id=book_id).first()
                if reservation_queue_obj is not None:
                    Event.objects.create(
                        member_id=reservation_queue_obj.member_id,
                        book_id=book_id,
                        event_type=EventTypeEnum.FULFILL
                    )
                    reservation_queue_obj.delete()
                    reservation_queue_obj.save()
                else:
                    book.available_copies += 1
                    book.save()
            return JsonResponse(data={"message": "Book has been returned"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return JsonResponse(data={"error": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@require_http_methods("POST")
def reserve_book(request: HttpRequest, book_id):
    try:
        request_data = JSONParser().parse(request)
        member_id = request_data.get('member_id')
        if member_id is None:
            raise Exception("member_id is required")
        book = Book.objects.filter(id=book_id).last()
        if book is None:
            return JsonResponse(data={"message": "book_id is invalid"}, status=status.HTTP_404_NOT_FOUND)
        member = Member.objects.filter(id=member_id).last()
        if member is None:
            return JsonResponse(data={"message": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        reservation_queue_obj = ReservationQueue.objects.create(
            book_id=book_id,
            member_id=member_id
        )
        return JsonResponse(data={"message": f'book_id - {book_id} has been reserved with waitlist number - {reservation_queue_obj.id}'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return JsonResponse(data={"error": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)