from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models import Max, F
from .models import Order, Topic, Response, Photo, Message


User = get_user_model()


class OrderTest(TestCase):
    def setUp(self):
        admin = User.objects.create_user(
            username='admin',
            password='12345'
        )
        admin.save()
        photographer = User.objects.create_user(
            username='user',
            password='123456',
            is_photographer=True
        )
        photographer.save()
        topic = Topic.objects.create(name='свадебная')
        topic.save()
        self.order = Order.objects.create(
            owner=admin,
            text='qwerty',
            price=1000,
            is_public=True,
            topic=topic
        )
        self.order.save()
        response = Response.objects.create(
            text='asdasd',
            is_selected=True,
            order=self.order,
            photographer=photographer
        )
        response.save()
        self.photo_for_response = Photo.objects.create(
            image='photo/test_photo_1',
            response=response,
            photographer=photographer
        )
        self.photo_for_response.save()

    def test_is_photos_on_order_page(self):
        self.client.login(username='admin', password='12345')
        server_response = self.client.get('/order/' + str(self.order.id) + '/')
        self.assertEqual(server_response.status_code, 200)
        # print(str(response.content))
        self.assertContains(server_response, self.photo_for_response.image.url)
        self.assertTrue(self.photo_for_response in server_response.context['photo_list'])
        self.assertTemplateUsed(server_response, 'order_info.html')


class ProfileTest(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(
            username='test1',
            password='test123',
            is_photographer=True
        )
        self.user_1.save()

        self.user_2 = User.objects.create_user(
            username='test2',
            password='test12345',
            is_photographer=True
        )

        self.photo = Photo.objects.create(
            image='photo/test_photo_1',
            photographer=self.user_1
        )
        self.photo.save()

        topic = Topic.objects.create(name='test')
        topic.save()

        order_1 = Order.objects.create(
            topic=topic,
            owner=self.user_1,
            price=1000,
            is_public=True,
        )
        order_1.save()

        order_2 = Order.objects.create(
            topic=topic,
            owner=self.user_2,
            price=2000,
            is_public=True,
        )
        order_2.save()

        response = Response.objects.create(
            order=order_2,
            photographer=self.user_1,
            is_selected=False
        )
        response.save()

        Message.objects.create(
            sender=self.user_1,
            receiver=self.user_2,
            text='sadas',
        )

        Message.objects.create(
            sender=self.user_2,
            receiver=self.user_1,
            text='sadsdfdsf',
        )

        Message.objects.create(
            sender=self.user_1,
            receiver=self.user_2,
            text='qwerty',
        )

        Message.objects.create(
            sender=self.user_2,
            receiver=self.user_1,
            text='bvnnbmnbm',
        )

    def test_view_profile(self):
        self.client.login(username='test1', password='test123')
        server_response = self.client.get('/profile/' + str(self.user_1.id) + '/')
        self.assertEqual(server_response.status_code, 200)
        self.assertEqual(self.user_1, server_response.context['user'])
        self.assertTemplateUsed(server_response, 'profile.html')
        self.assertContains(server_response, self.photo.image.url)
        self.assertContains(server_response, self.user_1.first_name)
        self.assertContains(server_response, self.user_1.last_name)
        self.assertContains(server_response, self.user_1.email)
        for order in self.user_1.order_set.all():
            self.assertContains(server_response, order)
        for response in self.user_1.response_set.all():
            self.assertContains(server_response, response)
        # user_messages = self.user_1.sent_messages\
        #     .annotate(last_date=Max('date_time')).filter(date_time=F('last_date')) #+ self.user_1.received_messages.all()
        # print(user_messages)