from django import forms

from .models import BlockList


class BlockListForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={"style": "resize: vertical"}))

    class Meta:
        model = BlockList
        fields = ["name", "description", "country"]
