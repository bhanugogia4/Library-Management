from enum import Enum

from django.db import models

from book.models import Book
from member.models import Member


# Create your models here.
class EventTypeEnum(models.IntegerChoices):
    CHECKOUT = 1
    RETURN = 2
    FULFILL = 3

class Event(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    event_type = models.SmallIntegerField(EventTypeEnum.choices)
    returned = models.BooleanField(null=True)


class ReservationQueue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
