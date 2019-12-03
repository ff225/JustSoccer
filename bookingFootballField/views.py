from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from .models import pendingReservation, review, payment
from .forms import pendingReservationForm, confirmReservation, reviewForm
from search.forms import SearchPitch
from footballFieldManagement.models import CampiDaCalcio, eventi
from accounts.models import UtentiRegistrati
import datetime
from footballFieldManagement.forms import AddFootballField
from urllib.parse import quote
from PrenotazioneCampi.settings import STRIPE_SECREAT_KEY
import stripe
from django.contrib import messages
from django.core.mail import send_mail


# Create your views here.


class AboutFootballField(DetailView):
    model = CampiDaCalcio
    template_name = 'bookingFootballField/infoCampiUT.html'

    def get(self, request, pk):
        if CampiDaCalcio.objects.filter(pk=pk):
            campo = CampiDaCalcio.objects.get(pk=pk).__dict__
            campo['citta'] = campo['citta'][0] + campo['citta'][1:].lower()
            campo['nomeCampo'] = campo['nomeCampo'][0].upper() + campo['nomeCampo'][1:].lower()
            campo['via'] = campo['via'][0].upper() + campo['via'][1:].lower()
            print('Informazioni sul campo: ', campo)

            form = AddFootballField(initial=campo)
            lng = str(campo['longitudine'])
            lat = str(campo['latitudine'])
            form.initial['longitudine'] = lng
            form.initial['latitudine'] = lat

            voti = review.objects.filter(campo_id=pk).values('voto')
            if voti.count() != 0:
                n_voti = voti.count()
                print(voti)
                media_voti = 0
                for voto in voti:
                    media_voti += voto.get('voto')
                media_voti /= n_voti

                return render(request, self.template_name,
                              {'form': form, 'pk': pk, 'media': media_voti, 'chiuso': campo['chiuso']})
            return render(request, self.template_name,
                          {'form': form, 'pk': pk, 'media': 'non è stato recensito', 'chiuso': campo['chiuso']})
        else:
            return redirect('home')


class ReserveField(View, PermissionRequiredMixin):
    permission_required = 'bookingFootballField.add_pendingreservation'
    template_name = 'bookingFootballField/booking.html'

    def get(self, request, pk):
        path = request.get_full_path()

        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=%s' % quote(path))

        if not request.user.has_perm('bookingFootballField.add_pendingreservation'):
            return redirect('home')

        if CampiDaCalcio.objects.filter(pk=pk):
            giorno = self.request.GET.get('giorno')
            orario = self.request.GET.get('orario')

            campo = CampiDaCalcio.objects.get(pk=pk)
            cliente = UtentiRegistrati.objects.get(pk=self.request.user.id)
            prezzo_c = campo.prezzo_campo
            data = {'cliente': cliente, 'campo': campo, 'ora': orario, 'data': giorno}
            print('data:', data)
            form = pendingReservationForm(initial=data)

            lng = str(campo.longitudine)
            lat = str(campo.latitudine)

            return render(request, self.template_name,
                          {'form': form, 'pk': campo.pk, 'lng': lng, 'lat': lat, 'prezzo_c': str(prezzo_c)})
        else:
            return redirect('search')

    def post(self, request, pk):
        form = pendingReservationForm(request.POST)

        print('is valid:', form.is_valid())
        fields = {}
        if form.is_valid():
            for field in form.fields:
                fields[field] = form.cleaned_data[field]

            reservation = pendingReservation(**fields)
            if not reservation.check_reservation_data():
                messages.warning(request, 'Non è possibile prenotare un campo con la data del passato!')
                return redirect('search')

            if reservation.ora < reservation.campo.orario_apertura or reservation.ora >= reservation.campo.orario_chiusura:
                messages.warning(request, 'Orario errato!')
                return redirect('search')

            if not str(reservation.data.weekday()) in reservation.campo.giorni_apertura:
                messages.warning(request, 'Impossibile prenotare!')
                return redirect('search')

            if reservation.check_reservation_data_hour():
                messages.warning(request, 'Orario errato!')
                return redirect('search')

            reservation.accettato = None
            reservation.save()
            print(fields)

            return redirect('payament', reservation.pk)

        print('errori presenti nel form: ', form.errors)
        return render(request, 'search/search.html',
                      {'form': SearchPitch, 'message_error': 'Impossibile prenotare campo'})


