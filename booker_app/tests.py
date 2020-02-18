import datetime
from django.test import TestCase
from django.urls import reverse
from booker_app.models import Book, Identifier


class TestBookModel(TestCase):

    def setUp(self):
        self.book = Book(
            authors='John Doe',
            title='Life of John',
            pub_date='1990-10-20',
            page_count=9,
            language='en',
            cover_image_adress="http://books.google.com/books/content?id=-qTbb7djcOoC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api"
        )
        self.book.save()

    def test_identifier_display_multiple_idents(self):
        """
        Property identifier_display() returns array with
        identifiers of a book.
        """
        Identifier(value='9788307018867', type='ISBN_13', book=self.book).save()
        Identifier(value='1234567891', type='ISBN_10', book=self.book).save()
        result = self.book.identifier_display
        expected = ['ISBN_13: 9788307018867', 'ISBN_10: 1234567891']

        self.assertEqual(len(result), len(expected))
        for ident in expected:
            assert ident in result

    def test_identifier_display_one_ident(self):
        Identifier(value='1234567890', type='ISBN_13', book=self.book).save()

        result = self.book.identifier_display
        expected = ['ISBN_13: 1234567890']

        self.assertEqual(len(result), len(expected))
        self.assertEqual(result, expected)

    def test_identifier_display_no_idents(self):
        result = self.book.identifier_display
        expected = []

        self.assertEqual(len(result), len(expected))


class TestIdentifierModel(TestCase):

    def setUp(self):
        self.book = Book(
            authors='John Doe',
            title='Life of John',
            pub_date='1990-10-20',
            page_count=9,
            language='en',
            cover_image_adress="http://books.google.com/books/content?id=-qTbb7djcOoC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api"
        )
        self.book.save()

    def test_save_identifier_ok(self):
        ident = Identifier(value='9992', type='OTHER', book=self.book)
        ident.save()

        # Save rises an exception if we have a duplicate identifier, so if we
        # get here all is good
        self.assertTrue(True)

    def test_save_identifier_duplicate_type_fails(self):
        ident = Identifier(value='9992', type='ISBN_10', book=self.book)
        ident_2 = Identifier(value='9993', type='ISBN_10', book=self.book)

        ident.save()
        with self.assertRaises(ValueError):
            ident_2.save()

    def test_update_existing_identifier_ok(self):
        ident = Identifier(value='9992', type='ISBN_10', book=self.book)

        ident.save()
        ident.value = '9999'
        ident.save()

        # No exception raised
        self.assertEqual(ident.value, '9999')
        self.assertEqual(len(Identifier.objects.all()), 1)


# Function to populate Book and Identifier model in view tests.
def create_book_with_ident(
        authors,
        title,
        pub_date,
        page_count,
        language,
        cover_image_adress,
        ident_type,
        ident_value):
    book = Book(
        authors=authors,
        title=title,
        pub_date=pub_date,
        page_count=page_count,
        language=language,
        cover_image_adress=cover_image_adress
    )
    book.save()
    identifier = Identifier(
        type=ident_type,
        value=ident_value,
        book=book
    )
    identifier.save()
    return book, identifier

class TestBookListView(TestCase):
    def test_no_books(self):
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Any book wasn't added yet.")
        self.assertQuerysetEqual(response.context['book_list'], [])

    def test_one_book(self):
        book, ident = create_book_with_ident(
            'a',
            'a',
            '1990-01-01',
            1,
            'a',
            'a',
            'ISSN',
            '5454'
        )
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['book_list'].first(), book)

    def test_multiple_books(self):
        book, ident = create_book_with_ident(
            'foo', 'foo', '1990-01-01', 1, 'bar', 'bar', 'ISSN', '5454'
        )
        book_2, ident_2 = create_book_with_ident(
            'foo', 'foo', '1990-01-01', 1, 'foo', 'foo', 'ISBN_10', '5450'
        )
        book_3, ident_3 = create_book_with_ident(
            'foo', 'foo', '1990-01-01', 1, 'foo', 'foo', 'ISBN_13', '5451'
        )
        list_of_books = Book.objects.all()
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['book_list']), 3)
        for book in response.context['book_list']:
            assert(book in list_of_books)


