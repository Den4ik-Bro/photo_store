import json
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
import django_filters
from photo_store.models import Photo, Tag
from photo_store.serializers import PhotoSerializer, UserPhotoSerializer, UserResponsePhotoSerializer
from order.models import Order, Response, Topic
from order.serializers import ExtendOrderSerializer, ResponseSerializer, TopicSerializer
from message.models import Message
from message.serializers import MessageSerializer, ShowMessageSerializer, MessageCreateSerializer
from customer.serializers import UserSerializer
from rest_framework.decorators import api_view, action
from rest_framework.response import Response as RestResponse
from rest_framework import status, filters
from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsOwnerOrReadOnly, IsOwner, IsAdminOrReadOnly


User = get_user_model()


def test_ajax(request):
    order = Order.objects.first()
    # print(model_to_dict(order))
    # response = json.dumps(model_to_dict(order), cls=DjangoJSONEncoder)
    serializer = ExtendOrderSerializer(order)
    print(type(serializer.data))
    print(serializer.data)
    return HttpResponse(json.dumps(serializer.data))


def create_ajax(request):
    # if request.is_ajax():
    # order_data = json.loads(request.body)
    # print(order_data, type(order_data))
    serializer = ExtendOrderSerializer(data=json.loads(request.body))
    if serializer.is_valid():
        serializer.save(owner=request.user)
        # Order.objects.create(
        #     text=serializer.validated_data['text'],
        #     price=serializer.validated_data['price'],
        #     start_date=serializer.validated_data['start_date'],
        #     finish_date=serializer.validated_data['finish_date'],
        #     date_time=datetime.datetime.now(),
        #     owner=request.user,
        #     topic=Topic.objects.get(pk=1)
        # )
    else:
        print(serializer.errors)
    return HttpResponse('ok')


def create_response_ajax(request, order_id):
    serializer = ResponseSerializer(data=json.loads(request.body))
    # print(serializer)
    if serializer.is_valid():
        serializer.save(photographer=request.user, order=Order.objects.get(pk=order_id))
        # Response.objects.create(
        #     text=serializer.validated_data['text'],
        #     # date_time=datetime.datetime.now(),
        #     is_selected=False,
        #     photographer=request.user,
        #     order=Order.objects.get(pk=45)
        # )
    else:
        print(serializer.errors)
    return HttpResponse('ok')


def create_message_ajax(request, pk):
    serializer = MessageSerializer(data=json.loads(request.body))
    if serializer.is_valid():
        serializer.save(sender=request.user, receiver=User.objects.get(pk=pk))
    else:
        print(serializer.errors)
    return HttpResponse(json.dumps(serializer.data))


@api_view(['GET'])
def show_message_ajax(request, pk):
    message = Message.objects.get(pk=pk)
    serialiazer = ShowMessageSerializer(message)
    return RestResponse(serialiazer.data)


@api_view(['POST'])
def create_message_api(request):
    if request.method == 'POST':
        serializer = MessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return RestResponse(serializer.data)
        else:
            return RestResponse(serializer.errors)


@api_view(['GET'])
def show_order_ajax(request, pk):
    order = Order.objects.get(pk=pk)
    serializer = ExtendOrderSerializer(order)
    return RestResponse(serializer.data)


@api_view(['GET'])
def show_order_ist_api(request):
    order = Order.objects.all()
    serializer = ExtendOrderSerializer(order, many=True)
    return RestResponse(serializer.data)


@api_view(['POST', 'PUT'])
def create_or_update_order_api(request, pk=None):
    if request.method == 'POST' or request.method == 'PUT':
        if pk:
            order = Order.objects.get(pk=pk)
            serializer = ExtendOrderSerializer(data=request.data, instance=order)
        else:
            serializer = ExtendOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return RestResponse(serializer.data)
        else:
            return RestResponse(serializer.errors)


@api_view(['GET'])
def show_photo_ajax(request, pk):
    photo = Photo.objects.get(pk=pk)
    serializer = PhotoSerializer(photo)
    return RestResponse(serializer.data)


@api_view(['POST'])
def create_photo_api(request, pk):
    if request.method == 'POST':
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return RestResponse(serializer.data)
        return RestResponse(serializer.errors)



#
#
# class ApiOrderDetailView(APIView):
#
#     def get_object(self, pk):
#         try:
#             order = Order.objects.get(pk=pk)
#         except Order.DoesNotExist:
#             raise Http404
#         return order
#
#     def get(self, request, pk):
#         order = self.get_object(pk)
#         serializer = ExtendOrderSerializer(order)
#         return RestResponse(serializer.data)
#
#     def put(self, request, pk):
#         order = self.get_object(pk)
#         serializer = ExtendOrderSerializer(order, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return RestResponse(serializer.data)
#         return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         order = self.get_object(pk)
#         order.delete()
#         return RestResponse(status=status.HTTP_204_NO_CONTENT)


