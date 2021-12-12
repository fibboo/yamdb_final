import datetime as dt


def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    year_context = dt.datetime.today().year
    return {
        'year': year_context
    }