class Payment(View, PermissionRequiredMixin):
    permission_required = 'bookingFootballField.add_pendingreservation'
    template_name = 'bookingFootballField/payment.html'
    stripe.api_key = STRIPE_SECREAT_KEY

    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
        print('Utente ha i permessi:', request.user.has_perm('bookingFootballField.add_pendingreservation'))
        if not request.user.has_perm('bookingFootballField.add_pendingreservation'):
            return redirect('home')
        reservation = pendingReservation.objects.filter(pk=pk, cliente_id=request.user.id,
                                                        accettato=True)
        if not reservation.exists():
            reservation = pendingReservation.objects.get(pk=pk)

            utente = reservation.cliente.username
            campo = reservation.campo.nomeCampo
            prezzo = reservation.campo.prezzo_campo
            data = reservation.data
            ora = reservation.ora
            return render(request, self.template_name,
                          {'utente': utente, 'campo': campo, 'prezzo': prezzo, 'data': data, 'ora': ora, 'pk': pk})

        return redirect('scheduledmatch')

    def post(self, request, pk):

        reservation = pendingReservation.objects.get(pk=pk)
        print(reservation.__dict__)
        prezzo = int(reservation.campo.prezzo_campo * 100)
        try:
            print('dentro try')
            token = self.request.POST.get('stripeToken')
            print(token)
            charge = stripe.Charge.create(
                amount=prezzo,  # cents
                currency="eur",
                source=token
            )

            transazione = payment()
            transazione.stripe_charge_id = charge['id']
            transazione.cliente = reservation.cliente
            transazione.prezzo = prezzo
            transazione.save()
            print('salvo transazione')
            reservation.payment = transazione
            reservation.accettato = True
            reservation.save()

            send_mail(
                'Prenotazione campo: ' + reservation.campo.nomeCampo + ' data: ' + reservation.data.strftime(
                    '%d/%m/%y') + ', ' + reservation.ora.__format__('%H:%M'),
                'Caro ' + reservation.cliente.first_name +
                ',\nTi informiamo che abbiamo ricevuto il pagamento.' +
                '\nInformazioni sulla prenotazione:\n' +
                'Campo: ' + reservation.campo.nomeCampo +
                '\nData: ' + str(reservation.data) +
                '\nOra: ' + str(reservation.ora) +
                '\nPuoi trovare la prenotazione in "partite in programma".' +
                '\nBuon divertimento! ',
                reservation.campo.email,
                [reservation.cliente.email],
                fail_silently=False,
            )
            return redirect('nextmatch')

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught

            print('Status is: %s' % e.http_status)
            print('Type is: %s' % e.error.type)
            print('Code is: %s' % e.error.code)
            # param is '' in this case
            print('Param is: %s' % e.error.param)
            print('Message is: %s' % e.error.message)
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            print('1 ', e)
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print('2', e)
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            print('3', e)
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            print('3', e)
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            print('4', e)
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            print('5', e)
        messages.warning(request, 'Prenotazione fallita. Puoi riprovare in prenotazioni in attesa.')
        send_mail(
            'Prenotazione campo: ' + reservation.campo.nomeCampo + ' data: ' + reservation.data.strftime(
                '%d/%m/%y') + ', ' + reservation.ora.__format__('%H:%M'),
            'Caro ' + reservation.cliente.first_name +
            ',\nTi informiamo che il pagamento non è andato a buon fine.' +
            '\nInformazioni sulla prenotazione:\n' +
            'Campo: ' + reservation.campo.nomeCampo +
            '\nData: ' + str(reservation.data) +
            '\nOra: ' + str(reservation.ora) +
            '\nPuoi riprovare seguendo il link: ' + 'http://127.0.0.1:8000' + request.path,
            reservation.campo.email,
            [reservation.cliente.email],
            fail_silently=False,
        )
        return redirect('home')


