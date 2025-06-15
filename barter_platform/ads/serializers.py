from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class AdSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Ad
        fields = [
            'id', 'user', 'title', 'description', 'image_url',
            'category', 'condition', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ExchangeProposalSerializer(serializers.ModelSerializer):
    ad_sender = AdSerializer(read_only=True)
    ad_receiver = AdSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = ExchangeProposal
        fields = [
            'id', 'ad_sender', 'ad_receiver', 'sender', 'receiver',
            'comment', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sender', 'receiver', 'created_at', 'updated_at']