from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Photo, Tag
from message.models import Message
from order.models import *
from customer.serializers import UserSerializer
from order.serializers import ResponseSerializer


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

    def create(self, validated_data):
        tag, create = Tag.objects.get_or_create(name=validated_data['name'])
        return tag


class PhotoSerializer(serializers.ModelSerializer):
    photographer = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True)

    class Meta:
        model = Photo
        fields = '__all__'

    def create(self, validated_data):
        tag_data = validated_data.pop('name')
        tag_serializer = TagSerializer(data=tag_data)
        if tag_serializer.is_valid():
            tag = tag_serializer.save()

        photo = Photo.objects.create(**validated_data, tags=tag)
        return photo

    def update(self, instance, validated_data):
        instance.tags = validated_data['tags']
        instance.save()
        return instance


class UserPhotoSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True)
    photographer = UserSerializer(read_only=True)

    class Meta:
        model = Photo
        fields = '__all__'


class ShowUserMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'


class UserResponsePhotoSerializer(serializers.ModelSerializer):
    response = ResponseSerializer(read_only=True)
    tags = TagSerializer(read_only=True, required=False)

    class Meta:
        model = Photo
        fields = '__all__'