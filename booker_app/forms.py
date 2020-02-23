from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError

from booker_app.models import Book, Identifier
from booker.settings import MAX_STR_LEN


class BookForm(forms.Form):
    authors = forms.CharField(
        max_length=MAX_STR_LEN,
        label='Authors',
        widget=forms.TextInput(
                 attrs={'size':'30', 'class':'inputText'}
        )
    )
    title = forms.CharField(
        max_length=MAX_STR_LEN,
        label='Title',
        widget=forms.TextInput(
                 attrs={'size':'30', 'class':'inputText'}
        )
    )
    pub_date = forms.CharField(
        required=False,
        label='Publication date (YYYY-MM-DD)',
        widget=forms.TextInput(
                 attrs={'size':'30', 'class':'inputText'}
        )
    )
    page_count = forms.IntegerField(
        label='Page count',
        required=False,
        widget=forms.NumberInput(
                 attrs={'size':'30', 'class':'inputText'}
        )
    )
    language = forms.CharField(
        max_length=2,
        help_text='2 letters format, eg. "en", "pl"',
        label='Language',
        widget=forms.TextInput(
                 attrs={'size':'30', 'class':'inputText'}
        )
    )
    cover_image_adress = forms.URLField(
        max_length=MAX_STR_LEN,
        required=False,
        label='Cover image adress',
        widget=forms.TextInput(
                 attrs={'size':'30', 'class':'inputText'}
        )
    )

    def clean(self):
        cleaned = self.cleaned_data
        check_date_pub = cleaned.get('pub_date')
        if len(check_date_pub) < 1:
            check_date_pub = None
        elif len(check_date_pub) == 4:
            check_date_pub += '-01-01'
            check_date_pub = datetime.strptime(check_date_pub, '%Y-%m-%d')
        elif len(check_date_pub) > 4 and len(check_date_pub) < 8:
            check_date_pub += '-01'
            check_date_pub = datetime.strptime(check_date_pub, '%Y-%m-%d')

        cleaned = {
            'authors': cleaned.get('authors'),
            'title': cleaned.get('title'),
            'pub_date': check_date_pub,
            'page_count': cleaned.get('page_count'),
            'language': cleaned.get('language'),
            'cover_image_adress': cleaned.get('cover_image_adress')
        }
        return cleaned


class BookFormEdit(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BookFormEdit, self).__init__(*args, **kwargs)
        self.fields['authors'].widget.attrs['size'] = 30
        self.fields['title'].widget.attrs['size'] = 30
        self.fields['pub_date'].widget.attrs['size'] = 30
        self.fields['language'].widget.attrs['size'] = 30
        self.fields['page_count'].widget.attrs['size'] = 30
        self.fields['cover_image_adress'].widget.attrs['size'] = 30

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


class IdentifierForm(forms.Form):
    ISBN_10 = forms.CharField(
        max_length=MAX_STR_LEN,
        required=False,
        widget=forms.TextInput(
            attrs={'size':'30', 'class':'inputText'}
        )
    )
    ISBN_13 = forms.CharField(
        max_length=MAX_STR_LEN,
        required=False,
        widget=forms.TextInput(
            attrs={'size':'30', 'class':'inputText'}
        )
    )
    ISSN = forms.CharField(
        max_length=MAX_STR_LEN,
        required=False,
        widget=forms.TextInput(
            attrs={'size':'30', 'class':'inputText'}
        )
    )
    OTHER = forms.CharField(
        max_length=MAX_STR_LEN,
        required=False,
        widget=forms.TextInput(
            attrs={'size':'30', 'class':'inputText'}
        )
    )


class SearchBookForm(forms.Form):
    search_field = forms.CharField(max_length=MAX_STR_LEN, label='Search')


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
    search_authors = forms.CharField(
        max_length=MAX_STR_LEN, label='Search in authors', required=False)
    search_title = forms.CharField(
        max_length=MAX_STR_LEN, label='Search in title', required=False)
    search_isbn = forms.CharField(
        max_length=MAX_STR_LEN, label='Search in isbn', required=False)
    search_lccn = forms.CharField(
        max_length=MAX_STR_LEN, label='Search in lccn', required=False)
    search_oclc = forms.CharField(
        max_length=MAX_STR_LEN, label='Search in oclc', required=False)

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
