from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from accounts.models import Proprietario
from footballFieldManagement.forms import AddFootballField, CreateEvent
from footballFieldManagement.models import CampiDaCalcio, eventi
from bookingFootballField.models import review
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.storage import FileSystemStorage
from geopy.geocoders import Here
from PrenotazioneCampi.settings import MAPS_API_ID, MAPS_APP_CODE
from django.contrib import messages


# Create your views here.

class NewFootballField(PermissionRequiredMixin, CreateView):
    permission_required = 'footballFieldManagement.add_campidacalcio'
    template_name = 'footballFieldManagement/add_ff.html'

    def get(self, request):
        prp = Proprietario.objects.get(pk=self.request.user.id).__dict__
        prp['citta'] = prp['citta'][0].upper() + prp['citta'][1:].lower()
        form = AddFootballField(initial=prp)
        return render(request, 'footballFieldManagement/add_ff.html', {'form': form})

    def post(self, request):
        maps = Here(app_id=MAPS_API_ID, app_code=MAPS_APP_CODE)

        form = AddFootballField(request.POST, request.FILES)

        fields = {}
        for field in form.fields:
            fields.setdefault(field, None)
        print('Dizionario creato:\n', fields)

        print('form is valid:', form.is_valid())
        if form.is_valid():
            for field in fields.keys():
                fields[field] = form.cleaned_data[field]

            # Anche se il form è valido potrebbe essere un indirizzo errato.
            indirizzo = fields['via'] + ' ' + str(fields['civico']) + ', ' + fields['citta'] + ' ' + str(fields['cap'])
            print(indirizzo)
            map = maps.geocode(query=indirizzo)
            print(map)
            if map is None:
                messages.warning(request, 'Errore durante la geocodifica! Riprovare!')
                return render(request, 'footballFieldManagement/add_ff.html', {'form': form})
            lng = map.longitude
            lat = map.latitude
            fields['longitudine'] = lng
            fields['latitudine'] = lat
            fields['via'] = fields['via'].upper()

            image_name = str(fields['image'])
            print(image_name)
            fs = FileSystemStorage()
            print('check image exist: ', fs.exists(image_name))
            if fs.exists(image_name):
                pass
            else:
                try:
                    print('Dentro else')
                    file = request.FILES['image']
                    fs.save(image_name, file)
                except KeyError:
                    pass

            print('Dizionario che verrà salvato in model CampiDaCalcio:\n', fields)
            try:
                campo = CampiDaCalcio(**fields)
                if campo.check_orario_lavoro():
                    campo.save()
                    prp = Proprietario.objects.get(pk=request.user.id)
                    prp.possiedeCampi.add(CampiDaCalcio.objects.get(id=campo.id))
                    return redirect('home')
                messages.error(request, 'Orario di apertura o chisura errato')
            except:
                messages.error(request, 'Impossibile aggiungere il campo!\nEsiste già un campo con questo indirizzo')
        print('stampo gli errori', form.errors)
        return render(request, 'footballFieldManagement/add_ff.html', {'form': form})


