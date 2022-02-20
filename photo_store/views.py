from django.shortcuts import redirect, reverse
from .forms import PhotoForm, TagForm
from django.contrib.auth import get_user_model
from django.views import generic
from .models import Photo, Tag
from order.models import Order, Response, Topic



User = get_user_model()


class MainView(generic.TemplateView):
    template_name = 'main.html'


class PhotoCreateView(generic.CreateView):
    model = User

    def post(self, request, *args, **kwargs):
        photo_form = PhotoForm(request.POST, request.FILES)
        if photo_form.is_valid():
            photo = photo_form.save(commit=False)
            photo.photographer = self.request.user
            photo.save()
            return redirect(reverse('customer:show_profile', kwargs={'pk': self.request.user.id}))


class DeletePhotoView(generic.DeleteView):
    model = Photo

    def get_success_url(self):
        return reverse('customer:show_profile', kwargs={'pk': self.request.user.id})

    def get(self, request, pk):
        return self.post(request, pk)


class CreateResponsePhoto(generic.CreateView):
    model = Photo
    template_name = 'order_info.html'

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        photo_form = PhotoForm(request.POST, request.FILES)
        if photo_form.is_valid():
            photo = photo_form.save(commit=False)
            photo.photographer = self.request.user
            for response in order.response_set.all():  # перебираем респонсы что бы вытащить тот где is_selected = True
                if response.is_selected == True:
                    photo.response = response
            photo.save()
            return redirect(reverse('order:order', kwargs={'pk': order.id}))


class PhotoDetailView(generic.DetailView):
    model = Photo
    template_name = 'photo_view.html'

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = TagForm()
        return context


class TagCreateView(generic.CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'photo_view.html'

    def post(self, request, photo_id):
        form = self.form_class(request.POST)
        photo = Photo.objects.get(pk=photo_id)
        if form.is_valid():
            # tag = form.save()
            tag, created = Tag.objects.get_or_create(name=form.cleaned_data['name'])
            tag.photo_set.add(photo)
        return redirect(reverse('photo_store:photo_view', kwargs={'pk': photo_id}))


class TagPhotoDetailView(generic.DetailView):
    model = Tag
    template_name = 'tag_photos.html'
    context_object_name = 'tag'




