from django.urls import path
from booker_app.views import (
    BookView, BookFormView, BookDetailsView, BookDelete, BookListJsonView,
    ImportBookView
)

urlpatterns = [
    path('book_list/', BookView.as_view(), name='book_list'),
    path('book_list_json/', BookListJsonView.as_view(), name='book_list_json'),
    path(
        'book_details/<int:book_id>/',
        BookDetailsView.as_view(),
        name='book_details'
    ),
    path('add_book/', BookFormView.as_view(), name='add_book'),
    path(
        'book_details/<int:id>/delete_book/',
        BookDelete.as_view(),
        name='delete_book'
    ),
    path('import_book/', ImportBookView.as_view(), name='import_book'),
]
