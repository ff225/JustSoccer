from django.shortcuts import render, redirect, reverse
from django.views.generic import DetailView, ListView, View
from bookingFootballField.models import pendingReservation
from .forms import SearchPitch, SearchBase
from footballFieldManagement.models import CampiDaCalcio
from django.db.models import Avg
import datetime


class SearchView(View):
    form_class = SearchBase
    template_name = 'home.html'

    def get(self, request):
        form = SearchBase()

        if request.user.is_superuser:
            return redirect('/admin')

        if request.user.has_perm('footballFieldManagement.change_campidacalcio'):
            return redirect('scheduledmatch')

        if request.user.id is None:
            pass
        else:
            citta = request.user.citta[0] + request.user.citta[1:].lower()
            form.initial['citta'] = citta

        date = datetime.datetime.now().time()
        hour = date.hour + 1
        date = date.replace(hour=hour, minute=00)
        form.initial['giorni_apertura'] = datetime.date.today()
        form.initial['orario_apertura'] = date.__format__('%H:%M')
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SearchBase(request.POST)

        fields = {}
        print('Search result form is valid:', form.is_valid())
        if form.is_valid():
            for field in form.fields:
                fields[field] = form.cleaned_data[field]

            print('Query:', fields)
            giorno_settimana = fields['giorni_apertura'].weekday()
            giorno_cal = fields['giorni_apertura'].strftime("%d/%m/%y")

            urlparams = '?citta=%s&orario=%s&giorni_apertura=%s&giorno_cal=%s' % (
                fields['citta'], fields['orario_apertura'], giorno_settimana, giorno_cal)
            return redirect(reverse('searchBase') + urlparams)

        return render(request, self.template_name, {'form': form})


class ListSearchBaseResult(ListView):
    model = CampiDaCalcio
    template_name = 'search/search_result.html'

    def get_queryset(self):
        orario = self.request.GET.get('orario')
        citta = self.request.GET.get('citta').upper()
        giorno_apertura = self.request.GET.get('giorni_apertura')
        giorno_cal = self.request.GET.get('giorno_cal')
        giorno_cal = datetime.datetime.strptime(giorno_cal, '%d/%m/%y').date()

        campi_riservati = pendingReservation.objects.filter(ora__exact=orario, campo__citta=citta,
                                                            data=giorno_cal).values_list('campo_id')
        #print('Campi riservati:', campi_riservati)

        campi = CampiDaCalcio.objects.filter(orario_apertura__lte=orario, orario_chiusura__gt=orario, citta=citta,
                                             giorni_apertura__regex=giorno_apertura, chiuso=False).exclude(
            id__in=campi_riservati)

        campi = campi.annotate(avg=Avg('review__voto')).order_by('-avg')
        return campi

    def post(self, request):
        # recupero pk
        orario = request.GET.get('orario')
        giorno = request.GET.get('giorno_cal')

        url = '?orario=%s&giorno=%s' % (orario, giorno)
        pk = request.POST.get('campo')

        if (pk == None):
            return redirect('listFF')
        print('pk campo:', pk)
        return redirect(reverse('reserve', args=[pk]) + url)


class SearchResult(DetailView):
    form_class = SearchPitch
    template_name = 'search/search.html'

    def get(self, request):
        form = SearchPitch()

        if request.user.id == None:
            pass
        else:
            form.initial['citta'] = request.user.citta

        date = datetime.datetime.now().time()
        hour = date.hour + 1
        date = date.replace(hour=hour, minute=00)
        form.initial['giorni_apertura'] = datetime.date.today()
        form.initial['orario_apertura'] = date.__format__('%H:%M')
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SearchPitch(request.POST)

        fields = {}
        print('Search result form is valid:', form.is_valid())
        if form.is_valid():
            for field in form.fields:
                fields[field] = form.cleaned_data[field]

            print('Query:', fields)
            giorno_settimana = fields['giorni_apertura'].weekday()
            giorno_cal = fields['giorni_apertura'].strftime("%d/%m/%y")

            urlparams = '?citta=%s&orario=%s&prezzo=%s&tipo_campo=%s&giorni_apertura=%s&giorno_cal=%s' % (
                fields['citta'], fields['orario_apertura'], fields['prezzo_campo'], fields['tipo_campo'][0],
                giorno_settimana, giorno_cal)
            return redirect(reverse('search_result') + urlparams)

        return render(request, self.template_name, {'form': form})


class ListSearch(ListView):
    model = CampiDaCalcio
    template_name = 'search/search_result.html'

    def get_queryset(self):
        orario = self.request.GET.get('orario')
        citta = self.request.GET.get('citta')
        citta = citta.upper()
        prezzo = self.request.GET.get('prezzo')
        tipo_campo = self.request.GET.get('tipo_campo')
        giorno_apertura = self.request.GET.get('giorni_apertura')
        giorno_cal = self.request.GET.get('giorno_cal')
        giorno_cal = datetime.datetime.strptime(giorno_cal, '%d/%m/%y').date()

        campi_riservati = pendingReservation.objects.filter(ora__exact=orario, campo__citta=citta,
                                                            data=giorno_cal,
                                                            campo__tipo_campo=tipo_campo).values_list('campo_id')

        x = CampiDaCalcio.objects.filter(orario_apertura__lte=orario, orario_chiusura__gt=orario, citta=citta,
                                         tipo_campo=tipo_campo, giorni_apertura__regex=giorno_apertura,
                                         prezzo_campo__lte=prezzo, chiuso=False).exclude(id__in=campi_riservati)
        # print('type x:', type(x))
        # print('x:', x)
        y = x.annotate(avg=Avg('review__voto')).order_by('avg')
        # print('y:', y)
        # print('type:', type(y))
        # for z in y:
        #   print(z.__dict__)

        return y

    def post(self, request):
        # recupero pk
        orario = request.GET.get('orario')
        giorno = request.GET.get('giorno_cal')

        url = '?orario=%s&giorno=%s' % (orario, giorno)
        pk = request.POST.get('campo')

        if (pk == None):
            return redirect('listFF')
        print('pk campo:', pk)
        return redirect(reverse('reserve', args=[pk]) + url)