# class ApiListUpdateOrderView(mixins.ListModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
#     queryset = Order.objects.all()
#     serializer_class = ExtendOrderSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#
#     def put(self, request, pk, *args, **kwargs):
#         return self.update(request, pk, *args, **kwargs)


# class ApiListUpdateOrderView(generics.RetrieveUpdateDestroyAPIView):
#     pass


# class OrderViewSet(viewsets.ViewSet):
#
#     def list(self, request):
#         orders = Order.objects.all()
#         serializer = ExtendOrderSerializer(orders, many=True)
#         return RestResponse(serializer.data)
#
#     def retrieve(self, request, pk):
#         order = Order.objects.get(pk=pk)
#         serializer = ExtendOrderSerializer(order)
#         return RestResponse(serializer.data)
#
#     def destroy(self, request, pk):
#         Order.objects.get(pk=pk).delete()
#         return RestResponse(status=status.HTTP_204_NO_CONTENT)
#
#     def update(self, request, pk):
#         order = Order.objects.get(pk=pk)
#         serializer = ExtendOrderSerializer(data=request.data, instance=order)
#         if serializer.is_valid():
#             serializer.save()
#             return RestResponse(serializer.data, status=status.HTTP_200_OK)
#         return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def partial_update(self, request, pk):
#         order = Order.objects.get(pk=pk)
#         serializer = ExtendOrderSerializer(data=request.data, instance=order, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return RestResponse(serializer.data, status=status.HTTP_200_OK)
#         return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def create(self, request):
#         serializer = ExtendOrderSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return RestResponse(serializer.data, status=status.HTTP_201_CREATED)
#         return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# order_list_view = OrderViewSet.as_view({'GET': 'list'})
# order_detail_view = OrderViewSet.as_view({'GET':'retrieve'})


class OrderApiViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = ExtendOrderSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['topic__name', ]
    permission_classes = [IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return RestResponse(serializer.data)
        return RestResponse(serializer.errors)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', 'email']

    @action(methods=['GET'], detail=True)
    def send_message_this_user(self, request, pk):
        user = User.objects.get(pk=pk)
        Message.objects.create(sender=request.user, receiver=user, text=request.data['text'])
        return RestResponse({'status':'the message has been sent'})


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = ShowMessageSerializer


class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAdminUser, IsOwner]

    @action(detail=True, methods=['GET'])
    def select_for_order(self, request, pk):
        # if request.user.has_perm()
        response = self.get_object()
        if response.order.response_set.filter(is_selected=True).exists():
            return RestResponse({'status': 'for this order response already selected'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user != response.order.owner:
            return RestResponse({'status':'вы не можете выбрать отклик к этому заказу'}, status=status.HTTP_400_BAD_REQUEST)
        response.is_selected = True
        response.save()
        return RestResponse({'status': 'response selected'})


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAdminOrReadOnly]


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer


class UserPhotoApiViewSet(viewsets.ModelViewSet):
    """Портфолио пользователя"""
    serializer_class = UserPhotoSerializer

    def get_queryset(self):
        return self.request.user.photo_set.filter(response=None)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(photographer=request.user)
            return RestResponse(serializer.data, status=status.HTTP_201_CREATED)
        return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserResponsePhotoApiViewSet(viewsets.ModelViewSet):
    """Все фотографии пользователя к заказам"""
    serializer_class = UserResponsePhotoSerializer

    def get_queryset(self):
        return self.request.user.photo_set.filter(response__isnull=False)
        # user = self.request.user
        # return user.photo_set.filter(response__photographer=user)


class UserOrderApiViewSet(viewsets.ModelViewSet):
    """Все заказы псозданные ползователем"""
    serializer_class = ExtendOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = ExtendOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return RestResponse(serializer.data, status=status.HTTP_201_CREATED)
        return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserResponseApiViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet
                             ):
    """Отклики пользователя"""
    serializer_class = ResponseSerializer

    def get_queryset(self):
        return Response.objects.filter(photographer=self.request.user)

    # @action(detail=True, methods=['GET'])
    # def is_selected(self):
    #     response = Response.objects.filter(photographer=self.request.user, is_selected=True)
    #     serializer = ResponseSerializer(response, many=True)
    #     return RestResponse(serializer.data)


class UserMessagesApiViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.CreateModelMixin,
                             viewsets.GenericViewSet
                             ):
    """Сообщения пользователя, где он либо отправитель, либо получатель"""
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user))

    @action(methods=['GET'], detail=True)
    def send_message(self, request, pk):
        message = self.get_object()
        if message.sender == request.user:
            receiver = message.receiver
        else:
            receiver = message.sender
        Message.objects.create(sender=request.user, receiver=receiver, text=request.data['text'])
        return RestResponse({'status': 'message created'})

