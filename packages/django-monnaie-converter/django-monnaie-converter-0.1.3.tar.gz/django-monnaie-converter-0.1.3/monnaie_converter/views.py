from django.shortcuts import render
from .forms import CurrencyForm

# Taux de conversion (exemple statique)
CONVERSION_RATES = {
    ('USD', 'EUR'): 0.85,
    ('EUR', 'USD'): 1.18,
    ('XOF', 'EUR'): 0.0015,
    ('EUR', 'XOF'): 655.957,
    ('USD', 'XOF'): 655.957 * 0.85,  # ~557.56
    ('XOF', 'USD'): 1 / (655.957 * 0.85),  # ~0.00179
}

def convert_currency(request):
    result = None
    if request.method == "POST":
        form = CurrencyForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            from_currency = form.cleaned_data['from_currency']
            to_currency = form.cleaned_data['to_currency']

            if from_currency == to_currency:
                result = amount  # Pas besoin de conversion
            else:
                rate = CONVERSION_RATES.get((from_currency, to_currency))
                if rate:
                    result = round(amount * rate, 2)
                else:
                    result = "Conversion non disponible pour ces devises"
    else:
        form = CurrencyForm()

    return render(request, 'monnaie_converter/converter.html', {
        'form': form,
        'result': result
    })