class ModifyFootballField(PermissionRequiredMixin, UpdateView):
    permission_required = 'footballFieldManagement.change_campidacalcio'
    model = CampiDaCalcio
    template_name = 'footballFieldManagement/add_ff.html'
    fields = '__all__'

    def get(self, request, pk):
        if not request.user.has_perm('footballFieldManagement.change_campidacalcio'):
            return redirect('home')
        prp = Proprietario.objects.get(pk=self.request.user.id)
        if CampiDaCalcio.objects.filter(proprietario=prp, pk=pk):
            campo = CampiDaCalcio.objects.get(pk=pk).__dict__
            campo['nomeCampo'] = campo['nomeCampo'][0].upper() + campo['nomeCampo'][1:].lower()
            campo['citta'] = campo['citta'][0] + campo['citta'][1:].lower()
            campo['via'] = campo['via'][0] + campo['via'][1:].lower()
            form = AddFootballField(initial=campo)
            # dizionario contente le informazioni sul campo attuale
            form.fields['email'].disabled = True
            form.fields['telefono'].disabled = True

            print('Informazioni campo attuali:\n', campo)
            return render(request, self.template_name, {'form': form})
        else:
            return redirect('listFF')

    def post(self, request, pk):
        maps = Here(app_id=MAPS_API_ID, app_code=MAPS_APP_CODE)
        campo = CampiDaCalcio.objects.get(pk=pk)
        value = request.POST.copy()
        value['citta'] = value['citta'].upper()
        value['via'] = value['via'].upper()
        form = AddFootballField(value, request.FILES, instance=campo)

        fields = {}
        for field in form.fields:
            fields.setdefault(field, None)
        print('Dizionario creato: ', fields)

        form.fields['email'].disabled = True
        form.fields['telefono'].disabled = True

        print('pk:', pk)
        print('form is_valid:', form.is_valid())
        if form.is_valid():
            for field in form.fields:
                fields[field] = form.cleaned_data[field]

            indirizzo = fields['via'] + ' ' + str(fields['civico']) + ', ' + fields['citta'] + ' ' + str(fields['cap'])
            print(indirizzo)
            map = maps.geocode(query=indirizzo)
            print(map)
            # Anche se il form è valido potrebbe essere un indirizzo errato.
            if map is None:
                messages.warning(request, 'Errore durante la geocodifica! Riprovare!')
                return render(request, 'footballFieldManagement/add_ff.html', {'form': form})
            lng = map.longitude
            lat = map.latitude
            fields['via'] = fields['via'].upper()
            fields['longitudine'] = lng
            fields['latitudine'] = lat

            image_name = str(fields['image'])
            fs = FileSystemStorage()
            print('check if exist image:', fs.exists(image_name))
            if fs.exists(image_name):
                pass
            else:
                try:
                    print('else')
                    file = request.FILES['image']
                    fs.save(image_name, file)
                except KeyError:
                    fields['image'] = 'default.jpg'

            print('Dizionario delle modifiche che verrà salvato in CampiDaCalcio:\n', fields)

            test = CampiDaCalcio(**fields)
            if test.check_orario_lavoro():
                CampiDaCalcio.objects.filter(pk=pk).update(**fields)
                return redirect('aboutFF', campo.pk)
            else:
                messages.error(request, 'Orario non consentito.')
        print('errori presenti nel form: ', form.errors)
        return render(request, 'footballFieldManagement/add_ff.html', {'form': form})


class DeleteFootballField(PermissionRequiredMixin, DeleteView):
    permission_required = 'footballFieldManagement.delete_campidacalcio'
    model = CampiDaCalcio
    template_name = 'footballFieldManagement/field_confirm_delete.html'

    def get(self, request, pk):
        prp = Proprietario.objects.get(pk=self.request.user.id)
        if not CampiDaCalcio.objects.filter(proprietario=prp, pk=pk).exists():
            return redirect('home')
        else:
            campo = CampiDaCalcio.objects.get(proprietario=prp, pk=pk)
            return render(request, self.template_name, {'object': campo.nomeCampo})

    success_url = reverse_lazy('home')


class ListFootballField(ListView):
    fields = '__all__'
    template_name = 'footballFieldManagement/listaCampi.html'

    def get_queryset(self):
        print(self.request.user.id)
        prp = Proprietario.objects.get(pk=self.request.user.id)
        campo = CampiDaCalcio.objects.filter(proprietario=prp)
        return campo

    def post(self, request):
        # recupero pk
        pk = request.POST.get('campo')
        if (pk == None):
            return redirect('listFF')
        return redirect('aboutFF', pk)


class AboutFootballField(DetailView):
    model = CampiDaCalcio
    template_name = 'footballFieldManagement/infoFootballField.html'

    def get(self, request, pk):
        if not request.user.has_perm('footballFieldManagement.add_campidacalcio'):
            return redirect('home')
        prp = Proprietario.objects.get(pk=self.request.user.id)
        if CampiDaCalcio.objects.filter(proprietario=prp, pk=pk):
            # dizionario contente le informazioni sul campo attuale
            campo = CampiDaCalcio.objects.get(pk=pk).__dict__
            campo['nomeCampo'] = campo['nomeCampo'][0].upper() + campo['nomeCampo'][1:].lower()
            campo['citta'] = campo['citta'][0] + campo['citta'][1:].lower()
            campo['via'] = campo['via'][0] + campo['via'][1:].lower()
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
            return redirect('listFF')


class NewEvent(PermissionRequiredMixin, CreateView):
    permission_required = 'footballFieldManagement.add_eventi'
    model = eventi
    form_class = CreateEvent
    template_name = 'footballFieldManagement/create_event.html'

    def get_form(self, form_class=CreateEvent):
        form = super(NewEvent, self).get_form(form_class)
        form.fields['organizzatore'].queryset = CampiDaCalcio.objects.filter(proprietario=self.request.user.id)
        return form

    def post(self, request):

        form = CreateEvent(request.POST, request.FILES)

        fields = {}
        for field in form.fields:
            fields.setdefault(field, None)
        print('Dizionario creato:\n', fields)

        print('stampo gli errori', form.errors)
        if form.is_valid():
            for field in fields.keys():
                fields[field] = form.cleaned_data[field]
                print(fields[field])

            image_name = str(fields['foto_evento'])
            print(image_name)
            fs = FileSystemStorage()
            print('check image exist: ', fs.exists(image_name))
            if fs.exists(image_name):
                pass
            else:
                try:
                    print('Dentro else')
                    file = request.FILES['foto_evento']
                    fs.save(image_name, file)
                except KeyError:
                    pass

            evento = eventi.objects.create(**fields)
            evento.save()

            return redirect('home')

        return render(request, 'footballFieldManagement/create_event.html', {'form': form})


