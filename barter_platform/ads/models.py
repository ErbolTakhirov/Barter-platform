from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Ad(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/у'),
        ('damaged', 'С дефектами'),
    ]

    CATEGORY_CHOICES = [
        ('electronics', 'Электроника'),
        ('clothing', 'Одежда'),
        ('books', 'Книги'),
        ('home', 'Для дома'),
        ('sports', 'Спорт'),
        ('toys', 'Игрушки'),
        ('other', 'Другое'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image_url = models.URLField(blank=True, null=True, verbose_name='URL изображения')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Категория')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, verbose_name='Состояние')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ad_detail', kwargs={'pk': self.pk})


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]

    ad_sender = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='sent_proposals',
        verbose_name='Объявление отправителя'
    )
    ad_receiver = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='received_proposals',
        verbose_name='Объявление получателя'
    )
    comment = models.TextField(verbose_name='Комментарий')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Предложение обмена'
        verbose_name_plural = 'Предложения обмена'
        ordering = ['-created_at']
        unique_together = ['ad_sender', 'ad_receiver']

    def __str__(self):
        return f'Обмен: {self.ad_sender.title} -> {self.ad_receiver.title}'

    @property
    def sender(self):
        return self.ad_sender.user

    @property
    def receiver(self):
        return self.ad_receiver.user