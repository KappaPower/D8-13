from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from .models import Post, Comment, Author, Category, UserCategory, PostCategory, User
from .filters import PostFilter
from .forms import PostForm, UserForm
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import render, reverse, redirect
from django.views import View
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.http import HttpResponse
from .tasks import *
from django.core.cache import cache #импортируем наш кэш

from django.views.decorators.cache import cache_page # импортируем декоратор для кэширования отдельного представления

# Если у вас есть в проекте представления (views), оформленные через функции, тогда кэширование будет выполняться очень просто.
# @cache_page(100) # в аргументы к декоратору передаём количество секунд, которые хотим, чтобы страница держалась в кэше. Внимание! Пока страница находится в кэше, изменения, происходящие на ней, учитываться не будут!
# def my_view(request):
#     ...

class PostList(ListView):
    model = Post
    ordering = '-creation_date'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10  # вот так мы можем указать количество записей на странице


class ArticleList(PostList):
    template_name = 'article.html'


class PostDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'

    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'post-{self.kwargs["pk"]}',
                        None)  # кэш очень похож на словарь, и метод get действует также. Он забирает значение по ключу, если его нет, то забирает None.

        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            # obj = super().get_object(queryset=kwargs['queryset'])
            cache.set(f'post-{self.kwargs["pk"]}', obj)

        return obj

    def create_post(request):
        if request.method == 'POST':
            form = PostForm(request.POST)
            form.save()
            return HttpResponseRedirect('//')
        form = PostForm()
        return render(request, 'news_edit.html', {'form': form})


class PostSearch(ListView):
    template_name = 'search.html'
    context_object_name = 'post'
    queryset = Post.objects.all()

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self,
                         **kwargs):  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса (привет, полиморфизм, мы скучали!!!)
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET,
                                       queryset=self.get_queryset())  # вписываем наш фильтр в контекст
        context['categories'] = Category.objects.all()
        context['form'] = PostForm

        return context


class PostView(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostUpdateView(UpdateView):
    template_name = 'news_edit.html'
    form_class = PostForm

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления товара
class PostDeleteView(DeleteView):
    template_name = 'post_delete.html'
    # queryset = Post.objects.get(pk=id)
    success_url = '/news/'

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class NewsCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        current_url = self.request.path
        post = form.save(commit=False)
        post.category_news = self.model.NEWS
        return super().form_valid(form)


class ArticleCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        current_url = self.request.path
        post = form.save(commit=False)
        post.category_news = self.model.ARTICLE
        return super().form_valid(form)


class PostCreate(CreateView):
    # Указываем нашу разработанную форму
    form_class = PostForm
    # модель товаров
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'post_create.html'


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'user_update.html'
    form_class = UserForm

    def get_object(self, **kwargs):
        return self.request.user


class GradientView(DetailView):
    template_name = 'gradient.html'
    form_class = UserForm


class ClassMessage(View):
    # template_name = 'send_mess.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'send_message.html', {})

    def post(self, request, *args, **kwargs):

        html_content = render_to_string(
            'message.html', {}
        )

        msg = EmailMultiAlternatives(
            subject='d_mess',
            body="{appointment}",
            from_email='khusainovoff@yandex.ru',
            to=['ikhusainov@gmail.com'],
        )

        msg.attach_alternative(html_content, 'text/html')

        msg.send()

        return redirect('/news/message/')

class CategoryList(ListView):
    model = Category
    template_name = 'subscribers.html'
    context_object_name = 'categories'
    queryset = Category.objects.order_by('-id')


@login_required
def add_subscribe(request):
    user = request.user
    category = Category.objects.get(pk=request.POST['id_cat'])
    subscribe = UserCategory(user_id=user.id, category_id=category.id)
    subscribe.save()
    return redirect('/')

@receiver(post_save, sender=PostCategory)
def post(sender, instance, created, **kwargs):
    users = Category.objects.filter(pk=instance.postCategory).values("subscribers")
    for i in users:
        send_mail(
            subject=f"{instance.title}",
            message=f"Здравствуй, {User.objects.get(pk=i['subscribers']).username}."
                    f" Новая статья в твоём любимом разделе! \n Заголовок статьи: {instance.title} \n"
                    f" Текст статьи: {instance.text[:50]}",
            from_email='khusainovoff@yandex.ru',
            recipient_list=[User.objects.get(pk=i['subscribers']).email],
        )
        return redirect('/')


class IndexView(View):
    def get(self, request):
        hello.delay()
        return HttpResponse('Hello!')