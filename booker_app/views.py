from django.shortcuts import render, redirect, reverse
from django.http import (
    HttpResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
)
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import DeleteView

from booker_app.forms import BookForm, IdentifierForm
from booker_app.models import Book, Identifier


class BookView(View):
    def get(self, request):
        book_list = Book.objects.all()
        context = {'book_list': book_list}
        return render(request, 'book_list.html', context)


class BookListJsonView(View):
    def get(self, request):
        book_list = list(Book.objects.values())
        context = {'book_list': book_list}
        return JsonResponse(book_list, safe=False)


class BookDetailsView(View):
    def get(self, request, book_id):
        book = Book.objects.get(id=book_id)
        if not book:
            return HttpResponseNotFound('<h1>Book not found</h1>')
        form_book = BookForm(
            initial={
                'authors': book.authors,
                'title': book.title,
                'pub_date': book.pub_date,
                'page_count': book.page_count,
                'language': book.language,
                'cover_image_adress': book.cover_image_adress
            }
        )
        identifiers = Identifier.objects.filter(book_id=book.id).all()
        forms_ident = [
            IdentifierForm(
                initial={
                    'type': ident.type,
                    'value': ident.value,
                    'book': ident.book
                }
            ) for ident in identifiers
        ]
        context = {'form_book': form_book, 'forms_ident': forms_ident}
        return render(request, 'book_details.html', context)

    def post(self, request, book_id):
        book = Book.objects.get(id=book_id)
        if not book:
            return HttpResponseNotFound('<h1>Book not found</h1>')
        form_book = BookForm(
            request.POST,
            initial={
                'authors': book.authors,
                'title': book.title,
                'pub_date': book.pub_date,
                'page_count': book.page_count,
                'language': book.language,
                'cover_image_adress': book.cover_image_adress
            },
            instance=book
        )
        identifiers = Identifier.objects.filter(book_id=book.id).all()
        forms_ident = [
            IdentifierForm(
                request.POST,
                initial={
                    'type': ident.type,
                    'value': ident.value,
                    'book': ident.book
                },
                instance=ident) for ident in identifiers
        ]
        if form_book.is_valid():
            form_book.save()
            for ident_form in forms_ident:
                if ident_form.is_valid():
                    ident = ident_form.save(commit=False)
                    ident.book=book
                    ident.save()
                    return redirect('book_list')
                else:
                    context = {
                        'form_book': form_book,
                        'forms_ident': forms_ident
                    }
                    return render(request, 'book_details', context)

        else:
            context = {'form_book': form_book, 'forms_ident': forms_ident}
            return render(request, 'book_details', context)


class BookFormView(View):
    def get(self, request):
        form_book = BookForm()
        form_ident = IdentifierForm()
        return render(
            request,
            'add_book.html',
            {'form_book': form_book, 'form_ident': form_ident}
        )

    def post(self, request):
        form_book = BookForm(request.POST)
        form_ident = IdentifierForm(request.POST)

        if form_book.is_valid():
            new_book = form_book.save()
            if form_ident.is_valid():
                ident = form_ident.save(commit=False)
                ident.book=new_book
                ident.save()

                return redirect('book_list')
        else:
            return render(
                request,
                'add_book.html',
                {'form_book': form_book, 'form_ident': form_ident}
            )


class BookDelete(View):
    def post(self, request, id):
        book = Book.objects.get(id=id)
        if book:
            book.delete()
            return HttpResponseRedirect(reverse('book_list'))
        else:
          return HttpResponseNotFound('<h1>Book not found</h1>')
