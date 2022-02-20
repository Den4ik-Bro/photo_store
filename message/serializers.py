from django.contrib.auth import get_user_model
from rest_framework import serializers
from customer.serializers import UserSerializer
from .models import Message

user = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    # sender = serializers.PrimaryKeyRelatedField(
    #     required=False,
    #     queryset=User.objects.all()
    # )
    # receiver = serializers.PrimaryKeyRelatedField(
    #     required=False,
    #     queryset=User.objects.all()
    # )
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Message
        exclude = ('response',)


class ShowMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer()

    class Meta:
        model = Message
        fields = '__all__'

    # def create(self, validated_data):
    #     message = Message.objects.create(receiver=self.receiver, **validated_data)
    #     return message


class MessageCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'
