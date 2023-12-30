from django.urls import path
from . import views
from .feeds import LatestPostsFeed
from django.contrib.auth import views as auth_views


app_name = 'blog'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='blog/registration/login.html'), name='login'),
    path('', views.PostList.as_view(), name='post_list'),
    path('tag/<slug:tag_slug>/', views.PostList.as_view(), name='tags_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.PostDetail.as_view(), name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),
    path('feed/', LatestPostsFeed(), name='posts_feed'),
]