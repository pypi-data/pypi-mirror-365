from django import forms

class CurrencyForm(forms.Form):
    CURRENCY_CHOICES = [
        ('USD', 'USD - Dollar américain'),
        ('EUR', 'EUR - Euro'),
        ('XOF', 'XOF - Franc CFA'),
    ]

    amount = forms.FloatField(label="Montant", min_value=0)

    from_currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        label="De",
        widget=forms.Select(attrs={'class': 'select-field'})
    )

    to_currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        label="Vers",
        widget=forms.Select(attrs={'class': 'select-field'})
    )
