from django.urls import path
from .views import StoreView, StoreFAQListCreateView, StoreFAQDetailView

urlpatterns = [
    path("store/", StoreView.as_view(), name="store-detail"),
    path("store/faqs/", StoreFAQListCreateView.as_view(), name="store-faqs"),
    path("store/faqs/<int:pk>/", StoreFAQDetailView.as_view(), name="store-faq-detail"), 
]
