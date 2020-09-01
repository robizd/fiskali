from django.http import HttpResponseRedirect


class NaplatniUredajOdabirMixin():

    def dispatch(self, request, *args, **kwargs):

        if 'naplatniuredaj' not in request.session.keys() or 'naplatniuredaj_id' not in request.session.keys():
            return HttpResponseRedirect("/naplatni-uredaji/odabir")

        return super().dispatch(request, *args, **kwargs)
