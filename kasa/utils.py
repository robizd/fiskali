import datetime


def current_year():
    return datetime.date.today().year


def current_month():
    return datetime.date.today().month


def current_day():
    return datetime.date.today().day


def current_week():
    return datetime.date.today().weekday()
