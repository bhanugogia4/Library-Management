from django.urls import path
from circulation.views import checkout_book, return_book, reserve_book


urlpatterns = [
    path('checkout/<int:book_id>', view=checkout_book, name='checkout_book'),
    path('return', view=return_book, name='return_book'),
    path('reserve/<int:book_id>', view=reserve_book, name='reserve_book')
]