from django import forms

from .models import ShortURL
import string
import random


def generateShort(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


class URLSnipForm(forms.ModelForm):
    # alias = forms.CharField(max_length=25)
    # url=forms.URLField()
    # name=forms.CharField(max_length=100)
    class Meta:
        model = ShortURL
        fields = ['alias', 'url', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alias'].required = False
        self.fields['name'].required = False
        self.fields['alias'].widget.attrs = {"placeholder": "Alias (Optional)"}
        self.fields['url'].widget.attrs = {"placeholder": "URL"}
        self.fields['name'].widget.attrs = {"placeholder": "Name (Optional)"}

    def is_valid(self) -> bool:
        if self.instance.alias and len(self.instance.alias) < 6:
            self.add_error('alias', 'Alias must be at least 6 characters')
            return False
        if self.instance.alias and self.instance.alias.lower() in ['allurls','admin','urlsnip']:
            self.add_error('alias', 'Alias is reserved')
            return False
        return super().is_valid()
