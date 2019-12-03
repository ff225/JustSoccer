from django.urls import path, include
from accounts.views import profile, RegUserView, RegOwnerView, EditProfileOwnerView, EditProfileUserView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('registration', RegUserView.as_view(), name='newUser'),
    path('registration/owner', RegOwnerView.as_view(), name='newOwner'),
    path('profile', login_required(profile), name='profile'),
    path('profile/edit', login_required(EditProfileUserView.as_view()), name='editProfileUt'),
    path('profile/editowner', login_required(EditProfileOwnerView.as_view()), name='editProfileOw'),

]
