from django.urls import path
from .views import SearchResult, ListSearch, ListSearchBaseResult

urlpatterns = [
    path('search', SearchResult.as_view(), name='search'),
    path('searchBase', ListSearchBaseResult.as_view(), name='searchBase'),
    path('search_result', ListSearch.as_view(), name='search_result'),
]
