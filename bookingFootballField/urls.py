from django.urls import path
from .views import ReserveField, AboutFootballField, \
    ListPendingReservationUt, ListAcceptedReservationUt, DeletePendingReservationUt, ListEventUt, reviewFied, Payment, \
    ListScheduledMatchesUt

# TODO utilizzare nomi più pertinenti
urlpatterns = [
    path('about/<int:pk>', AboutFootballField.as_view(), name='about_pitch'),
    path('review', reviewFied.as_view(), name='review'),
    path('reservation/attesa', ListPendingReservationUt.as_view(), name='reservation_attesa'),
    path('reservation/scheduledmatch', ListScheduledMatchesUt.as_view(), name='nextmatch'),
    path('reservation/accepted', ListAcceptedReservationUt.as_view(), name='reservation_accepted'),
    path('eventi_disponibili', ListEventUt.as_view(), name='eventi_disponibili'),
    path('delete/<int:pk>', DeletePendingReservationUt.as_view(), name='delete_r'),
    path('checkout/<int:pk>', ReserveField.as_view(), name='reserve'),
    path('checkout/confirm/<int:pk>', Payment.as_view(), name='payament')

]
