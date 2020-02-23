import json
import requests
from datetime import datetime

from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.http import (
    HttpResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
)
from django.urls import reverse_lazy
from django.views import View

from booker_app.forms import (BookForm, IdentifierForm, SearchBookForm,
    ImportBookForm, BookFormEdit
)
from booker_app.models import Book, Identifier


class BookView(View):
    def get(self, request):
        book_list = Book.objects.all()
        form = SearchBookForm()
        context = {'book_list': book_list, 'form': form}
        return render(request, 'book_list.html', context)

    def post(self, request, *args, **kwargs):
        form = SearchBookForm(request.POST)
        if not form.is_valid():  # TODO fix redirect
            return redirect('book_list')
        search_phrase = form.cleaned_data['search_field']
        search_result = Book.objects.filter(
            Q(authors__icontains=search_phrase) |
            Q(title__icontains=search_phrase) |
            Q(language__icontains=search_phrase) |
            Q(pub_date__icontains=search_phrase)
        )

        context = {'book_list': search_result}
        return render(request, 'book_list.html', context)


class BookListJsonView(View):
    def get(self, request):
        """Search keyword should be passed through the URL as a querystring
        in the following format:
        ?authors=[AUTHORS]&title=[TITLE]&language=[LANGUAGE]&pub_date=[YYYY-MM-DD]
        """
        authors = request.GET.get('authors', '')
        title = request.GET.get('title', '')
        language = request.GET.get('language', '')
        pub_date = request.GET.get('pub_date', '')
        search_result = list(Book.objects.filter(
            authors__icontains=authors,
            title__icontains=title,
            language__icontains=language,
            pub_date__icontains=pub_date
        ).values())

        return JsonResponse(search_result, safe=False)


