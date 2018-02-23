from django import forms

from .models import BlockList


class BlockListForm(forms.ModelForm):
    class Meta:
        model = BlockList
        fields = ["name", "description", "country"]
