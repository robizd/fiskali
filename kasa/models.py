from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utils import current_year
from .validators import validate_IBAN, validate_OIB


# Create your models here.
class ZaposlenikManager(BaseUserManager):
    def create_user(self, username, first_name, last_name, oib, password):

        if not username:
            raise ValueError('The given username must be set')

        username = self.model.normalize_username(username)

        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            oib=oib,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, first_name='', last_name='', oib=''):

        user = self.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            oib=oib,
            password=password
        )

        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class Zaposlenik(AbstractBaseUser):

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Obavezno polje. 150 znakova ili manje.'),
        validators=[username_validator],
        error_messages={
            'unique': _("Korisničko ime je već u upotrebi."),
        },
    )

    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=150)
    oib = models.CharField(_('OIB'), validators=[validate_OIB], max_length=11)

    email = models.EmailField(
        _('email address'),
        max_length=255
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    tvrtka = models.ForeignKey('Tvrtka', on_delete=models.PROTECT, null=True)

    objects = ZaposlenikManager()

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['first_name', 'last_name', 'oib', 'fizicka_ili_pravna_osoba']

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        verbose_name = _('Zaposlenik')
        verbose_name_plural = _('Zaposlenici')
        unique_together = ('oib', 'tvrtka')

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def save(self, *args, **kwargs):

        super(Zaposlenik, self).save(*args, **kwargs)
        try:
            if self.tvrtka.inicijalizacija is False:
                poslovnica = Poslovnica.objects.get(tvrtka=self.tvrtka)
                naplatni_uredaj = NaplatniUredaj.objects.create(broj=1, poslovnica=poslovnica)
                naplatni_uredaj.zaposlenici.add(self)
                naplatni_uredaj.save()

                self.tvrtka.inicijalizacija = True
                self.tvrtka.save()
        except:
            pass


class Tvrtka(models.Model):
    naziv = models.CharField(_('naziv'), max_length=150)
    mjesto = models.CharField(_('mjesto'), max_length=150)
    adresa = models.CharField(_('adresa'), max_length=150)
    oib = models.CharField(_('OIB'), validators=[validate_OIB], max_length=11)
    iban = models.CharField(_('IBAN'), validators=[validate_IBAN], max_length=34, blank=True)
    u_sustavu_pdv = models.BooleanField(_('u sustavu PDV-a'), default=False)

    telefon_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=('broj telefona nije ispravan'))
    telefon = models.CharField(_('telefon'), validators=[telefon_regex], max_length=17, blank=True)

    certifikat = models.FileField(blank=True, upload_to='certifikati/')
    certifikat_lozinka = models.CharField(max_length=100, blank=True)

    inicijalizacija = models.BooleanField(_('inicijalizacija'), default=False)

    class Meta:
        verbose_name = _('tvrtka')
        verbose_name_plural = _('tvrtke')

    def save(self, *args, **kwargs):
        insert = False
        if not self.pk:
            insert = True

        super(Tvrtka, self).save(*args, **kwargs)

        if insert is True:
            Kupac.objects.create(naziv="Razni kupci", tvrtka=self)
            Poslovnica.objects.create(naziv="Poslovnica 1", oznaka="POSL1", broj=1, tvrtka=self)

    def __str__(self):
        return self.naziv


class Poslovnica(models.Model):
    naziv = models.CharField(_('naziv'), max_length=150)
    mjesto = models.CharField(_('mjesto'), max_length=150, blank=True)
    adresa = models.CharField(_('adresa'), max_length=150, blank=True)
    broj = models.IntegerField(_('broj'))
    oznaka = models.CharField(_('oznaka'), max_length=10)

    telefon_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=('broj telefona nije ispravan'))
    telefon = models.CharField(_('telefon'), validators=[telefon_regex], max_length=17, blank=True)

    tvrtka = models.ForeignKey(Tvrtka, on_delete=models.PROTECT)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('poslovnica')
        verbose_name_plural = _('poslovnice')
        unique_together = (('naziv', 'tvrtka'), ('oznaka', 'tvrtka'), ('broj', 'tvrtka'))

    def save(self, *args, **kwargs):
        super(Poslovnica, self).save(*args, **kwargs)
        if self.is_active is False:
            NaplatniUredaj.objects.filter(poslovnica=self).update(is_active=False)

    def __str__(self):
        return self.naziv


class NaplatniUredaj(models.Model):
    broj = models.IntegerField(_('broj'))
    zaposlenici = models.ManyToManyField(Zaposlenik)
    poslovnica = models.ForeignKey(Poslovnica, on_delete=models.PROTECT)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('naplatni uređaj')
        verbose_name_plural = _('naplatni uređaji')
        unique_together = ('broj', 'poslovnica')

    def __str__(self):
        return str(self.broj)