class BookDetailsView(View):
    def get(self, request, book_id):
        book = Book.objects.get(id=book_id)
        if not book:
            not_found_msg = 'Book not found'
            return render(request, 'book_details.html', not_found_msg)
        form_book = BookFormEdit(
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
        initial_values = {
            ident.type: ident.value for ident in identifiers}
        form_ident = IdentifierForm(initial=initial_values)

        context = {'form_book': form_book, 'form_ident': form_ident}
        return render(request, 'book_details.html', context)

    def post(self, request, book_id):
        book = Book.objects.get(id=book_id)
        if not book:
            not_found_msg = 'Book not found'
            return render(
                request,
                'book_details.html',
                {'not_found_msg':not_found_msg}
            )

        form_book = BookFormEdit(
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
        ident_types_in_book = [ident.type for ident in identifiers]
        form_ident = IdentifierForm(request.POST)

        if form_book.is_valid():
            form_book.save(commit=False)

            if form_ident.is_valid():
                for ident_type in Identifier.IDENTIFIER_TYPES:
                    ident_type = ident_type[0]  # Pick a value from the tuple
                    if form_ident.cleaned_data[ident_type]:
                        # check if ident value exists in other book.
                        ident_exist_in_other_book = Identifier.objects.filter(
                            type=ident_type,
                            value=form_ident.cleaned_data[ident_type]
                        ).first()
                        if (ident_exist_in_other_book and
                            ident_exist_in_other_book.book_id != book.id):
                            error_msg = "Book with this identifier already exists."
                            return render(
                                request,
                                'book_list.html',
                                {'error_msg': error_msg}
                            )
                        form_book.save()
                        if ident_type in ident_types_in_book:
                            ident_to_update = Identifier.objects.filter(
                                book_id=book.id, type=ident_type
                            ).first()
                            ident_to_update.type=ident_type
                            ident_to_update.value=form_ident.cleaned_data[ident_type]
                            ident_to_update.book=book
                            ident_to_update.save()
                        else:
                            Identifier(
                            type=ident_type,
                            value=form_ident.cleaned_data[ident_value],
                            book=book
                            ).save()
                        success_msg = 'Book updated successfully'
                        context = {
                            'form_book': form_book,
                            'form_ident': form_ident,
                            'success_msg': success_msg
                        }
                        return render(request, 'book_details.html', context)
            else:
                error_msg = "Updating failed. Invalid indentifier."
                context = {'error_msg': error_msg}
                return render(request, 'book_details.html', context)

        else:
            success_msg = 'Book updated successfully'
            context = {
                'form_book': form_book,
                'form_ident': form_ident,
                'success_msg': success_msg
            }
            return render(request, 'book_details.html', context)


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

        book_exists = None
        ident_instances = []
        if form_ident.is_valid():
            for ident_type in Identifier.IDENTIFIER_TYPES:
                ident_type = ident_type[0]  # Pick a value from the tuple
                value = form_ident.cleaned_data[ident_type]
                if value:
                    ident = Identifier.objects.filter(
                        type=ident_type,
                        value=value
                    ).first()
                    if ident:
                        book_exists = True
                        error_msg = (
                            f'Book with {ident_type}: {value} already exists.'
                        )
                        break
                    else:
                        ident_instances.append(Identifier(
                            type=ident_type,
                            value=value
                        ))

        if book_exists:
            return render(
                request,
                'add_book.html',
                {
                    'form_book': form_book,
                    'form_ident': form_ident,
                    'error_msg': error_msg
                }
            )

        if form_book.is_valid():
            authors=form_book.cleaned_data['authors']
            title=form_book.cleaned_data['title']
            pub_date=form_book.cleaned_data['pub_date']
            page_count=form_book.cleaned_data['page_count']
            language=form_book.cleaned_data['language']
            cover_image_adress=form_book.cleaned_data['cover_image_adress']

            # If no idents exist we don't want to duplicate the book
            if not ident_instances and self.check_if_book_exists(
                authors,
                title,
                pub_date,
                page_count,
                language,
                cover_image_adress):

                error_msg = f'{title} by {authors} already exists.'
                return render(
                    request,
                    'add_book.html',
                    {
                        'form_book': form_book,
                        'form_ident': form_ident,
                        'msg': error_msg
                    }
                )

            new_book = Book(
                authors=form_book.cleaned_data['authors'],
                title=form_book.cleaned_data['title'],
                pub_date=form_book.cleaned_data['pub_date'],
                page_count=form_book.cleaned_data['page_count'],
                language=form_book.cleaned_data['language'],
                cover_image_adress=form_book.cleaned_data['cover_image_adress']
            )
            new_book.save()
            for ident in ident_instances:
                ident.book = new_book
                ident.save()

            return redirect('book_list')


    def check_if_book_exists(
        self,
        authors,
        title,
        pub_date,
        page_count,
        language,
        cover_image_adress):

        return Book.objects.filter(
            authors=authors,
            title=title,
            pub_date=pub_date,
            page_count=page_count,
            language=language,
            cover_image_adress=cover_image_adress
        ).first()


class BookDelete(View):
    def post(self, request, id):
        book = Book.objects.get(id=id)
        if book:
            idents = Identifier.objects.filter(book_id=book.id).all()
            for ident in idents:
                ident.delete()
            book.delete()
            return HttpResponseRedirect(reverse('book_list'))
        else:
          return HttpResponseRedirect(reverse('book_list'))


class ImportBookView(View):
    """https://www.googleapis.com/books/v1/volumes?q=search+terms"""
    def get(self, request):
        form = ImportBookForm()
        return render(request, 'import_book.html', {'form': form})

    def post(self, request, *args):
        form = ImportBookForm(request.POST)
        if form.is_valid():
            search_authors = form.cleaned_data['search_authors']
            search_title = form.cleaned_data['search_title']
            search_isbn = form.cleaned_data['search_isbn']
            search_lccn = form.cleaned_data['search_lccn']
            search_oclc = form.cleaned_data['search_oclc']
        else:
            error_msg = 'Fill in at least one field to import books.'
            context = {'error_msg': error_msg}
            return render(request, 'import_book.html', context)

        keywords_fields = {
            'inauthor': search_authors,
            'intitle': search_title,
            'isbn': search_isbn,
            'lccn': search_lccn,
            'oclc': search_oclc
        }

        volume_infos = self.call_google_api(keywords_fields)
        if not volume_infos:
            error_msg = 'No volumes found. Change your search terms.'
            return render(request, 'book_list.html', {'error_msg': error_msg})

        success_msg = ''
        for item in volume_infos:
            book_exists = None  # we don't know if a book exists in our db
            ident_instances = []  # to be saved after the book
            for ident in item.get('industryIdentifiers', []):
                type = ident['type']
                value = ident['identifier']
                identifier = Identifier.objects.filter(
                    type=type,
                    value=value
                ).first()
                # Hack to break out of outer loop
                if identifier:
                    book_exists = True
                    error_msg = (
                        f'Book with {type}: {value} already exists.'
                    )
                    break
                else:
                    # Idents that we will want to save, but need a book
                    # instance for the Foreign Key
                    ident_instances.append(Identifier(type=type, value=value))

            if book_exists:
                return render(request, 'book_list.html', {"error_msg": error_msg})

            # authors is a list; a book can sometimes miss authors as well.
            authors = ','.join(item.get('authors', []))
            title = item['title']
            pub_date = self.clean_date(item.get('publishedDate'))
            page_count = item.get('pageCount')  # optional
            language = item.get('language')
            cover_image_adress = item.get('imageLinks', {}).get('thumbnail')

            # If no idents exist we don't want to duplicate the book
            if not ident_instances and self.check_if_book_exists(
                authors,
                title,
                pub_date,
                page_count,
                language,
                cover_image_adress):

                continue

            book = Book(
                authors=authors,
                title=title,
                pub_date=pub_date,
                page_count=page_count,
                language=language,
                cover_image_adress=cover_image_adress
            )
            book.save()
            for ident in ident_instances:
                ident.book = book
                ident.save()

            success_msg += f'"{book.title}" imported to the database. '

        return render(
            request,
            'book_list.html',
            {'success_msg': success_msg},
            {'error_msg': error_msg}
        )

    def call_google_api(self, keywords_fields):
        valid_fields = [
            f'{key_field}:{keywords_fields[key_field]}' for key_field
            in keywords_fields.keys() if keywords_fields[key_field]
        ]
        url = 'https://www.googleapis.com/books/v1/volumes'
        params = {'q': f'{valid_field}' for valid_field in valid_fields}
        response_bytes = requests.get(url, params=params)
        response = response_bytes.content.decode("utf-8")
        # Check if user found any book. If not return None.
        response_check = json.loads(response)["totalItems"]
        if not response_check:
            return None

        response = json.loads(response)['items']
        return [item['volumeInfo'] for item in response]

    def clean_date(self, pub_date):
        # Hack for date_pub if only a year or a year and a month are
        # specified
        if len(pub_date) < 5:
            pub_date += '-01-01'
        elif len(pub_date) < 8:
            pub_date += '-01'
        return datetime.strptime(pub_date, '%Y-%m-%d')

    def check_if_book_exists(
        self,
        authors,
        title,
        pub_date,
        page_count,
        language,
        cover_image_adress):

        return Book.objects.filter(
            authors=authors,
            title=title,
            pub_date=pub_date,
            page_count=page_count,
            language=language,
            cover_image_adress=cover_image_adress
        ).first()
