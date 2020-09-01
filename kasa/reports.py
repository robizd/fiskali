import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from geraldo import (Ellipse, Image, Label, Line, ObjectValue, Rect, Report,
                     ReportBand, SubReport)
from geraldo.generators import PDFGenerator

from .models import Racun, StavkaRacuna

# from reportlab.lib.colors import navy, yellow, red

cur_dir = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(cur_dir, 'fonts')

SEGOE_UI = (
    {'file': os.path.join(FONTS_DIR, 'segoeui.ttf'), 'name': 'Segoe UI'},
    {'file': os.path.join(FONTS_DIR, 'segoeuib.ttf'), 'name': 'Segoe UI Bold', 'bold': True}
)


@method_decorator(login_required(login_url='/prijava'), name='dispatch')
class RacunPDFView(View):

    def get(self, request, *args, **kwargs):
        name = "racun.pdf"

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = "attachment; filename*=UTF-8''{filename};".format(filename=name)
        racun = Racun.objects.filter(id=self.kwargs['pk'])
        report = RacunReport(queryset=racun)
        report.generate_by(PDFGenerator, response)

        return response


class SubReport_Porez(SubReport):

    def get_queryset(self, subrepo, racun):
        return racun.racunporez_set.all()
    band_header = ReportBand(
        elements=[
            Label(
                text='Stopa PDV-a',
                top=6.7 * cm,
                width=17 * cm,
                style={'alignment': TA_LEFT, 'fontName': 'Helvetica-Bold', 'fontSize': 10},
            ),
            Label(
                text='Osnovica PDV-a',
                top=6.7 * cm,
                left=3 * cm,
                width=14 * cm,
                style={'alignment': TA_LEFT, 'fontName': 'Helvetica-Bold', 'fontSize': 10},
            ),
            Label(
                text='Iznos PDV-a',
                top=6.7 * cm,
                left=6 * cm,
                width=11 * cm,
                style={'alignment': TA_LEFT, 'fontName': 'Helvetica-Bold', 'fontSize': 10},
            ),
            Label(
                text='Ukupno',
                top=6.7 * cm,
                width=10.5 * cm,
                style={'alignment': TA_RIGHT, 'fontName': 'Segoe UI Bold', 'fontSize': 10},
            ),
        ]
    )
    band_detail = ReportBand(
        height=0.5 * cm,
        elements=[
            ObjectValue(
                get_value=lambda x: '{x.stopa_poreza} %'.format(x=x),
                attribute_name='stopa_poreza',
                top=6.3 * cm,
                width=2 * cm,
                style={'alignment': TA_CENTER},
            ),
            ObjectValue(
                attribute_name='osnovica_poreza',
                top=6.3 * cm,
                width=5.6 * cm,
                style={'alignment': TA_RIGHT},
            ),
            ObjectValue(
                attribute_name='iznos_poreza',
                top=6.3 * cm,
                width=8 * cm,
                height=0.1 * cm,
                style={'alignment': TA_RIGHT},
            ),
            ObjectValue(
                attribute_name='ukupno',
                top=6.3 * cm,
                width=10.5 * cm,
                style={'alignment': TA_RIGHT},
            ),
        ]
    )
    band_footer = ReportBand(
        elements=[
            Line(
                top=6.4 * cm,
                left=0.0 * cm,
                right=10.5 * cm,
                bottom=6.4 * cm,
                stroke_width=0.8,
            ),
            Label(
                text='Ukupno',
                top=6.5 * cm,
                style={'alignment': TA_LEFT, 'fontSize': 13}

            ),
            ObjectValue(
                attribute_name='ukupno_osnovica',
                top=6.5 * cm,
                width=5.6 * cm,
                style={'alignment': TA_RIGHT},
            ),
            ObjectValue(
                attribute_name='ukupno_porez',
                top=6.5 * cm,
                width=8 * cm,
                style={'alignment': TA_RIGHT},
            ),
            ObjectValue(
                attribute_name='ukupni_iznos',
                top=6.5 * cm,
                width=10.5 * cm,
                style={'alignment': TA_RIGHT},
            ),

            ObjectValue(
                get_value=lambda x: 'JIR: {x.jir}'.format(x=x),
                top=8.2 * cm,
                width=17 * cm,
                left=0.5 * cm,
                style={'alignment': TA_LEFT}
            ),
            Rect(left=0 * cm, top=8 * cm, width=10 * cm, height=1.5 * cm),
            ObjectValue(
                get_value=lambda x: 'ZKI: {x.zki}'.format(x=x),
                top=8.7 * cm,
                left=0.5 * cm,
                width=17 * cm,
                style={'alignment': TA_LEFT}
            ),
        ]
    )


