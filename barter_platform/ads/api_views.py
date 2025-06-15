from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import Ad, ExchangeProposal
from .serializers import AdSerializer, ExchangeProposalSerializer


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'condition', 'user']
    search_fields = ['title', 'description']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        ad = self.get_object()
        if ad.user != request.user:
            return Response(
                {'error': 'Вы можете редактировать только свои объявления'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        ad = self.get_object()
        if ad.user != request.user:
            return Response(
                {'error': 'Вы можете удалять только свои объявления'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_ads(self, request):
        """Получить объявления текущего пользователя"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Требуется авторизация'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        ads = self.queryset.filter(user=request.user)
        page = self.paginate_queryset(ads)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(ads, many=True)
        return Response(serializer.data)


class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'ad_sender__user', 'ad_receiver__user']

    def get_queryset(self):
        # Пользователь видит только свои предложения
        return self.queryset.filter(
            models.Q(ad_sender__user=self.request.user) |
            models.Q(ad_receiver__user=self.request.user)
        )

    def create(self, request, *args, **kwargs):
        ad_sender_id = request.data.get('ad_sender_id')
        ad_receiver_id = request.data.get('ad_receiver_id')

        if not ad_sender_id or not ad_receiver_id:
            return Response(
                {'error': 'Необходимо указать ID объявлений отправителя и получателя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ad_sender = Ad.objects.get(id=ad_sender_id, user=request.user)
            ad_receiver = Ad.objects.get(id=ad_receiver_id)
        except Ad.DoesNotExist:
            return Response(
                {'error': 'Объявление не найдено'},
                status=status.HTTP_404_NOT_FOUND
            )

        if ad_receiver.user == request.user:
            return Response(
                {'error': 'Нельзя создать предложение для своего объявления'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем существующие предложения
        if ExchangeProposal.objects.filter(
                ad_sender=ad_sender,
                ad_receiver=ad_receiver
        ).exists():
            return Response(
                {'error': 'Предложение уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        proposal = ExchangeProposal.objects.create(
            ad_sender=ad_sender,
            ad_receiver=ad_receiver,
            comment=request.data.get('comment', '')
        )

        serializer = self.get_serializer(proposal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        proposal = self.get_object()

        # Только получатель может изменять статус
        if proposal.ad_receiver.user != request.user:
            return Response(
                {'error': 'Только получатель может изменить статус предложения'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Разрешаем изменять только статус
        allowed_fields = ['status']
        data = {k: v for k, v in request.data.items() if k in allowed_fields}

        serializer = self.get_serializer(proposal, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Получить отправленные предложения"""
        proposals = self.get_queryset().filter(ad_sender__user=request.user)
        page = self.paginate_queryset(proposals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(proposals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def received(self, request):
        """Получить полученные предложения"""
        proposals = self.get_queryset().filter(ad_receiver__user=request.user)
        page = self.paginate_queryset(proposals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(proposals, many=True)
        return Response(serializer.data)