class Racun(models.Model):

    NACIN_PLACANJA_CHOICES = (
        ('G', 'Gotovina'),
        ('K', 'Kartica'),
        ('T', 'Transakcijski račun'),
        ('O', 'Ostalo')
    )

    vrijeme_izdavanja = models.DateTimeField(_('datum izdavanja'), auto_now_add=True)
    broj = models.IntegerField(_('broj'))
    oznaka = models.CharField(_('oznaka'), max_length=50, default=current_year)
    godina = models.IntegerField(_('godina'))
    nacin_placanja = models.CharField(_('način plaćanja'), max_length=1, choices=NACIN_PLACANJA_CHOICES, default='G')
    zki = models.CharField(max_length=60)
    jir = models.CharField(max_length=60)
    poruka_porezna = models.CharField(max_length=200, blank=True)
    napomena = models.CharField(_('napomena'), max_length=60, blank=True)
    ukupni_iznos = models.DecimalField(_('ukupni iznos'), max_digits=10, decimal_places=2, null=True)
    ukupno_osnovica = models.DecimalField(_('ukupno osnovica'), max_digits=10, decimal_places=2, null=True)
    ukupno_porez = models.DecimalField(_('ukupno porez'), max_digits=10, decimal_places=2, null=True)
    naziv_operatera = models.CharField(_('naziv operatera'), max_length=150)
    naziv_kupca = models.CharField(_('naziv kupca'), max_length=150)

    zakljucan = models.BooleanField(_('zakljucan'), default=False)

    operater = models.ForeignKey(Zaposlenik, on_delete=models.PROTECT)
    naplatni_uredaj = models.ForeignKey(NaplatniUredaj, on_delete=models.PROTECT)
    kupac = models.ForeignKey('Kupac', verbose_name=_('kupac'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('racun')
        verbose_name_plural = _('racuni')
        unique_together = ('broj', 'naplatni_uredaj', 'godina')

    def save(self, *args, **kwargs):

        if self.zakljucan is False:
            self.naziv_operatera = str(self.operater)
            self.naziv_kupca = str(self.kupac)
            self.zakljucan = True

        super(Racun, self).save(*args, **kwargs)

    def __str__(self):
        return "Broj racuna" + ' ' + str(self.broj)

    @property
    def opis_nacina_placanja(self):
        opisdict = {oznaka: opis for oznaka, opis in self.NACIN_PLACANJA_CHOICES}
        return opisdict[self.nacin_placanja]


class RacunPorez(models.Model):
    stopa_poreza = models.IntegerField(_('stopa poreza'))
    osnovica_poreza = models.DecimalField(_('osnovica poreza'), max_digits=10, decimal_places=2)
    iznos_poreza = models.DecimalField(_('iznos poreza'), max_digits=10, decimal_places=2)
    ukupno = models.DecimalField(_('ukupno'), max_digits=10, decimal_places=2)

    racun = models.ForeignKey(Racun, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('racun porez')
        verbose_name_plural = _('racun porezi')

    def __str__(self):
        return "Broj racuna" + ' ' + str(self.racun.broj)


class StavkaRacuna(models.Model):
    rbr = models.IntegerField(_('redni broj'), default=0)
    kolicina = models.IntegerField(_('količina'))
    naziv_artikla = models.CharField(_('naziv'), max_length=150)
    cijena_artikla = models.DecimalField(_('cijena'), max_digits=10, decimal_places=2)
    pdv_artikla = models.IntegerField(_('PDV'))
    pnp_artikla = models.BooleanField(_('PNP'), default=False)
    ukupno = models.DecimalField(_('ukupno'), max_digits=10, decimal_places=2)
    zakljucan = models.BooleanField(_('zakljucan'), default=False)

    artikl = models.ForeignKey('Artikl', verbose_name=_('artikl'), on_delete=models.PROTECT)
    racun = models.ForeignKey(Racun, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('stavka računa')
        verbose_name_plural = _('stavke računa')

    def save(self, *args, **kwargs):

        if self.zakljucan is False:
            self.naziv_artikla = self.artikl.naziv
            self.cijena_artikla = self.artikl.maloprodajna_cijena
            self.pdv_artikla = self.artikl.pdv.stopa
            self.pnp_artikla = self.artikl.pnp
            self.ukupno = self.cijena_artikla * self.kolicina
            self.zakljucan = True

        super(StavkaRacuna, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class Artikl(models.Model):
    JEDINICA = (
        ('KOM', 'kom'),
        ('L', 'l'),
        ('KG', 'kg'),
        ('DAN', 'dan'),
        ('SAT', 'sat'),
    )

    naziv = models.CharField(_('naziv'), max_length=150)
    maloprodajna_cijena = models.DecimalField(_('maloprodajna cijena'), max_digits=10, decimal_places=2)
    tvrtka = models.ForeignKey('Tvrtka', on_delete=models.PROTECT)
    pdv = models.ForeignKey('PDV', on_delete=models.PROTECT)
    pnp = models.BooleanField(_('Porez na potrošnju (PNP)'), default=False)
    jedinica = models.CharField(_('jedinica'), max_length=10, choices=JEDINICA, default='KOM')

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('artikl')
        verbose_name_plural = _('artikli')
        unique_together = ('naziv', 'tvrtka')

    def __str__(self):
        return self.naziv


class Kupac(models.Model):
    naziv = models.CharField(_('naziv'), max_length=150)
    adresa = models.CharField(_('adresa'), max_length=150)
    oib = models.CharField(_('OIB'), validators=[validate_OIB], max_length=11, blank=True)
    napomena = models.CharField(_('napomena'), max_length=150, blank=True)
    tvrtka = models.ForeignKey('Tvrtka', on_delete=models.PROTECT)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('kupac')
        verbose_name_plural = _('kupci')
        unique_together = ('oib', 'naziv', 'tvrtka')

    def __str__(self):
        return self.naziv


class PDV(models.Model):
    stopa = models.IntegerField(_('Stopa PDV-a [%]'))

    class Meta:
        verbose_name = _('PDV')
        verbose_name_plural = _('PDV')

    def __str__(self):
        return str(self.stopa) + '%'
