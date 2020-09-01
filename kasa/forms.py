from dal import autocomplete
from django import forms
from django.contrib.auth.forms import (ReadOnlyPasswordHashField,
                                       UserCreationForm)
from django.forms import Select, inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import (Artikl, Kupac, NaplatniUredaj, Poslovnica, Racun,
                     StavkaRacuna, Tvrtka, Zaposlenik)


class ZaposlenikCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_('Lozinka'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Potvrda lozinke'), widget=forms.PasswordInput)

    class Meta:
        model = Zaposlenik
        fields = ('username', 'first_name', 'last_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ZaposlenikChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Zaposlenik
        fields = ('username', 'first_name', 'last_name', 'oib', 'tvrtka',
                  'password', 'is_active', 'is_admin', 'is_staff')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class RacunForm(forms.ModelForm):
    class Meta:
        model = Racun
        fields = ['nacin_placanja', 'kupac']
        widgets = {
            'kupac': autocomplete.ModelSelect2(url='kupac-autocomplete',
                                               attrs={
                                                   'data-placeholder': 'Odaberi kupca'
                                               },)
        }


class StavkaRacunaForm(forms.ModelForm):
    # jedinica = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}),required=False)

    class Meta:
        model = StavkaRacuna
        fields = ['artikl','kolicina']

        widgets = {
            # 'artikl': Select(attrs={'class': 'form-control'}),
            # 'kolicina': Select(attrs={'class': 'form-control'})
            'artikl': autocomplete.ModelSelect2(url='artikl-autocomplete',
                                                attrs={
                                                    'data-placeholder': 'Odaberi artikl'
                                                },)
        }



class StavkaRacunaFormSet(inlineformset_factory(Racun, StavkaRacuna, form=StavkaRacunaForm, extra=1)):
    pass


class ZaposlenikCreateForm(UserCreationForm):
    class Meta:
        model = Zaposlenik
        fields = ['username', 'first_name', 'last_name', 'email', 'oib', 'is_staff']


class ZaposlenikUpdateForm(forms.ModelForm):
    class Meta:
        model = Zaposlenik
        fields = ['is_staff']


class PoslovnicaForm(forms.ModelForm):
    class Meta:
        model = Poslovnica
        fields = ['naziv', 'mjesto', 'adresa', 'telefon']


class ArtiklForm(forms.ModelForm):
    class Meta:
        model = Artikl
        fields = ['naziv', 'maloprodajna_cijena', 'pdv', 'pnp', 'jedinica']


class NaplatniUredajForm(forms.ModelForm):
    class Meta:
        model = NaplatniUredaj
        fields = ['zaposlenici', 'poslovnica']


class KupacForm(forms.ModelForm):
    class Meta:
        model = Kupac
        fields = ['naziv', 'adresa', 'oib', 'napomena']


class TvrtkaForm(forms.ModelForm):
    class Meta:
        model = Tvrtka
        fields = ['naziv', 'mjesto', 'adresa', 'oib', 'iban', 'u_sustavu_pdv', 'telefon', 'certifikat',
                  'certifikat_lozinka']


class TvrtkaRegistracijaForm(forms.ModelForm):
    class Meta:
        model = Tvrtka
        fields = ['naziv', 'mjesto', 'adresa', 'oib']


class PrometForm(forms.Form):
    zaposlenik = forms.CharField(required=False, widget=autocomplete.Select2(url='operater-autocomplete',
                                                attrs={
                                                    'data-placeholder': 'Odaberi zaposlenika'
                                                }, ))

    kupac = forms.CharField(required=False, widget=autocomplete.Select2(url='kupac-autocomplete',
                                                attrs={
                                                    'data-placeholder': 'Odaberi kupca'
                                                }, ))

    uredaj = forms.CharField(required=False, widget=autocomplete.Select2(url='uredaj-autocomplete',
                                                attrs={
                                                    'data-placeholder': 'Odaberi uredaj'
                                                }, ))

    poslovnica = forms.CharField(required=False, widget=autocomplete.Select2(url='poslovnica-autocomplete',
                                                                         attrs={
                                                                             'data-placeholder': 'Odaberi poslovnicu'
                                                                         }, ))

    datum_od = forms.DateTimeField(required=False, widget=forms.SelectDateWidget)

    datum_do = forms.DateTimeField(required=False, widget=forms.SelectDateWidget)
