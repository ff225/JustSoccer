from django.urls import path
from footballFieldManagement.views import NewFootballField, ListFootballField, ModifyFootballField, \
    AboutFootballField, DeleteFootballField, NewEvent, ListEventProprietario, AboutEvent, ModifyEvento, DeleteEvent
from bookingFootballField.views import ListAcceptedReservationPrp, ListPendingReservationPrp, ListScheduledMatchesPrp

# TODO utilizzare nomi più pertinenti
urlpatterns = [
    path('bookinghistory', ListAcceptedReservationPrp.as_view(), name='bhistoryprp'),
    path('pendingreservation', ListPendingReservationPrp.as_view(), name='pendingreservationPRP'),
    path('scheduledmatch', ListScheduledMatchesPrp.as_view(), name='scheduledmatch'),
    path('newFF', NewFootballField.as_view(), name='newFF'),
    path('listFF', ListFootballField.as_view(), name='listFF'),
    path('modifyFF/<int:pk>', ModifyFootballField.as_view(), name='modifyFF'),
    path('aboutFF/<int:pk>', AboutFootballField.as_view(), name='aboutFF'),
    path('deleteFF/<int:pk>', DeleteFootballField.as_view(), name='deleteFF'),
    path('newEvent', NewEvent.as_view(), name='newEvent'),
    path('listEvent', ListEventProprietario.as_view(), name='list_event'),
    path('aboutEvent/<int:pk>', AboutEvent.as_view(), name='about_event'),
    path('modifyEvent/<int:pk>', ModifyEvento.as_view(), name='modify_event'),
    path('deleteEvent/<int:pk>', DeleteEvent.as_view(), name='delete_event'),
]
