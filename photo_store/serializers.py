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


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
        )  # ниже есть второй такой же сериализатор О_о


class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = '__all__'

    def create(self, validated_data):
        topic, created = Topic.objects.get_or_create(name=validated_data['name'])
        return topic


class ExtendOrderSerializer(serializers.ModelSerializer):
    topic = TopicSerializer()
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Order
        # fields = '__all__'
        exclude = ('date_time',)

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


class ResponseSerializer(serializers.ModelSerializer):
    photographer = UserSerializer(read_only=True)
    order = ExtendOrderSerializer(read_only=True)

    class Meta:
        model = Response
        fields = ('id', 'is_selected', 'text', 'order', 'photographer')


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