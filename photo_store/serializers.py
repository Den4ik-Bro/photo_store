from rest_framework import serializers


from .models import Order, User, Response


# class OrderSerializer(serializers.Serializer):
#     date_time = serializers.DateTimeField(read_only=True)
#     text = serializers.CharField()
#     price = serializers.IntegerField()
#     start_date = serializers.DateField()
#     finish_date = serializers.DateField()


class OrderSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('date_time',)


class ResponseSerializer(serializers.ModelSerializer):
    photographer = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())
    order = serializers.PrimaryKeyRelatedField(required=False, queryset=Order.objects.all())

    class Meta:
        model = Response
        fields = (
            'text',
        )