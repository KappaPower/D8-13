from django.urls import path
from .views import PostList, PostDetail, PostSearch, PostUpdateView, PostDeleteView, PostCreate, ArticleList, \
    UserUpdateView, GradientView, CategoryList, add_subscribe, IndexView
from django.views.decorators.cache import cache_page

# Если вы используете классовые представления или дженерики, то нужно добавлять кэширование напрямую в urls.py
# (в котором хранятся именно сами представления, а не основной urls.py из папки с settings.py).
urlpatterns = [
    path('', PostList.as_view()),
    path('article/', ArticleList.as_view(), name='article_list'),
    path('<int:pk>', cache_page(300)(PostDetail.as_view())), # добавим кэширование на детали товара. Раз в 100 сек товар будет записываться в кэш для экономии ресурсов.
    path('search/', PostSearch.as_view(), name='search'),
    path('<int:pk>/edit/', PostUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete', PostDeleteView.as_view(), name='post_delete'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('user/', UserUpdateView.as_view(), name='user_update'),
    path('gradient/', GradientView.as_view(), name='gradient'),
    path('sub/', CategoryList.as_view(), name='category'),  # Путь к списку категорий с кнопками на подписку
    path('sub/subscribe/', add_subscribe, name='subscribe'),
    path('', IndexView.as_view())
]
