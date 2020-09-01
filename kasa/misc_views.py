from dal import autocomplete

from kasa.models import Artikl, Kupac, Zaposlenik, NaplatniUredaj, Poslovnica


class KupacAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Kupac.objects.filter(tvrtka=self.request.user.tvrtka).order_by('id')

        if self.q:
            qs = qs.filter(naziv__istartswith=self.q)

        return qs


class ArtiklAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Artikl.objects.filter(tvrtka=self.request.user.tvrtka).order_by('id')

        if self.q:
            qs = qs.filter(naziv__istartswith=self.q)

        return qs


class OperaterAutocompleteVeiw(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Zaposlenik.objects.filter(tvrtka=self.request.user.tvrtka).order_by('id')

        if self.q:
            qs = qs.filter(naziv__istartswith=self.q)

        return qs


class UredajAutocompleteVeiw(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = NaplatniUredaj.objects.filter(poslovnica__tvrtka=self.request.user.tvrtka).order_by('id')

        if self.q:
            qs = qs.filter(naziv__istartswith=self.q)

        return qs


class PoslovnicaAutocompleteVeiw(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Poslovnica.objects.filter(tvrtka=self.request.user.tvrtka).order_by('id')

        if self.q:
            qs = qs.filter(naziv__istartswith=self.q)

        return qs

