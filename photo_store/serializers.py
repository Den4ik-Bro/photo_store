from rest_framework import serializers


class OrderSerializer(serializers.Serializer):
    date_time = serializers.DateTimeField()
    text = serializers.CharField()
    price = serializers.IntegerField()
    start_date = serializers.DateField()
    finish_date = serializers.DateField()