class TestBookDetailsView(TestCase):

    def test_no_book(self):
        with self.assertRaises(Book.DoesNotExist):
            url = reverse('book_details', kwargs={'book_id': 1})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

    def test_book_details_get(self):
        book, ident = create_book_with_ident(
            'a',
            'a',
            '1990-01-01',
            1,
            'a',
            'a',
            'ISSN',
            '5454'
            )
        url = reverse('book_details', kwargs={'book_id': 1})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form_book']['authors'].value(), 'a')
        self.assertEqual(
            response.context['form_book']['title'].value(), 'a')
        self.assertEqual(
            response.context['form_book']['pub_date'].value(), datetime.date(1990, 1, 1))
        self.assertEqual(
            response.context['form_book']['page_count'].value(), 1)
        self.assertEqual(
            response.context['form_book']['cover_image_adress'].value(), 'a')
        self.assertEqual(
            response.context['forms_ident'][0]['type'].value(), 'ISSN')
        self.assertEqual(
            response.context['forms_ident'][0]['value'].value(), '5454')

    def test_book_edit_post_ok(self):
        book, ident = create_book_with_ident(
            'foo',
            'foo',
            '1990-01-01',
            1,
            'pl',
            'foo',
            ident_type='ISSN',
            ident_value='1337'
        )
        url = reverse('book_details', kwargs={'book_id': book.id})
        data = {
            'authors':'bar',
            'title':'bar',
            'pub_date':'2010-10-10',
            'language': 'en',
            'page_count': 42,
            'type': 'ISBN_10',
            'value': '5454'
        }
        response = self.client.post(url, data)
        book_edited = Book.objects.first()

        self.assertEqual(book_edited.authors, data['authors'])

    def test_book_edit_no_book_post(self):
        with self.assertRaises(Book.DoesNotExist):
            url = reverse('book_details', kwargs={'book_id': 1})
            data = {
                'authors':'bar',
                'title':'bar',
                'pub_date':'2010-10-10',
                'language': 'en',
                'page_count': 42,
                'type': 'ISBN_10',
                'value': '5454'
            }
            response = self.client.post(url, data)

            self.assertEqual(book_edited.authors, data['authors'])


class TestBookFormView(TestCase):
    def test_add_book_ok(self):
        data = {
            'authors':'a',
            'title':'b',
            'pub_date':'2010-10-10',
            'language': 'pl',
            'page_count':4,
            'type': 'ISBN_10'
        }
        response = self.client.post(reverse('add_book'), data)
        added_book = Book.objects.first()
        added_ident = Identifier.objects.first()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(added_book.authors, 'a')
        self.assertEqual(added_book.title, 'b'),
        self.assertEqual(added_book.pub_date, datetime.date(2010, 10, 10)),
        self.assertEqual(added_book.language, 'pl'),
        self.assertEqual(added_book.page_count, 4),
        self.assertEqual(added_ident.type, 'ISBN_10')

    def test_add_book_invalid_indent_type(self):
        with self.assertRaises(ValueError):
            data = {
                'authors':'foo',
                'title':'foo',
                'pub_date':'2010-10-10',
                'language': 'pl',
                'page_count':4,
                'type': 'ISNB_15',
                'value': '1000000'
            }
            response = self.client.post(reverse('add_book'), data)
            self.assertEqual(response.status_code, 400)


class TestBookDeleteView(TestCase):
    def test_delete_book(self):
        book, ident = create_book_with_ident(
            'foo',
            'foo',
            '1990-01-01',
            1,
            'pl',
            'foo',
            ident_type='ISSN',
            ident_value='0009'
        )
        url = f'/booker_app/book_details/{book.id}/delete_book/'
        response = self.client.post(url)
        b = Book.objects.all()

        self.assertEqual(len(b), 0)
