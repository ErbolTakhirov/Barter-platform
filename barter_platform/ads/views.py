from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm, SearchForm


def ad_list(request):
    """Список всех объявлений с поиском и фильтрацией"""
    ads = Ad.objects.all()
    form = SearchForm(request.GET)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        condition = form.cleaned_data.get('condition')

        if query:
            ads = ads.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )

        if category:
            ads = ads.filter(category=category)

        if condition:
            ads = ads.filter(condition=condition)

    paginator = Paginator(ads, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'ads/ad_list.html', context)


def ad_detail(request, pk):
    """Детальная страница объявления"""
    ad = get_object_or_404(Ad, pk=pk)
    user_ads = []

    if request.user.is_authenticated:
        user_ads = Ad.objects.filter(user=request.user).exclude(pk=pk)

    context = {
        'ad': ad,
        'user_ads': user_ads,
    }
    return render(request, 'ads/ad_detail.html', context)


@login_required
def ad_create(request):
    """Создание нового объявления"""
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            messages.success(request, 'Объявление успешно создано!')
            return redirect('ad_detail', pk=ad.pk)
    else:
        form = AdForm()

    return render(request, 'ads/ad_form.html', {
        'form': form,
        'title': 'Создать объявление'
    })


@login_required
def ad_edit(request, pk):
    """Редактирование объявления"""
    ad = get_object_or_404(Ad, pk=pk)

    if ad.user != request.user:
        messages.error(request, 'Вы можете редактировать только свои объявления!')
        return redirect('ad_detail', pk=pk)

    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление успешно обновлено!')
            return redirect('ad_detail', pk=pk)
    else:
        form = AdForm(instance=ad)

    return render(request, 'ads/ad_form.html', {
        'form': form,
        'title': 'Редактировать объявление',
        'ad': ad
    })


@login_required
def ad_delete(request, pk):
    """Удаление объявления"""
    ad = get_object_or_404(Ad, pk=pk)

    if ad.user != request.user:
        messages.error(request, 'Вы можете удалять только свои объявления!')
        return redirect('ad_detail', pk=pk)

    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Объявление успешно удалено!')
        return redirect('ad_list')

    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})


@login_required
@require_POST
def create_proposal(request, pk):
    """Создание предложения обмена"""
    receiver_ad = get_object_or_404(Ad, pk=pk)
    sender_ad_id = request.POST.get('sender_ad_id')
    comment = request.POST.get('comment', '')

    if not sender_ad_id:
        messages.error(request, 'Выберите товар для обмена!')
        return redirect('ad_detail', pk=pk)

    sender_ad = get_object_or_404(Ad, pk=sender_ad_id, user=request.user)

    # Проверяем, что не создаем предложение самому себе
    if receiver_ad.user == request.user:
        messages.error(request, 'Нельзя создать предложение обмена для своего товара!')
        return redirect('ad_detail', pk=pk)

    # Проверяем, нет ли уже такого предложения
    existing_proposal = ExchangeProposal.objects.filter(
        ad_sender=sender_ad,
        ad_receiver=receiver_ad
    ).first()

    if existing_proposal:
        messages.warning(request, 'Предложение обмена уже существует!')
        return redirect('ad_detail', pk=pk)

    # Создаем новое предложение
    ExchangeProposal.objects.create(
        ad_sender=sender_ad,
        ad_receiver=receiver_ad,
        comment=comment
    )

    messages.success(request, 'Предложение обмена отправлено!')
    return redirect('ad_detail', pk=pk)


@login_required
def proposal_list(request):
    """Список предложений обмена пользователя"""
    # Предложения, которые пользователь отправил
    sent_proposals = ExchangeProposal.objects.filter(
        ad_sender__user=request.user
    )

    # Предложения, которые пользователь получил
    received_proposals = ExchangeProposal.objects.filter(
        ad_receiver__user=request.user
    )

    context = {
        'sent_proposals': sent_proposals,
        'received_proposals': received_proposals,
    }
    return render(request, 'ads/proposal_list.html', context)


@login_required
@require_POST
def update_proposal_status(request, pk):
    """Обновление статуса предложения обмена"""
    proposal = get_object_or_404(ExchangeProposal, pk=pk)
    new_status = request.POST.get('status')

    # Только получатель может изменять статус
    if proposal.ad_receiver.user != request.user:
        messages.error(request, 'Вы не можете изменить статус этого предложения!')
        return redirect('proposal_list')

    if new_status in ['accepted', 'rejected']:
        proposal.status = new_status
        proposal.save()

        status_text = 'принято' if new_status == 'accepted' else 'отклонено'
        messages.success(request, f'Предложение обмена {status_text}!')

    return redirect('proposal_list')


@login_required
def my_ads(request):
    """Объявления текущего пользователя"""
    ads = Ad.objects.filter(user=request.user)
    paginator = Paginator(ads, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ads/my_ads.html', {'page_obj': page_obj})