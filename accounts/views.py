from django.shortcuts import render, redirect
from django.views.generic import CreateView, View
from .models import UtentiRegistrati, Proprietario
from .forms import RegUtente, RegProprietario, editUtente, editProprietario
from footballFieldManagement.models import CampiDaCalcio
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.contrib.auth import authenticate, login


# Create your views here.
@login_required()
def profile(request):
    return render(request, 'accounts/profile.html')


class RegUserView(CreateView):
    template_name = 'accounts/registrati.html'
    form_class = RegUtente

    def post(self, request):
        form = RegUtente(request.POST)
        fields = {}
        for field in form.fields:
            fields.setdefault(field, None)

        print('Dizionario form pronto:', fields)
        print('form is valid:', form.is_valid())
        if form.is_valid():
            for field in fields.keys():
                fields[field] = form.cleaned_data[field]

            fields.pop('password2')
            fields['citta'] = fields['citta'].upper()
            password = fields.pop('password1')

            user = UtentiRegistrati.objects.create(**fields)
            user.set_password(password)
            user.user_permissions.add(Permission.objects.get(name='Can add Prenotazione in attesa'),
                                      Permission.objects.get(name='Can delete Prenotazione in attesa'),
                                      Permission.objects.get(name='Can add Recensione'), )
            user.save()

            ut = authenticate(request, username=fields['username'], password=password)
            login(request, ut)
            return redirect('home')

        print('stampo gli errori', form.errors)
        return render(request, 'accounts/registrati.html', {'form': form})


class EditProfileUserView(View):
    template_name = 'accounts/modifica.html'

    def get(self, request):

        ut = UtentiRegistrati.objects.get(pk=request.user.id).__dict__
        ut['citta'] = ut['citta'][0] + ut['citta'][1:].lower()
        form = editUtente(initial=ut)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        print('Dentro post editUtente')
        data = UtentiRegistrati.objects.get(pk=request.user.id)

        form = editUtente(request.POST, instance=data, pk=data.pk)
        fields = {}
        for field in form.fields:
            fields.setdefault(field, None)
        fields.pop('password')

        print('Dizionario pronto:', fields)
        print('form is valid:', form.is_valid())
        if form.is_valid():
            for field in fields.keys():
                fields[field] = form.cleaned_data[field]
            fields['citta'] = fields['citta'].upper()
            print(fields)
            UtentiRegistrati.objects.filter(pk=data.pk).update(**fields)

            return redirect('profile')

        print('stampo gli errori', form.errors)
        return render(request, 'accounts/modifica.html', {'form': form})


class RegOwnerView(CreateView):
    template_name = 'accounts/registrati.html'
    form_class = RegProprietario

    def post(self, request):
        form = RegProprietario(request.POST)

        fields = {}
        for field in form.fields:
            fields.setdefault(field, None)
        print('Dizionario form pronto:', fields)

        print('form is valid:', form.is_valid())
        if form.is_valid():
            for field in fields.keys():
                fields[field] = form.cleaned_data[field]

            fields['citta'] = fields['citta'].upper()
            fields.pop('password2')
            password = fields.pop('password1')

            prp = Proprietario.objects.create(**fields)
            prp.set_password(password)
            prp.user_permissions.add(Permission.objects.get(name='Can add Campo da calcio'),
                                     Permission.objects.get(name='Can change Campo da calcio'),
                                     Permission.objects.get(name='Can delete Campo da calcio'),
                                     Permission.objects.get(name='Can add Evento'),
                                     Permission.objects.get(name='Can delete Evento'),
                                     Permission.objects.get(name='Can change Evento'),
                                     Permission.objects.get(name='Can change Prenotazione in attesa'), )

            prp.save()
            ut = authenticate(request, username=fields['username'], password=password)
            login(request, ut)
            return redirect('home')

        print('stampo gli errori:', form.errors)
        return render(request, 'accounts/registrati.html', {'form': form})


class EditProfileOwnerView(View):
    template_name = 'accounts/modifica.html'

    def get(self, request):
        proprietario = Proprietario.objects.get(pk=request.user.id).__dict__
        citta = proprietario['citta'][0] + proprietario['citta'][1:].lower()
        form = editProprietario(initial=proprietario)
        form.initial['citta'] = citta
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        prp = Proprietario.objects.get(pk=request.user.id)
        form = editProprietario(request.POST, instance=prp, pk=prp.pk)

        fields = {}
        for field in form.fields:
            fields.setdefault(field, None)
        print('Dizionario pronto:', fields)

        print('form is valid:', form.is_valid())
        if form.is_valid():
            for field in fields.keys():
                fields[field] = form.cleaned_data[field]

            fields['citta'] = fields['citta'].upper()

            Proprietario.objects.filter(pk=prp.pk).update(**fields)
            CampiDaCalcio.objects.filter(proprietario=prp).update(
                email=fields['email'], telefono=fields['telefono'])

            return redirect('profile')
        else:
            print('stampo gli errori', form.errors)
            return render(request, 'accounts/modifica.html', {'form': form})
