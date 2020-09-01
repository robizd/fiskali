from django.http import HttpResponseRedirect


def naplatni_uredaj_odabir(f):

        def wrap(request, *args, **kwargs):

                if 'naplatniuredaj' not in request.request.session.keys():
                        return HttpResponseRedirect("/naplatni-uredaji/odabir")
                return f(request, *args, **kwargs)

        wrap.__doc__ = f.__doc__
        wrap.__name__ = f.__name__

        return wrap
