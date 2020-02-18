from django import forms

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
    search_field = forms.CharField(label='search_field', max_length=100)
