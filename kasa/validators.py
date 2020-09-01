from django.core.exceptions import ValidationError
from stdnum import iban
from stdnum.hr import oib


def validate_OIB(oib_param):
    try:
        oib.validate(oib_param)
    except Exception:
        raise ValidationError(
            'Potrebno je unijeti ispravan OIB')


def validate_IBAN(iban_param):
    try:
        iban.validate(iban_param)
    except Exception:
        raise ValidationError(
            'Potrebno je unijeti ispravan IBAN')
