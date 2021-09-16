from django.forms import modelformset_factory
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models import Max, F, Avg
from .models import Order, Topic, Response, Photo, Message, Tag
from .forms import PhotoForm, InviteForm
from PIL import Image


User = get_user_model()


class OrderTest(TestCase):
    def setUp(self):
        admin = User.objects.create_user(
            username='admin',
            password='12345',
            is_photographer=True
        )
        photographer = User.objects.create_user(
            username='user',
            password='123456',
            is_photographer=True
        )
        topic = Topic.objects.create(name='свадебная')
        topic.save()
        self.order = Order.objects.create(
            owner=admin,
            text='qwerty',
            price=1000,
            is_public=True,
            topic=topic
        )
        response = Response.objects.create(
            text='asdasd',
            is_selected=True,
            order=self.order,
            photographer=photographer
        )
        self.photo_for_response = Photo.objects.create(
            image='photo/test_photo_1',
            response=response,
            photographer=photographer
        )

    def test_is_photos_on_order_page(self):
        self.client.login(username='admin', password='12345')
        server_response = self.client.get('/order/' + str(self.order.id) + '/')
        self.assertEqual(server_response.status_code, 200)
        # print(str(response.content))
        self.assertContains(server_response, self.photo_for_response.image.url)
        self.assertTrue(self.photo_for_response in server_response.context['photo_list'])
        self.assertTemplateUsed(server_response, 'order_info.html')

    def test_orders_view(self):
        self.client.login(username='admin', password='12345')
        server_response = self.client.get('/orders/')
        self.assertEqual(server_response.status_code, 200)


class ProfileTest(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(
            username='test1',
            password='test123',
            is_photographer=True
        )

        self.user_2 = User.objects.create_user(
            username='test2',
            password='test12345',
            is_photographer=True
        )

        self.tag1 = Tag.objects.create(name='test')
        self.tag2 = Tag.objects.create(name='test_test')

        self.photo = Photo.objects.create(
            image='photo/test_photo_1',
            photographer=self.user_1,
        )
        self.photo.tags.add(self.tag2, self.tag1)

        topic = Topic.objects.create(name='test')

        order_1 = Order.objects.create(
            topic=topic,
            owner=self.user_1,
            price=1000,
            is_public=True,
        )

        order_2 = Order.objects.create(
            topic=topic,
            owner=self.user_2,
            price=2000,
            is_public=True,
        )

        response = Response.objects.create(
            order=order_2,
            photographer=self.user_1,
            is_selected=False
        )

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

        self.InviteFormSet = modelformset_factory(User, InviteForm, extra=0)
        self.form_set = self.InviteFormSet(queryset=User.objects.filter(is_photographer=True)
                                 .exclude(pk=self.user_1.id)
                                 .annotate(avg_rate=Avg('response__rate')), form_kwargs={'owner': self.user_1.id})

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
        x = self.user_1.sent_messages.filter(
            id__in=self.user_1.sent_messages.order_by().values('receiver').annotate(last_id=Max('id')).values_list('last_id',
                                                                                                              flat=True))

    # def test_photo_append(self):
    #     image = Image.open('media/test/test_test.jpg')
    #     form = PhotoForm()
    #     form['image'] = image
    #     form['description'] = 'dfdgfd'
    #     self.client.login(username='test1', password='test123')
    #     self.client.post('/profile/' + str(self.user_1.id) + '/', date=form)

    def test_main_views(self):
        server_response = self.client.get('')
        self.assertEqual(server_response.status_code, 200)
        self.assertTemplateUsed('main.html')

    def test_message_view(self):
        self.client.login(username='test1', password='test123')
        message = Message.objects.create(
            sender=self.user_1,
            receiver=self.user_2,
            text='sdfsd'
        )
        server_response = self.client.get('/message/' + str(message.receiver.id) + '/')
        self.assertEqual(server_response.status_code, 200)

    def test_photo_view(self):
        self.client.login(username='test1', password='test123')
        server_response = self.client.get('/photo_view/' + str(self.photo.id) + '/')
        self.assertEqual(server_response.status_code, 200)
        for tag in self.photo.tags.all():
            self.assertContains(server_response, tag.name)

    def test_photographers(self):
        self.client.login(username='test1', password='test123')
        server_response = self.client.get('/photographers/')
        self.assertEqual(server_response.status_code, 200)
        self.assertTemplateUsed('photographers.html')
        self.assertTrue(self.form_set in server_response.context['form_set'])
