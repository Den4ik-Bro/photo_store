from rest_framework import serializers
from .models import Topic, Order, Response
from customer.serializers import UserSerializer


class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = '__all__'

    def create(self, validated_data):
        topic, created = Topic.objects.get_or_create(name=validated_data['name'])
        return topic


class ExtendOrderSerializer(serializers.ModelSerializer):
    topic = serializers.StringRelatedField()
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Order
        exclude = ('id',)

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