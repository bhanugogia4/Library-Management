from django.db import models

# Create your models here.

class Book(models.Model):
    book_name = models.CharField(max_length=255)
    no_of_copies = models.IntegerField()
    available_copies = models.IntegerField()