from rest_framework import serializers


from .models import Order, User, Response, Message, Topic


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
        fields = '__all__'
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


class ExtendOrderSerializer(serializers.ModelSerializer):
    # topic = TopicSerializer()

    class Meta:
        model = Order
        fields = '__all__'