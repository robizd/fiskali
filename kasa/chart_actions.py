from django.db.models import Sum
from django.http import JsonResponse

from kasa.utils import current_year, current_month, current_day
from kasa.models import Racun


def getSatiChartData(user):
    sati_promet = list(Racun.objects.filter(operater=user,
                                              vrijeme_izdavanja__year=current_year(),
                                              vrijeme_izdavanja__month=current_month(),
                                              vrijeme_izdavanja__day=current_day())
                          .values('vrijeme_izdavanja__hour').annotate(Sum('ukupni_iznos'))
                          .order_by('vrijeme_izdavanja__hour'))

    return JsonResponse(sati_promet, safe=False)


def getDnevniChartData(user):
    sati_promet = list(Racun.objects.filter(operater=user,
                                            vrijeme_izdavanja__year=current_year(),
                                            vrijeme_izdavanja__month=current_month())
                       .values('vrijeme_izdavanja__day').annotate(Sum('ukupni_iznos'))
                       .order_by('vrijeme_izdavanja__day'))

    return JsonResponse(sati_promet, safe=False)


def getMjesecniChartData(user):
    mjeseci_promet = list(Racun.objects.filter(operater=user, vrijeme_izdavanja__year=current_year())
                          .values('vrijeme_izdavanja__month').annotate(Sum('ukupni_iznos'))
                          .order_by('vrijeme_izdavanja__month'))

    return JsonResponse(mjeseci_promet, safe=False)


def getGodisnjiChartData(user):
    godisnji_promet = list(Racun.objects.filter(operater=user)
                          .values('vrijeme_izdavanja__year').annotate(Sum('ukupni_iznos'))
                          .order_by('vrijeme_izdavanja__year'))

    return JsonResponse(godisnji_promet, safe=False)
