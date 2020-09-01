import django_filters

from .models import Racun


class RacuniFilter(django_filters.FilterSet):
    oznaka = django_filters.CharFilter(lookup_expr='icontains')
    vrijeme_izdavanja_between = django_filters.DateFromToRangeFilter(field_name='vrijeme_izdavanja',
                                                                     label='Date (Between)')
    naziv_kupca = django_filters.CharFilter(lookup_expr='icontains')
    ukupni_iznos = django_filters.RangeFilter(lookup_expr='range')
    naziv_operatera = django_filters.CharFilter(lookup_expr='icontains')
    naplatni_uredaj = django_filters.NumberFilter(lookup_expr='exact')

    class Meta:
        model = Racun
        fields = {

        }

class RacuniIzvjestaj(django_filters.FilterSet):
   pass
