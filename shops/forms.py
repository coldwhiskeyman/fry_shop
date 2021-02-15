from django import forms
from django.utils.translation import gettext_lazy as _


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(label=_('Количество'), min_value=1)