# Storico partite giocate
class ListAcceptedReservationUt(ListView, PermissionRequiredMixin):
    permission_required = 'bookingFootballField.add_pendingreservation'
    model = pendingReservation
    template_name = 'bookingFootballField/storicoUT.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
        if not request.user.has_perm(self.permission_required):
            return redirect('home')
        prenotazioni = pendingReservation.objects.filter(cliente_id=self.request.user.id,
                                                         data__lt=datetime.datetime.today().date()).exclude(
            accettato=None).order_by('data', 'ora')

        print(self.request.user.id)
        return render(request, self.template_name, {'pendingreservation_list': prenotazioni})


class ListPendingReservationUt(ListView, PermissionRequiredMixin):
    permission_required = 'bookingFootballField.add_pendingreservation'
    model = pendingReservation
    template_name = 'bookingFootballField/prenotazioni_attesa.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
        if not request.user.has_perm(self.permission_required):
            return redirect('home')
        data = datetime.datetime.today()
        pendingReservation.objects.filter(cliente_id=self.request.user.id, accettato=None,
                                          data__lte=data.date(),
                                          ora__lte=data.time()).delete()
        prenotazioni = pendingReservation.objects.filter(cliente_id=self.request.user.id, accettato=None).order_by(
            'data', 'ora')

        return render(request, self.template_name, {'pendingreservation_list': prenotazioni})

    def post(self, request):
        pk = request.POST.get('prenotazione')

        if (pk == None):
            return redirect('reservation_attesa')
        return redirect(reverse('payament', args=[pk]))


class ListScheduledMatchesUt(ListView, PermissionRequiredMixin):
    permission_required = 'bookingFootballField.add_pendingreservation'
    model = pendingReservation
    template_name = 'bookingFootballField/storicoUT.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
        if not request.user.has_perm(self.permission_required):
            return redirect('home')
        prenotazioni = pendingReservation.objects.filter(
            cliente_id=self.request.user.id, data__gte=datetime.datetime.today().date(),
            ora__gt=datetime.datetime.now().time()).exclude(
            accettato=None).order_by('data', 'ora')
        return render(request, self.template_name, {'pendingreservation_list': prenotazioni})


class DeletePendingReservationUt(DeleteView, PermissionRequiredMixin):
    permission_required = 'bookingFootballField.delete_pendingreservation'
    model = pendingReservation
    template_name = 'footballFieldManagement/field_confirm_delete.html'

    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
        if not request.user.has_perm(self.permission_required):
            return redirect('home')
        prenotazione = pendingReservation.objects.get(pk=pk)
        prenotazione = prenotazione.campo.nomeCampo + ' ' + prenotazione.data.strftime(
            '%d/%m/%y') + ' ' + prenotazione.ora.strftime('%H:%M')
        return render(request, self.template_name, {'object': prenotazione})

    success_url = reverse_lazy('reservation_attesa')


'''
    def post(self, request, pk):
        pendingReservation.objects.get(pk=pk).delete()
        return redirect('reservation_attesa')
'''


class ListEventUt(ListView):
    model = eventi
    template_name = 'footballFieldManagement/listEvent.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
        if not request.user.has_perm('bookingFootballField.add_pendingreservation'):
            return redirect('home')

        citta = self.request.user.citta
        eventi_disp = eventi.objects.filter(organizzatore__citta=citta, scadenza_iscrizione__gte=datetime.date.today())

        return render(request, self.template_name, {'eventi_list': eventi_disp})

    def post(self, request):
        pk = request.POST.get('evento')
        evento = eventi.objects.get(pk=pk)
        print('ciao')
        print(self.request.user.email)
        send_mail(
            'Evento: ' + evento.titolo,
            'Gentile ' + self.request.user.first_name + ',\n' +
            "Grazie per l'interesse. Ti informiamo che le iscrizioni saranno aperte fino al:" + evento.scadenza_iscrizione.strftime(
                '%d/%m/%y') + '.\nPer maggiori informazioni contatta il campo al numero: ' + evento.organizzatore.telefono
            + '\n\nCordiali saluti, \n' + evento.organizzatore.nomeCampo + '.',
            evento.organizzatore.email,
            [self.request.user.email],
        )

        messages.info(request, 'Ti abbiamo inviato una email!')
        return redirect('home')


