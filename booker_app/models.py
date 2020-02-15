from django.db import models

from booker.settings import MAX_STR_LEN


class Book(models.Model):
    """Book model with basic book fields according to Google Books:

    Attributes:
        authors: one ore more authors. String
        title: String.
        pub_date: Date of publication. Date.
        page_count: Page count. Integer.
        language: Language in which a book was published. Max_len=2
            according to ISO 639-1 code used in Google Book API.
        cover_image: A link to cover image.
    """
    authors = models.CharField(max_length=MAX_STR_LEN)
    title = models.CharField(max_length=MAX_STR_LEN)
    pub_date = models.DateField('date published')
    page_count = models.IntegerField()
    language = models.CharField(max_length=2)
    cover_image = models.CharField(max_length=MAX_STR_LEN)


class Identifier(models.Model):
    """Identifier field for the Book class was moved to a new class because
    identifier can have one of four types according to Google Books API
    (https://developers.google.com/resources/api-libraries/documentation/books/v1/java/latest/com/google/api/services/books/model/Volume.VolumeInfo.IndustryIdentifiers.html)
    Attributes:
        value: value of a book identifier. String
        type: one of four to choice from IDENTIFIER_TYPES. String.
        book: book object which the identifier belongs to. ForeignKey.
    """
    IDENTIFIER_TYPES = [
        ('ISBN_10', 'ISBN_10'),
        ('ISBN_13', 'ISBN_13'),
        ('ISSN', 'ISSN'),
        ('OTHER', 'OTHER')
    ]
    value = models.CharField(max_length=MAX_STR_LEN)
    type = models.CharField(
        max_length=7,
        choices=IDENTIFIER_TYPES
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
