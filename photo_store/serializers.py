from django.contrib.auth import get_user_model
from rest_framework import serializers


from .models import Order, Response, Message, Topic, Photo, Tag

User = get_user_model()


# class OrderSerializer(serializers.Serializer):
#     date_time = serializers.DateTimeField(read_only=True)
#     text = serializers.CharField()
#     price = serializers.IntegerField()
#     start_date = serializers.DateField()
#     finish_date = serializers.DateField()


class OrderSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=User.objects.all()
    )

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('date_time',)


class ResponseSerializer(serializers.ModelSerializer):
    photographer = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=User.objects.all()
    )
    order = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=Order.objects.all()
    )

    class Meta:
        model = Response
        fields = ('text', 'order', 'photographer')
        read_only_fields = ('datetime',)


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=User.objects.all()
    )
    receiver = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=User.objects.all()
    )

    class Meta:
        model = Message
        fields = (
            'sender',
            'receiver',
            'text',
            'date_time'
        )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class ShowMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Message
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = '__all__'

    def create(self, validated_data):
        topic, created = Topic.objects.get_or_create(name=validated_data['name'])
        return topic


class ExtendOrderSerializer(serializers.ModelSerializer):
    topic = TopicSerializer()
    owner = UserSerializer()

    class Meta:
        model = Order
        # exclude = ('owner',)
        fields = '__all__'
        read_only_fields = ('owner',)

    def create(self, validated_data):
        print('before', validated_data)
        topic_data = validated_data.pop('topic')
        print('after', validated_data, topic_data)
        topic_serializer = TopicSerializer(data=topic_data)
        if topic_serializer.is_valid():
            topic = topic_serializer.save()

        order = Order.objects.create(**validated_data, topic=topic)
        return order

    def update(self, instance, validated_data):
        if 'topic' in validated_data:
            validated_data.pop('topic')
        return super().update(instance, validated_data)


class MessageCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

    def create(self, validated_data):
        tag, create = Tag.objects.get_or_create(name=validated_data['name'])
        return tag


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )


class PhotoSerializer(serializers.ModelSerializer):
    photographer = UserSerializer(read_only=True)
    tags = TagSerializer()

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