# Partite che sono state giocate
class ListAcceptedReservationPrp(ListView, PermissionRequiredMixin):
    permission_required = 'bookingFootballField.change_pendingreservation'
    model = pendingReservation
    template_name = 'bookingFootballField/storicoPRP.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
        if not request.user.has_perm(self.permission_required):
            return redirect('home')
        prenotazioni = pendingReservation.objects.filter(
            campo__proprietario__p_iva=self.request.user.proprietario.p_iva,
            data__lte=datetime.datetime.today().date()).exclude(accettato=None).order_by('data',
                                                                                         'ora')
        return render(request, self.template_name, {'pendingreservation_list': prenotazioni})


# Partite che devono essere giocate
class ListScheduledMatchesPrp(ListView, PermissionRequiredMixin):
    permission_required = 'bookingFootballField.change_pendingreservation'
    model = pendingReservation
    template_name = 'bookingFootballField/storicoPRP.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
        if not request.user.has_perm(self.permission_required):
            return redirect('home')
        giorno = datetime.datetime.today().date()
        ora = datetime.datetime.today().time().__format__('%H:%M')
        prenotazioni = pendingReservation.objects.filter(
            campo__proprietario__p_iva=self.request.user.proprietario.p_iva,
            data__gte=giorno,
            ora__gte=ora).exclude(accettato=None).order_by('data',
                                                           'ora')
        return render(request, self.template_name, {'pendingreservation_list': prenotazioni})



class ListPendingReservationPrp(ListView, PermissionRequiredMixin):
    permission_required = 'bookingFootballField.change_pendingreservation'
    model = pendingReservation
    template_name = 'bookingFootballField/prenotazioni_attesaPRP.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
        if not request.user.has_perm(self.permission_required):
            return redirect('home')

        form = confirmReservation()
        data = datetime.datetime.today()
        pendingReservation.objects.filter(campo__proprietario__p_iva=self.request.user.proprietario.p_iva,
                                          accettato=None, data__lte=data.date(), ora__lte=data.time()).delete()
        prenotazioni = pendingReservation.objects.filter(
            campo__proprietario__p_iva=self.request.user.proprietario.p_iva,
            accettato=None).order_by('data', 'ora')
        return render(request, self.template_name, {'pendingreservation_list': prenotazioni, 'form': form})

    def post(self, request):

        form = confirmReservation(request.POST)

        if form.is_valid():
            accettato = form.cleaned_data['accettato']

            pk = request.POST.get('prenotazione')

            pendingReservation.objects.filter(pk=pk).update(accettato=accettato)

            return redirect('scheduledmatch')


class reviewFied(View, PermissionRequiredMixin):
    permission_required = 'bookingFootballField.add_review'
    model = review
    template_name = 'bookingFootballField/reviewField.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=%s' % quote(request.get_full_path()))
        if not request.user.has_perm(self.permission_required):
            return redirect('home')

        form = reviewForm()
        campi = CampiDaCalcio.objects.filter(pendingreservation__cliente_id=request.user.id,
                                             pendingreservation__accettato=True).distinct()
        print(campi)
        utente = UtentiRegistrati.objects.get(pk=request.user.id)

        form.initial['utente'] = utente
        form.fields['campo'].queryset = campi
        form.fields['voto'].initial = 1
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = reviewForm(request.POST)
        info = request.POST.copy()
        valutazione = review.objects.filter(campo=info['campo'], utente_id=request.user.id)
        if valutazione.exists():
            valutazione.delete()

        fields = {}

        for field in form.fields:
            fields.setdefault(field, None)

        print('form is valid:', form.is_valid())
        if form.is_valid():
            for field in fields.keys():
                fields[field] = form.cleaned_data[field]

            review.objects.update_or_create(**fields)

            return redirect('home')
        return render(request, self.template_name, {'form': form})
