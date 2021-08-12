from django.test import TestCase
from django.contrib.auth import get_user_model

from photo_store.models import Order, Topic, Response, Photo

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

        user_2 = User.objects.create_user(
            username='test2',
            password='test12345',
            is_photographer=True
        )
        user_2.save()

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
            owner=user_2,
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

    def test_view_profile(self):
        self.client.login(username='test1', password='test123')
        server_response = self.client.get('/profile/' + str(self.user_1.id) + '/')
        self.assertEqual(server_response.status_code, 200)
        self.assertTrue(self.photo in self.user_1.photo_set.filter(photographer=self.user_1))
        self.assertTemplateUsed(server_response, 'profile.html')
