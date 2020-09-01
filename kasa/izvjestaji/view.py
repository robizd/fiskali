from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View
from django.http import JsonResponse

from kasa.filters import RacuniFilter
from kasa.models import Racun, Artikl, Kupac, Poslovnica


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class IzvjestajiRacunView(ListView):
    model = Racun
    paginate_by = 10
    template_name = "kasa/izvjestaji/izvjestaji_racun.html"

    def get_queryset(self, **kwargs):
        queryset = Racun.objects.filter(naplatni_uredaj__poslovnica__tvrtka=self.request.user.tvrtka).select_related(
            'operater').order_by('-vrijeme_izdavanja')

        self.filter = RacuniFilter(self.request.GET, queryset=queryset)

        self.is_filtered = False
        for k, v in self.request.GET.items():
            if v:
                self.is_filtered = True

            if len(self.request.GET) == 1 and k == 'page':
                self.is_filtered = False

        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super(IzvjestajiRacunView, self).get_context_data(**kwargs)
        context['filters'] = self.filter
        context['is_filtered'] = self.is_filtered
        return context


def artikliSelect2(request):

    if 'term' in request.GET:
        search_term = request.GET['term']
        artikli_list = list(Artikl.objects.filter(tvrtka=request.user.tvrtka, naziv__icontains=search_term).values())
    else:
        artikli_list = list(Artikl.objects.filter(tvrtka=request.user.tvrtka).values())


    select2_result = [{'id': i['id'], 'text': i['naziv']} for i in artikli_list]
    more = {'more': True}

    result = {'results': select2_result, 'pagination': more}

    return JsonResponse(result, safe=False)


def kupacSelect2(request):
    if 'term' in request.GET:
        search_term = request.GET['term']
        kupac_list = list(Kupac.objects.filter(tvrtka=request.user.tvrtka, naziv__icontains=search_term).values())
    else:
        kupac_list = list(Kupac.objects.filter(tvrtka=request.user.tvrtka).values())

    select2_result = [{'id': i['id'], 'text': i['naziv']} for i in kupac_list]
    more = {'more': True}

    result = {'results': select2_result, 'pagination': more}

    return JsonResponse(result, safe=False)


def poslovnicaSelect2(request):
    if 'term' in request.GET:
        search_term = request.GET['term']
        poslovnica_list = list(Poslovnica.objects.filter(tvrtka=request.user.tvrtka, naziv__icontains=search_term).values())
    else:
        poslovnica_list = list(Poslovnica.objects.filter(tvrtka=request.user.tvrtka).values())

    select2_result = [{'id': i['id'], 'text': i['naziv']} for i in poslovnica_list]
    more = {'more': True}

    result = {'results': select2_result, 'pagination': more}

    return JsonResponse(result, safe=False)


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class IzvjestajiPrometView(View):

    template_name = "kasa/izvjestaji/izvjestaji_promet.html"

    def post(self, request):
        request.POST.get("artikl", "")
        print(request.POST.get("artikl"))
        pass


    def get(self, request):
        return render(request, self.template_name)
