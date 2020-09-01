import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import Max, Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, translate_url
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import LANGUAGE_SESSION_KEY, check_for_language
from django.utils.translation import gettext_lazy as _
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, UpdateView, View)

from kasa.actions import get_jir, get_zki
from kasa import chart_actions
from kasa.filters import RacuniFilter
from kasa.forms import (ArtiklForm, KupacForm, NaplatniUredajForm,
                        PoslovnicaForm, RacunForm, StavkaRacunaFormSet,
                        TvrtkaRegistracijaForm, ZaposlenikCreateForm,
                        ZaposlenikUpdateForm)
from kasa.mixins import NaplatniUredajOdabirMixin
from kasa.models import (Artikl, Kupac, NaplatniUredaj, Poslovnica, Racun,
                         RacunPorez, StavkaRacuna, Tvrtka, Zaposlenik)
from kasa.utils import current_year

from .tokens import account_activation_token


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
class NoviRacunCreateView(NaplatniUredajOdabirMixin, CreateView):
    template_name = 'kasa/racun/novi_racun.html'
    form_class = RacunForm

    def get_form(self, form_class=form_class):
        form = super().get_form(form_class)
        # form.fields['kupac'].queryset = Kupac.objects.filter(tvrtka=self.request.user.tvrtka).order_by('id')
        return form

    def get_success_url(self):
        return reverse('moji_racuni')

    def get_initial(self):
        initial = super().get_initial()
        kupac = self.request.user.tvrtka.kupac_set.get(id=1)
        initial['kupac'] = kupac
        return initial

    def get_context_data(self, **kwargs):
        data = super(NoviRacunCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['stavkeracuna'] = StavkaRacunaFormSet(self.request.POST)
        else:
            data['stavkeracuna'] = StavkaRacunaFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        stavkeracuna = context['stavkeracuna']

        pdv_osnovica_porez_ukupno = {}
        with transaction.atomic():
            form.instance.operater = self.request.user
            form.instance.naplatni_uredaj = NaplatniUredaj.objects.get(id=self.request.session['naplatniuredaj_id'],
                                                                       poslovnica__tvrtka=self.request.user.tvrtka)

            godina = str(current_year())
            broj_naplatnog_uredaja = str(form.instance.naplatni_uredaj.broj)
            oznaka_poslovnog_prostora = form.instance.naplatni_uredaj.poslovnica.oznaka

            # Broj računa
            racun = Racun.objects.filter(naplatni_uredaj=form.instance.naplatni_uredaj,
                                         godina=godina).aggregate(Max('broj'))

            if racun['broj__max'] is None:
                broj_racuna = 1
            else:
                broj_racuna = racun['broj__max'] + 1

            # Oznaka računa
            oznaka_racuna = str(broj_racuna) + '/' + oznaka_poslovnog_prostora + '/' + broj_naplatnog_uredaja

            form.instance.broj = broj_racuna
            form.instance.oznaka = oznaka_racuna
            form.instance.godina = godina

            self.object = form.save()

            if stavkeracuna.is_valid():
                stavkeracuna.instance = self.object
                stavkeracuna.save()

            # Iznosi računa, porezi i osnovice
            ukupni_iznos = 0
            rbr = 0
            for stavka in stavkeracuna:

                # Kad se prva inicijalna stavka izbrise, ostane kao delete=True
                if stavka.cleaned_data['DELETE'] == True:
                    continue

                # Rbr stavke
                rbr = rbr + 1
                stavka.instance.rbr = rbr
                stavka.save()

                iznos_stavke = stavka.instance.artikl.maloprodajna_cijena * stavka.instance.kolicina
                ukupni_iznos = ukupni_iznos + iznos_stavke

                key = stavka.instance.pdv_artikla

                if key in pdv_osnovica_porez_ukupno:
                    pdv_osnovica_porez_ukupno[key]['ukupno'] = pdv_osnovica_porez_ukupno[key]['ukupno'] + iznos_stavke
                else:
                    pdv_osnovica_porez_ukupno[key] = {}
                    pdv_osnovica_porez_ukupno[key]['ukupno'] = Decimal(iznos_stavke)

            self.object.ukupni_iznos = ukupni_iznos

            self.object.save()

            # Unos poreza, osnovice i iznosa poreza u RacunPorez
            ukupno_osnovica = 0
            ukupno_porez = 0
            for key in pdv_osnovica_porez_ukupno:
                pdv_osnovica_porez_ukupno[key]['osnovica'] = pdv_osnovica_porez_ukupno[key]['ukupno'] / \
                    Decimal((1 + key / 100))

                ukupno_osnovica = ukupno_osnovica + pdv_osnovica_porez_ukupno[key]['osnovica']

                pdv_osnovica_porez_ukupno[key]['porez'] = pdv_osnovica_porez_ukupno[key]['ukupno'] - \
                    pdv_osnovica_porez_ukupno[key]['osnovica']

                ukupno_porez = ukupno_porez + pdv_osnovica_porez_ukupno[key]['porez']

                racun_porez = RacunPorez(stopa_poreza=key,
                                         osnovica_poreza=pdv_osnovica_porez_ukupno[key]['osnovica'],
                                         iznos_poreza=pdv_osnovica_porez_ukupno[key]['porez'],
                                         ukupno=pdv_osnovica_porez_ukupno[key]['ukupno'],
                                         racun=self.object)
                racun_porez.save()

            self.object.ukupno_osnovica = ukupno_osnovica
            self.object.ukupno_porez = ukupno_porez

            self.object.save()

        # ZKI
        self.object.zki = get_zki(settings.MEDIA_ROOT + "/" + str(self.request.user.tvrtka.certifikat),
                                  self.request.user.tvrtka.certifikat_lozinka,
                                  self.request.user.tvrtka.oib,
                                  self.object.vrijeme_izdavanja,
                                  broj_racuna,
                                  oznaka_poslovnog_prostora,
                                  broj_naplatnog_uredaja,
                                  self.object.ukupni_iznos)
        self.object.save()

        # JIR
        jir = get_jir(settings.MEDIA_ROOT + "/" + str(self.request.user.tvrtka.certifikat),
                      self.request.user.tvrtka.certifikat_lozinka,
                      self.request.user.tvrtka.oib,
                      self.request.user.oib,
                      self.request.user.tvrtka.u_sustavu_pdv,
                      form.instance.nacin_placanja,
                      self.object.vrijeme_izdavanja,
                      broj_racuna,
                      oznaka_poslovnog_prostora,
                      broj_naplatnog_uredaja,
                      False,
                      self.object.ukupni_iznos,
                      pdv_osnovica_porez_ukupno)

        if jir['greska'] == 'N':
            self.object.jir = jir['jir']
        else:
            self.object.poruka_porezna = jir['greska_text']

        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
class MojiRacuniListView(ListView):
    model = Racun
    paginate_by = 10
    template_name = 'kasa/racun/moji_racuni.html'

    def get_queryset(self, **kwargs):
        queryset = Racun.objects.filter(operater=self.request.user).select_related(
            'naplatni_uredaj').order_by('-vrijeme_izdavanja')

        self.filter = RacuniFilter(self.request.GET, queryset=queryset)

        self.is_filtered = False
        for k, v in self.request.GET.items():
            if v:
                self.is_filtered = True

            if len(self.request.GET) == 1 and k == 'page':
                self.is_filtered = False

        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super(MojiRacuniListView, self).get_context_data(**kwargs)
        context['filters'] = self.filter
        context['is_filtered'] = self.is_filtered
        return context


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class RacuniListView(ListView):
    model = Racun
    paginate_by = 10
    template_name = "kasa/racun/racun_list.html"

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
        context = super(RacuniListView, self).get_context_data(**kwargs)
        context['filters'] = self.filter
        context['is_filtered'] = self.is_filtered
        return context


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
class RacunDetailView(TemplateView):
    template_name = "kasa/racun/racun_detalji.html"

    def get_context_data(self, **kwargs):
        context = super(RacunDetailView, self).get_context_data(**kwargs)
        context['racun'] = Racun.objects.get(id=self.kwargs['pk'],
                                             naplatni_uredaj__poslovnica__tvrtka=self.request.user.tvrtka)

        context['racun_porezi'] = RacunPorez.objects.filter(racun__id=self.kwargs['pk'])

        context['stavke_racuna'] = StavkaRacuna.objects.filter(racun__id=self.kwargs['pk'])

        return context


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class TvrtkaView(DetailView):
    model = Tvrtka
    template_name = 'kasa/tvrtka/tvrtka_detalji.html'

    def get_queryset(self):
        query_set = Tvrtka.objects.filter(id=self.request.user.tvrtka.id)
        return query_set


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class TvrtkaUpdateView(UpdateView):
    model = Tvrtka
    fields = ['iban', 'u_sustavu_pdv', 'telefon', 'certifikat',
              'certifikat_lozinka']
    template_name = 'kasa/tvrtka/tvrtka_uredi.html'

    def get_queryset(self):
        query_set = Tvrtka.objects.filter(id=self.request.user.tvrtka.id)
        return query_set

    def get_success_url(self):
        return reverse('tvrtka', kwargs={'pk': self.request.user.tvrtka.id})


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ZaposlenikListView(ListView):
    model = Zaposlenik
    paginate_by = 10
    template_name = 'kasa/zaposlenik/zaposlenik_list.html'

    def get_queryset(self):
        query_set = Zaposlenik.objects.filter(tvrtka=self.request.user.tvrtka, is_active=True)
        return query_set


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ZaposlenikCreateView(CreateView):
    form_class = ZaposlenikCreateForm
    template_name = 'kasa/zaposlenik/zaposlenik_dodaj.html'

    def get_success_url(self):
        return reverse('zaposlenici')

    def form_valid(self, form):
        form.instance.tvrtka = self.request.user.tvrtka
        return super().form_valid(form)


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ZaposlenikUpdateView(UpdateView):
    form_class = ZaposlenikUpdateForm
    template_name = 'kasa/zaposlenik/zaposlenik_uredi.html'

    def get_queryset(self):
        query_set = Zaposlenik.objects.filter(id=self.kwargs['pk'], tvrtka=self.request.user.tvrtka)
        return query_set

    def get_success_url(self):
        return reverse('zaposlenici')


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ZaposlenikDeleteView(View):

    def get(self, request, *args, **kwargs):

        Zaposlenik.objects.filter(id=self.kwargs['pk'],
                                  tvrtka=self.request.user.tvrtka).update(is_active=False)

        return HttpResponseRedirect(reverse('zaposlenici'))


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ArtikliListView(ListView):
    model = Artikl
    paginate_by = 10
    template_name = 'kasa/artikl/artikl_list.html'

    def get_queryset(self):
        query_set = Artikl.objects.filter(tvrtka=self.request.user.tvrtka, is_active=True).order_by('naziv')
        return query_set

    def get_context_data(self, **kwargs):
        context = super(ArtikliListView, self).get_context_data(**kwargs)
        context['pnp'] = settings.PNP
        return context


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ArtikliCreateView(CreateView):
    form_class = ArtiklForm
    template_name = 'kasa/artikl/artikl_dodaj.html'

    def get_success_url(self):
        return reverse('artikli')

    def form_valid(self, form):
        form.instance.tvrtka = self.request.user.tvrtka
        return super().form_valid(form)


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ArtikliUpdateView(UpdateView):
    form_class = ArtiklForm
    template_name = 'kasa/artikl/artikl_uredi.html'

    def get_queryset(self):
        query_set = Artikl.objects.filter(id=self.kwargs['pk'], tvrtka=self.request.user.tvrtka)
        return query_set

    def get_success_url(self):
        return reverse('artikli')


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ArtikliDeleteView(View):

    def get(self, request, *args, **kwargs):

        Artikl.objects.filter(id=self.kwargs['pk'],
                              tvrtka=self.request.user.tvrtka).update(is_active=False)

        return HttpResponseRedirect(reverse('artikli'))


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class PoslovnicaListView(ListView):
    model = Poslovnica
    template_name = 'kasa/poslovnica/poslovnica_list.html'

    def get_queryset(self):
        query_set = Poslovnica.objects.filter(tvrtka=self.request.user.tvrtka, is_active=True).order_by('naziv')
        return query_set


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class PoslovnicaUpdateView(UpdateView):
    model = Poslovnica
    fields = ['naziv', 'mjesto', 'adresa', 'telefon']
    template_name = 'kasa/poslovnica/poslovnica_uredi.html'

    def get_queryset(self):
        query_set = Poslovnica.objects.filter(id=self.kwargs['pk'], tvrtka=self.request.user.tvrtka)
        return query_set

    def get_success_url(self):
        return reverse('poslovnice')


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class PoslovnicaCreateView(CreateView):
    form_class = PoslovnicaForm
    template_name = 'kasa/poslovnica/poslovnica_dodaj.html'

    def get_success_url(self):
        return reverse('poslovnice')

    def form_valid(self, form):
        form.instance.tvrtka = self.request.user.tvrtka

        poslovnica = Poslovnica.objects.filter(tvrtka=self.request.user.tvrtka).aggregate(Max('broj'))

        if poslovnica['broj__max'] is None:
            broj_poslovnice = 1
        else:
            broj_poslovnice = poslovnica['broj__max'] + 1

        form.instance.broj = broj_poslovnice
        form.instance.oznaka = 'POSL' + str(broj_poslovnice)

        return super().form_valid(form)


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class PoslovnicaDeleteView(View):

    def get(self, request, *args, **kwargs):

        poslovnica = Poslovnica.objects.get(id=self.kwargs['pk'], tvrtka=self.request.user.tvrtka)
        poslovnica.is_active = False
        poslovnica.save()

        return HttpResponseRedirect(reverse('poslovnice'))


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class NaplatniUredajListView(ListView):
    model = NaplatniUredaj
    paginate_by = 10
    template_name = 'kasa/naplatni_uredaj/naplatni_uredaj_list.html'

    def get_queryset(self):
        query_set = NaplatniUredaj.objects.filter(
            poslovnica__tvrtka=self.request.user.tvrtka, is_active=True).order_by('-poslovnica', 'broj')
        return query_set


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class NaplatniUredajCreateView(CreateView):
    form_class = NaplatniUredajForm
    template_name = 'kasa/naplatni_uredaj/naplatni_uredaj_dodaj.html'

    def get_success_url(self):
        return reverse('naplatni_uredaji')

    def get_form(self, form_class=form_class):
        form = super().get_form(form_class)
        form.fields['poslovnica'].queryset = Poslovnica.objects.filter(tvrtka=self.request.user.tvrtka, is_active=True)
        form.fields['zaposlenici'].queryset = Zaposlenik.objects.filter(tvrtka=self.request.user.tvrtka, is_active=True)
        return form

    def form_valid(self, form):
        naplatni_uredaj = NaplatniUredaj.objects.filter(
            poslovnica=form.instance.poslovnica).aggregate(Max('broj'))

        if naplatni_uredaj['broj__max'] is None:
            broj_naplatnog_uredaja = 1
        else:
            broj_naplatnog_uredaja = naplatni_uredaj['broj__max'] + 1

        form.instance.broj = broj_naplatnog_uredaja

        return super().form_valid(form)


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class NaplatniUredajDeleteView(View):

    def get(self, request, *args, **kwargs):

        NaplatniUredaj.objects.filter(id=self.kwargs['pk'],
                                      poslovnica__tvrtka=self.request.user.tvrtka).update(is_active=False)

        return HttpResponseRedirect(reverse('naplatni_uredaji'))


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class NaplatniUredajUpdateView(UpdateView):
    form_class = NaplatniUredajForm
    template_name = 'kasa/naplatni_uredaj/naplatni_uredaj_uredi.html'

    def get_form(self, form_class=form_class):
        form = super().get_form(form_class)
        form.fields['poslovnica'].queryset = Poslovnica.objects.filter(tvrtka=self.request.user.tvrtka, is_active=True)
        form.fields['zaposlenici'].queryset = Zaposlenik.objects.filter(tvrtka=self.request.user.tvrtka, is_active=True)
        return form

    def get_queryset(self):
        query_set = NaplatniUredaj.objects.filter(id=self.kwargs['pk'], poslovnica__tvrtka=self.request.user.tvrtka)
        return query_set

    def get_success_url(self):
        return reverse('naplatni_uredaji')


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
class NaplatniUredajOdabirView(TemplateView):
    template_name = 'kasa/naplatni_uredaj/naplatni_uredaj_odabir.html'

    def get_context_data(self, **kwargs):
        context = super(NaplatniUredajOdabirView, self).get_context_data(**kwargs)
        context['naplatni_uredaji'] = NaplatniUredaj.objects.filter(zaposlenici=self.request.user, is_active=True)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        uredaj_id = request.GET.get('uredaj', '')

        if uredaj_id != '':
            try:
                uredaj = NaplatniUredaj.objects.get(id=uredaj_id, zaposlenici=self.request.user, is_active=True)
            except NaplatniUredaj.DoesNotExist:
                uredaj = None

            if uredaj is not None:
                request.session['naplatniuredaj'] = uredaj.broj
                request.session['naplatniuredaj_id'] = uredaj_id

            return HttpResponseRedirect("/")

        return self.render_to_response(context)


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class KupacCreateView(CreateView):
    form_class = KupacForm
    template_name = 'kasa/kupac/kupac_dodaj.html'

    def get_success_url(self):
        return reverse('kupci')

    def form_valid(self, form):
        form.instance.tvrtka = self.request.user.tvrtka
        return super().form_valid(form)


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class KupacListView(ListView):
    model = Kupac
    paginate_by = 10
    template_name = 'kasa/kupac/kupac_list.html'

    def get_queryset(self):
        query_set = Kupac.objects.filter(tvrtka=self.request.user.tvrtka, is_active=True).order_by('naziv')
        return query_set


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class KupacUpdateView(UpdateView):
    model = Kupac
    fields = ['naziv', 'adresa', 'oib', 'napomena']
    template_name = 'kasa/kupac/kupac_uredi.html'

    def get_queryset(self):
        query_set = Kupac.objects.filter(id=self.kwargs['pk'])
        return query_set

    def get_success_url(self):
        return reverse('kupci')


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class KupacDeleteView(View):

    def get(self, request, *args, **kwargs):

        Kupac.objects.filter(id=self.kwargs['pk'],
                             tvrtka=self.request.user.tvrtka).update(is_active=False)

        return HttpResponseRedirect(reverse('kupci'))


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
class PomocView(TemplateView):
    template_name = 'kasa/pomoc/pomoc.html'

@method_decorator(login_required(login_url='/prijava'), name='dispatch')
class IzvjestajiView(TemplateView):
    template_name = 'kasa/izvjestaji/izvjestaji.html'

    def get_context_data(self, **kwargs):
        context = super(IzvjestajiView, self).get_context_data(**kwargs)

        today = datetime.date.today()
        context['operater_promet_mjesec'] = Racun.objects.filter(operater=self.request.user,
                                                        vrijeme_izdavanja__month=today.month,
                                                        vrijeme_izdavanja__year=today.year)\
                                            .aggregate(Sum('ukupni_iznos')).get('ukupni_iznos__sum')

        context['operater_racuni_mjesec'] = Racun.objects.filter(operater=self.request.user,
                                                                 vrijeme_izdavanja__month=today.month,
                                                                 vrijeme_izdavanja__year=today.year).count()

        context['operater_promet_ukupni'] = Racun.objects.filter(operater=self.request.user)\
                                            .aggregate(Sum('ukupni_iznos')).get('ukupni_iznos__sum')

        context['firma_promet_ukupni'] = Racun.objects.filter(operater__tvrtka = self.request.user.tvrtka)\
                                         .aggregate(Sum('ukupni_iznos')).get('ukupni_iznos__sum')

        context['operater_racuni_ukupno'] = Racun.objects.filter(operater=self.request.user).count()

        context['firma_racuni_ukupno'] = Racun.objects.filter(operater__tvrtka = self.request.user.tvrtka).count()

        return context


def prometChart(request, period):

    if period == 0:
        return chart_actions.getMjesecniChartData(request.user)
    elif period == 1:
        return chart_actions.getSatiChartData(request.user)
    elif period == 2:
        return chart_actions.getDnevniChartData(request.user)
    elif period == 3:
        return chart_actions.getGodisnjiChartData(request.user)


@transaction.atomic
def registracija(request):
    if request.method == 'POST':

        zaposlenikForm = ZaposlenikCreateForm(request.POST)
        tvrtkaForm = TvrtkaRegistracijaForm(request.POST)

        if zaposlenikForm.is_valid() and tvrtkaForm.is_valid():
            zaposlenik = zaposlenikForm.save(commit=False)

            tvrtka = tvrtkaForm.save(commit=False)
            tvrtka.save()

            zaposlenik.is_staff = True
            zaposlenik.is_admin = False
            zaposlenik.is_active = False
            zaposlenik.tvrtka = tvrtka

            zaposlenik.save()

            # Slanje email-a za registraciju - START
            current_site = get_current_site(request)
            mail_subject = _('Fiskali kasa - Potvrda registracije')
            message = render_to_string('kasa/registracija/aktivacijski_email.html', {
                'user': zaposlenik,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(zaposlenik.pk)).decode(),
                'token': account_activation_token.make_token(zaposlenik),
            })
            to_email = zaposlenik.email
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )

            email.send()
            # Slanje email-a za registraciju - END

            return render(request, 'kasa/registracija/uspjesna_registracija.html')
    else:
        zaposlenikForm = ZaposlenikCreateForm()
        tvrtkaForm = TvrtkaRegistracijaForm()

    context = {'zaposlenikForm': zaposlenikForm,
               'tvrtkaForm': tvrtkaForm}

    return render(request, 'kasa/registracija/registracija.html', context)


