from django import forms
from django.core.exceptions import ValidationError

from booker_app.models import Book, Identifier
from booker.settings import MAX_STR_LEN


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'authors',
            'title',
            'pub_date',
            'language',
            'page_count',
            'cover_image_adress'
        ]


class IdentifierForm(forms.ModelForm):
    class Meta:
        model = Identifier
        fields = ['type', 'value']


class SearchBookForm(forms.Form):
    search_field = forms.CharField(max_length=100, label='Search')
    json = forms.BooleanField(required=False,initial=False,label='Show results in json')


class ImportBookForm(forms.Form):
    # Special keywords user can specify in the search terms to search
    # in particular fields. I chose only these field which can be saved in db.
    SEARCH_KEYWORDS = [
        ('inauthor', 'author'),
        ('intitle', 'title'),
        ('isbn', 'isbn'),
        ('lccn', 'lccn'),
        ('oclc', 'oclc')
    ]
    search_authors = forms.CharField(max_length=100, label='Search in authors', required=False)
    search_title = forms.CharField(max_length=100, label='Search in title', required=False)
    search_isbn = forms.CharField(max_length=100, label='Search in isbn', required=False)
    search_lccn = forms.CharField(max_length=100, label='Search in lccn', required=False)
    search_oclc = forms.CharField(max_length=100, label='Search in oclc', required=False)

    def clean(self):
        cleaned = self.cleaned_data
        counter = 0
        search_authors = cleaned.get("search_authors")
        search_title = cleaned.get("search_title")
        search_isbn = cleaned.get("search_isbn")
        search_lccn = cleaned.get("search_lccn")
        search_oclc = cleaned.get("search_oclc")
        keywords_fields = [
            search_authors,
            search_title,
            search_isbn,
            search_lccn,
            search_oclc
        ]
        for keyword in keywords_fields:
            if keyword:
                counter += 1
        if counter < 1:
            # Error raises if no field was filled in
            raise ValidationError("Fill in at least one field to import books")

        return cleaned