class SubReport_StavkeRacuna(SubReport):
    def get_queryset(self, subrepo, racun):
        return racun.stavkaracuna_set.all().order_by('rbr')

    band_detail = ReportBand(
        height=0.7 * cm,
        additional_fonts={'Segoe UI': SEGOE_UI},
        default_style={'fontName': 'Segoe UI', 'fontSize': 12},
        elements=[
            ObjectValue(
                attribute_name='rbr',
                top=6.7 * cm,
                left=0.2 * cm,
                width=17 * cm,
                style={'alignment': TA_LEFT}

            ),
            ObjectValue(
                attribute_name='naziv_artikla',
                top=6.7 * cm,
                left=1.5 * cm,
            ),
            ObjectValue(
                attribute_name='cijena_artikla',
                top=6.7 * cm,
                left=6 * cm,
                width=2 * cm,
                style={'alignment': TA_RIGHT}

            ),
            Label(
                text='kn',
                top=6.7 * cm,
                left=8.3 * cm,
            ),
            ObjectValue(
                attribute_name='kolicina',
                top=6.7 * cm,
                left=10.5 * cm,

            ),
            ObjectValue(
                attribute_name='ukupno',
                top=6.7 * cm,
                width=16.5 * cm,
                style={'alignment': TA_RIGHT}
            ),
            Label(
                text='kn',
                top=6.7 * cm,
                width=17 * cm,
                style={'alignment': TA_RIGHT}

            ),
            Line(
                top=6.6 * cm,
                left=0.0 * cm,
                right=17 * cm,
                bottom=6.6 * cm,
                stroke_width=0.8,
            ),
        ]
    )

    band_footer = ReportBand(
        elements=[
            ObjectValue(
                get_value=lambda x: 'Ukupno {x.ukupni_iznos} kn'.format(x=x),
                top=6.7 * cm,
                width=17 * cm,
                style={'alignment': TA_RIGHT}
            ),
        ]
    )


class RacunReport(Report):
    title = 'Racun'
    page_size = A4
    margin_top = 2 * cm
    margin_bottom = 0
    margin_left = 2 * cm
    margin_right = 2 * cm
    additional_fonts = {'Segoe UI': SEGOE_UI}
    default_style = {'fontName': 'Segoe UI', 'fontSize': 12}

    class band_detail(ReportBand):

        elements = [
            # LOGO
            Image(left=0 * cm, top=0 * cm, width=12 * cm, height=6 * cm,
                  style={'alignment': TA_LEFT}, filename=os.path.join(cur_dir, 'static/kasa/img/logo6.jpg')),

            # TVRTKA
            ObjectValue(attribute_name='operater', get_value=lambda x: '{x.operater.tvrtka}'.format(x=x),
                        width=17 * cm, top=0.3 * cm,
                        style={'alignment': TA_RIGHT}),
            ObjectValue(attribute_name='operater', get_value=lambda x: '{x.operater.tvrtka.adresa}'.format(x=x),
                        width=17 * cm, top=0.8 * cm,
                        style={'alignment': TA_RIGHT}),
            ObjectValue(attribute_name='operater', get_value=lambda x: 'OIB:{x.operater.tvrtka.oib}'.format(x=x),
                        width=17 * cm, top=1.3 * cm,
                        style={'alignment': TA_RIGHT}),
            ObjectValue(attribute_name='operater', get_value=lambda x: 'IBAN: {x.operater.tvrtka.iban}'.format(x=x)
                        if x.operater.tvrtka.iban else "",
                        width=17 * cm, top=1.8 * cm, style={'alignment': TA_RIGHT}),

            # KUPAC
            ObjectValue(attribute_name='kupac', top=3.2 * cm),
            ObjectValue(attribute_name='kupac', get_value=lambda x: '{x.kupac.adresa}'.format(x=x), top=3.7 * cm),
            ObjectValue(attribute_name='kupac', get_value=lambda x: 'OIB: {x.kupac.oib}'.format(x=x), top=4.2 * cm),
            # Label(text='OIB: 48531576841', top=5.1*cm),


            ObjectValue(attribute_name='vrijeme_izdavanja', get_value=lambda x:
                        x.vrijeme_izdavanja.strftime('Datum: %d/%m/%Y'),
                        top=4.8 * cm, width=5 * cm, left=12.5 * cm, style={'alignment': TA_LEFT}),

            ObjectValue(attribute_name='vrijeme_izdavanja', get_value=lambda x:
                        x.vrijeme_izdavanja.strftime('Vrijeme: %H:%M'),
                        top=5.3 * cm, width=5 * cm, left=12.5 * cm, style={'alignment': TA_LEFT}),

            ObjectValue(get_value=lambda x: 'Vrsta plaćanja: {x.opis_nacina_placanja}'.format(x=x),
                        top=5.8 * cm, width=5 * cm, left=12.5 * cm, style={'alignment': TA_LEFT}),

            ObjectValue(get_value=lambda x: 'Račun {x.oznaka}'.format(x=x), top=5.8 * cm, width=17 * cm,
                        style={'alignment': TA_LEFT, 'fontSize': 12}),
            Label(text='R.br.', top=7 * cm, style={'fontName': 'Helvetica-Bold', 'fontSize': 10}),
            Label(text='Naziv', top=7 * cm, left=1.5 * cm, style={'fontName': 'Helvetica-Bold', 'fontSize': 10}),
            Label(text='Jed.cijena', top=7 * cm, left=7 * cm, style={'fontName': 'Helvetica-Bold', 'fontSize': 10}),
            Label(text='Količina', top=7 * cm, left=10 * cm, style={'fontName': 'Segoe UI Bold', 'fontSize': 10}),
            Label(text='Ukupna cijena', top=7 * cm, width=17 * cm,
                  style={'alignment': TA_RIGHT, 'fontName': 'Helvetica-Bold', 'fontSize': 10}),
            Line(
                top=25 * cm,
                left=0.0 * cm,
                right=17 * cm,
                bottom=25 * cm,
                stroke_width=0.8,
            ),
            Label(text='Fiskali d.o.o.', top=25.2 * cm, width=17 * cm,
                  style={'alignment': TA_CENTER, 'fontSize': 10}),
            Label(text='Telefon: 023 300 201 E-mail: fiskali@gmail.com', top=25.6 * cm, width=17 * cm,
                  style={'alignment': TA_CENTER, 'fontSize': 10}),

        ]

    subreports = [
        SubReport_StavkeRacuna(),
        SubReport_Porez()
    ]
