from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .forms import ZaposlenikChangeForm, ZaposlenikCreationForm
from .models import (PDV, Artikl, Kupac, NaplatniUredaj, Poslovnica, Racun,
                     RacunPorez, StavkaRacuna, Tvrtka, Zaposlenik)

# Register your models here.
admin.site.register(
    [
        Tvrtka,
        Poslovnica,
        NaplatniUredaj,
        StavkaRacuna,
        Artikl,
        Kupac,
        PDV,
        RacunPorez
    ]
)


class ZaposlenikAdmin(BaseUserAdmin):

    form = ZaposlenikChangeForm
    add_form = ZaposlenikCreationForm

    list_display = ('username', 'first_name', 'last_name', 'oib', 'tvrtka', 'is_admin', 'is_staff', 'is_active')
    list_filter = ('username', 'oib')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Osobni podaci', {'fields': ('first_name', 'last_name', 'oib', 'tvrtka')}),
        ('Dozvole', {'fields': ('is_admin', 'is_staff', 'is_active')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'oib', 'tvrtka',
                       'password1', 'password2')}),
    )

    search_fields = ('first_name', 'last_name', 'oib', 'tvrtka')
    ordering = ('email',)

    filter_horizontal = ()


class StavkaRacunaInline(admin.StackedInline):
    model = StavkaRacuna


class RacunPorezInline(admin.StackedInline):
    model = RacunPorez


@admin.register(Racun)
class RacunAdmin(admin.ModelAdmin):
    inlines = [RacunPorezInline, StavkaRacunaInline]


admin.site.register(Zaposlenik, ZaposlenikAdmin)

admin.site.unregister(Group)
