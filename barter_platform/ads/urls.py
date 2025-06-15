from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import AdViewSet, ExchangeProposalViewSet

# API Router
router = DefaultRouter()
router.register(r'ads', AdViewSet)
router.register(r'proposals', ExchangeProposalViewSet)

urlpatterns = [
    # Web views
    path('', views.ad_list, name='ad_list'),
    path('ad/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ad/create/', views.ad_create, name='ad_create'),
    path('ad/<int:pk>/edit/', views.ad_edit, name='ad_edit'),
    path('ad/<int:pk>/delete/', views.ad_delete, name='ad_delete'),
    path('ad/<int:pk>/propose/', views.create_proposal, name='create_proposal'),
    path('proposals/', views.proposal_list, name='proposal_list'),
    path('proposal/<int:pk>/update/', views.update_proposal_status, name='update_proposal_status'),
    path('my-ads/', views.my_ads, name='my_ads'),

    # API endpoints
    path('api/', include(router.urls)),
]