def aktivacija(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        zaposlenik = Zaposlenik.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Zaposlenik.DoesNotExist):
        zaposlenik = None
    if zaposlenik is not None and account_activation_token.check_token(zaposlenik, token):
        zaposlenik.is_active = True
        zaposlenik.save()
        return render(request, 'kasa/registracija/uspjesna_aktivacija.html')
    else:
        return render(request, 'kasa/registracija/neuspjesna_aktivacija.html')


def demo(request):
    user = authenticate(request, username=settings.DEMO_USER, password=settings.DEMO_PASSWORD)
    login(request, user)

    return redirect('home')


def ukupnoAjax(request):
    if request.POST:
        stavkeracuna = StavkaRacunaFormSet(request.POST)

    ukupni_iznos = 0
    pdv_osnovica_porez_ukupno = {}
    stavkeracuna.is_valid()

    for stavka in stavkeracuna:
        cd = stavka.cleaned_data
        if 'artikl' in cd and 'kolicina' in cd and cd['DELETE']!= True:
            iznos_stavke = cd['artikl'].maloprodajna_cijena * cd['kolicina']
            ukupni_iznos = ukupni_iznos + iznos_stavke

            key = cd['artikl'].pdv.stopa

            if key in pdv_osnovica_porez_ukupno:
                pdv_osnovica_porez_ukupno[key]['ukupno'] = pdv_osnovica_porez_ukupno[key]['ukupno'] + iznos_stavke
            else:
                pdv_osnovica_porez_ukupno[key] = {}
                pdv_osnovica_porez_ukupno[key]['ukupno'] = Decimal(iznos_stavke)

    # Unos poreza, osnovice
    ukupno_osnovica = 0
    ukupno_porez = 0
    for key in pdv_osnovica_porez_ukupno:
        pdv_osnovica_porez_ukupno[key]['osnovica'] = pdv_osnovica_porez_ukupno[key]['ukupno'] / \
            Decimal((1 + key / 100))

        ukupno_osnovica = ukupno_osnovica + pdv_osnovica_porez_ukupno[key]['osnovica']

        pdv_osnovica_porez_ukupno[key]['porez'] = pdv_osnovica_porez_ukupno[key]['ukupno'] - \
            pdv_osnovica_porez_ukupno[key]['osnovica']

        ukupno_porez = ukupno_porez + pdv_osnovica_porez_ukupno[key]['porez']

    return_data = {}
    return_data['osnovica'] = "{0: .2f}".format(round(ukupno_osnovica, 2))
    return_data['porez'] = "{0: .2f}".format(round(ukupno_porez, 2))
    return_data['ukupno'] = "{0: .2f}".format(round(ukupni_iznos, 2))

    return JsonResponse(return_data)


def dohvatJediniceArtikla(request):
    artikal = Artikl.objects.get(pk=request.GET['artikal'])

    # TODO: vidit oko ovog
    if artikal.tvrtka_id != request.user.tvrtka.id:
        pass

    return JsonResponse({'jedinica':artikal.jedinica})