class ModifyEvento(PermissionRequiredMixin, UpdateView):
    permission_required = 'footballFieldManagement.change_eventi'
    model = eventi
    form_class = CreateEvent
    template_name = 'footballFieldManagement/create_event.html'
    fields = '__all__'

    def get(self, request, pk):
        if not request.user.has_perm('footballFieldManagement.add_campidacalcio'):
            return redirect('home')
        prp = Proprietario.objects.get(pk=self.request.user.id)
        if eventi.objects.filter(pk=pk, organizzatore__proprietario=prp):
            evento = eventi.objects.get(pk=pk).__dict__
            form = CreateEvent(initial=evento)
            form.fields['organizzatore'].queryset = CampiDaCalcio.objects.filter(proprietario=prp)
            return render(request, self.template_name, {'form': form})
        else:
            redirect('home')

    def post(self, request, pk):
        evento = eventi.objects.get(pk=pk)
        form = CreateEvent(request.POST, request.FILES, instance=evento)
        fields = {}
        for field in form.fields:
            fields.setdefault(field, None)
        print('Dizionario creato:\n', fields)

        print('pk:', pk)
        print('form is_valid:', form.is_valid())
        if form.is_valid():
            for field in form.fields:
                fields[field] = form.cleaned_data[field]
            image_name = str(fields['foto_evento'])
            fs = FileSystemStorage()

            if fs.exists(image_name):
                pass
            else:
                try:
                    print('else')
                    file = request.FILES['image']
                    fs.save(image_name, file)
                    print(fs.base_location)
                except KeyError:
                    pass

            eventi.objects.filter(pk=evento.pk).update(**fields)

            return redirect('home')
        print('errori presenti nel form:', form.errors)
        return render(request, 'footballFieldManagement/create_event.html', {'form': form})


class ListEventProprietario(ListView):
    fields = '__all__'
    template_name = 'footballFieldManagement/listEvent.html'

    def get(self, request):
        if not request.user.has_perm('footballFieldManagement.change_campidacalcio'):
            return redirect('home')
        prp = Proprietario.objects.get(pk=self.request.user.id)
        evento = eventi.objects.filter(organizzatore__proprietario=prp)
        return render(request, self.template_name, {'eventi_list': evento})

    def post(self, request):
        # recupero pk
        pk = request.POST.get('evento')
        if (pk == None):
            print('None')
            return redirect('list_event')
        return redirect('about_event', pk)


class AboutEvent(DetailView):
    model = eventi
    template_name = 'footballFieldManagement/infoEvento.html'

    def get(self, request, pk):
        if not request.user.has_perm('footballFieldManagement.add_campidacalcio'):
            return redirect('home')
        prp = Proprietario.objects.get(pk=self.request.user.id)
        if eventi.objects.filter(organizzatore__proprietario=prp, pk=pk):
            evento = eventi.objects.get(pk=pk).__dict__
            organizzatore_id = evento['organizzatore_id']
            form = CreateEvent(initial=evento)
            # lng e lat per la mappa
            campo = CampiDaCalcio.objects.get(proprietario=prp, pk=organizzatore_id)
            lng = str(campo.longitudine)
            lat = str(campo.latitudine)
            return render(request, self.template_name, {'form': form, 'pk': evento['id'], 'lat': lat, 'lng': lng})
        else:
            return redirect('list_event')


class DeleteEvent(PermissionRequiredMixin, DeleteView):
    permission_required = 'footballFieldManagement.delete_eventi'
    model = eventi
    template_name = 'footballFieldManagement/field_confirm_delete.html'

    def get(self, request, pk):
        prp = Proprietario.objects.get(pk=self.request.user.id)
        if eventi.objects.filter(pk=pk, organizzatore__proprietario=prp).exists():
            evento = eventi.objects.get(pk=pk,
                                        organizzatore__proprietario=prp)
            return render(request, self.template_name, {'object': evento.titolo})
        else:
            return redirect('home')

    success_url = reverse_lazy('list_event')
