"""fiskalna URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from kasa.misc_views import (ArtiklAutocompleteView, KupacAutocompleteView, UredajAutocompleteVeiw,
                             OperaterAutocompleteVeiw, PoslovnicaAutocompleteVeiw)
from kasa.reports import RacunPDFView
from kasa.views import (ArtikliCreateView, ArtikliDeleteView, ArtikliListView,
                        ArtikliUpdateView, KupacCreateView, KupacDeleteView,
                        KupacListView, KupacUpdateView, MojiRacuniListView,
                        NaplatniUredajCreateView, NaplatniUredajDeleteView,
                        NaplatniUredajListView, NaplatniUredajOdabirView,
                        NaplatniUredajUpdateView, NoviRacunCreateView,
                        PomocView, PoslovnicaCreateView, PoslovnicaDeleteView,
                        PoslovnicaListView, PoslovnicaUpdateView,
                        RacunDetailView, RacuniListView, TvrtkaUpdateView,
                        TvrtkaView, ZaposlenikCreateView, ZaposlenikDeleteView,
                        ZaposlenikListView, ZaposlenikUpdateView, aktivacija,
                        demo, registracija, IzvjestajiView)

from kasa.izvjestaji.view import (IzvjestajiRacunView, IzvjestajiPrometView, artikliSelect2, kupacSelect2,
                                  poslovnicaSelect2)


urlpatterns = [
    path('', NoviRacunCreateView.as_view(), name='home'),

    path(_('prijava'), auth_views.LoginView.as_view(), name="prijava"),
    path(_('odjava'), auth_views.LogoutView.as_view(), name="odjava"),
    path(_('registracija'), registracija, name="registracija"),
    url(_(r'^aktivacija/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'),
        aktivacija, name='aktivacija'),
    path(_('demo'), demo, name="demo"),

    path('admin/', admin.site.urls),
    path(_('racuni'), RacuniListView.as_view(), name="racuni"),
    path(_('moji-racuni'), MojiRacuniListView.as_view(), name="moji_racuni"),
    # path('lang', set_language, name="lang"),

    path(_('tvrtka/<int:pk>/'), TvrtkaView.as_view(), name="tvrtka"),
    path(_('tvrtka/izmijeni/<int:pk>/'), TvrtkaUpdateView.as_view(), name="tvrtka_izmijeni"),

    path(_('zaposlenici'), ZaposlenikListView.as_view(), name="zaposlenici"),
    path(_('zaposlenici/izmijeni/<int:pk>/'), ZaposlenikUpdateView.as_view(), name="zaposlenici_izmijeni"),
    path(_('zaposlenici/dodaj'), ZaposlenikCreateView.as_view(), name="zaposlenici_dodaj"),
    path(_('zaposlenici/izbrisi/<int:pk>/'), ZaposlenikDeleteView.as_view(), name="zaposlenici_brisi"),

    path(_('artikli'), ArtikliListView.as_view(), name="artikli"),
    path(_('artikli/izbrisi/<int:pk>/'), ArtikliDeleteView.as_view(), name="artikli_brisi"),
    path(_('artikli/dodaj'), ArtikliCreateView.as_view(), name="artikli_dodaj"),
    path(_('artikli/izmijeni/<int:pk>/'), ArtikliUpdateView.as_view(), name="artikli_izmijeni"),

    path(_('poslovnice'), PoslovnicaListView.as_view(), name="poslovnice"),
    path(_('poslovnica/izmijeni/<int:pk>/'), PoslovnicaUpdateView.as_view(), name="poslovnica_izmijeni"),
    path(_('poslovnica/dodaj'), PoslovnicaCreateView.as_view(), name="poslovnica_dodaj"),
    path(_('poslovnica/izbrisi/<int:pk>/'), PoslovnicaDeleteView.as_view(), name="poslovnica_brisi"),

    path(_('naplatni-uredaji'), NaplatniUredajListView.as_view(), name="naplatni_uredaji"),
    path(_('naplatni-uredaji/izmijeni/<int:pk>/'), NaplatniUredajUpdateView.as_view(), name="naplatni_uredaji_izmijeni"),
    path(_('naplatni-uredaji/dodaj'), NaplatniUredajCreateView.as_view(), name="naplatni_uredaji_dodaj"),
    path(_('naplatni-uredaji/odabir'), NaplatniUredajOdabirView.as_view(), name="naplatni_uredaji_odabir"),
    path(_('naplatni-uredaji/izbrisi/<int:pk>/'), NaplatniUredajDeleteView.as_view(), name="naplatni_uredaji_brisi"),

    path(_('kupac/dodaj'), KupacCreateView.as_view(), name="kupac_dodaj"),
    path(_('kupci'), KupacListView.as_view(), name="kupci"),
    path(_('kupac/izmjeni/<int:pk>/'), KupacUpdateView.as_view(), name="kupac_izmijeni"),
    path(_('kupac/izbrisi/<int:pk>/'), KupacDeleteView.as_view(), name="kupac_brisi"),

    path(_('izvjestaj'), IzvjestajiView.as_view(), name='izvjestaji'),
    path(_('racuni/izvjestaj'), IzvjestajiRacunView.as_view(), name='racuni_izvjestaj'),
    path(_('promet/izvjestaj'), IzvjestajiPrometView.as_view(), name='promet_izvjestaj'),
    path('promet/artikl', artikliSelect2, name='artikl_select2'),
    path('promet/kupac', kupacSelect2, name='kupac_select2'),
    path('promet/poslovnica', poslovnicaSelect2, name='poslovnica_select2'),

    path(_('racun-pdf/<int:pk>/'), RacunPDFView.as_view(), name="racun_pdf"),
    path(_('racun-detalji/<int:pk>/<int:display>/'), RacunDetailView.as_view(), name="racun_detalji"),

    path(_('pomoc'), PomocView.as_view(), name='pomoc'),

    # Autocomplete's
    url(r'^kupac-autocomplete/$', KupacAutocompleteView.as_view(), name='kupac-autocomplete',),
    url(r'^artikl-autocomplete/$', ArtiklAutocompleteView.as_view(), name='artikl-autocomplete',),
    url(r'^operater-autocomplete/$', OperaterAutocompleteVeiw.as_view(), name='operater-autocomplete',),
    url(r'^uredaj-autocomplete/$', UredajAutocompleteVeiw.as_view(), name='uredaj-autocomplete',),
    url(r'^poslovnica-autocomplete/$', PoslovnicaAutocompleteVeiw.as_view(), name='poslovnica-autocomplete',),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
