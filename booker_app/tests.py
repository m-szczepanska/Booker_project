from django.test import TestCase
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
