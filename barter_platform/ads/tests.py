from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Ad, ExchangeProposal


class AdModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_ad_creation(self):
        ad = Ad.objects.create(
            user=self.user,
            title='Test Ad',
            description='Test description',
            category='electronics',
            condition='new'
        )
        self.assertEqual(ad.title, 'Test Ad')
        self.assertEqual(ad.user, self.user)
        self.assertEqual(str(ad), 'Test Ad')


class AdViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.ad = Ad.objects.create(
            user=self.user,
            title='Test Ad',
            description='Test description',
            category='electronics',
            condition='new'
        )

    def test_ad_list_view(self):
        response = self.client.get(reverse('ad_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ad')

    def test_ad_detail_view(self):
        response = self.client.get(reverse('ad_detail', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ad')

    def test_ad_create_requires_login(self):
        response = self.client.get(reverse('ad_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_ad_create_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ad_create'))
        self.assertEqual(response.status_code, 200)

    def test_ad_edit_only_owner(self):
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('ad_edit', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect with error


class ExchangeProposalTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )

        self.ad1 = Ad.objects.create(
            user=self.user1,
            title='Ad 1',
            description='Description 1',
            category='electronics',
            condition='new'
        )

        self.ad2 = Ad.objects.create(
            user=self.user2,
            title='Ad 2',
            description='Description 2',
            category='books',
            condition='used'
        )

    def test_proposal_creation(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Test exchange'
        )
        self.assertEqual(proposal.status, 'pending')
        self.assertEqual(proposal.sender, self.user1)
        self.assertEqual(proposal.receiver, self.user2)

    def test_proposal_unique_constraint(self):
        ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='First proposal'
        )

        # Try to create duplicate proposal
        with self.assertRaises(Exception):
            ExchangeProposal.objects.create(
                ad_sender=self.ad1,
                ad_receiver=self.ad2,
                comment='Second proposal'
            )