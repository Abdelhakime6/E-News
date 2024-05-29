from django.urls import path
from . import views
from django.contrib import admin

from django.contrib.auth import views as auth_views


urlpatterns = [

		#path("home/", views.user_home(template_name="user_home.html", next_page='login'), name="user_home"),
        path("journalist/", views.journalist_home, name="journalist-home"),
        path('home/', views.LoginView.as_view(), name='login'),
        path('article/<slug:slug>/', views.article_view, name='article_view'),
        path('like/<int:pk>/',views.like_view, name='like_article'),
        path('dislike/<int:pk>/',views.dislike_view, name='dislike_article'),
        path('article/<slug:slug>/add_comment_ajax/', views.add_comment_ajax, name='add_comment_ajax'),
        path("signup/user/", views.UserSignUpView.as_view(), name="user-signup"),
    	path("signup/journalist/", views.JournalistSignUpView.as_view(), name="journalist-signup"),
    	path('logout/', auth_views.LogoutView.as_view(template_name="logout.html", next_page='login'), name="logout"),
        path("journalist/article/create/", views.create_article, name="create-article"),
        path('tag/<slug:slug>/', views.tagged_articles, name='tagged_articles'),
        path('top-articles/', views.top_articles, name='top_articles'),
        path('newest-articles/', views.newest_articles, name='newest_articles'),
        path('search/', views.search_results, name='search_results'),
        path('article/<int:pk>/update/', views.ArticleUpdateView.as_view(), name='update-article'),
        path('article/<int:pk>/request_delete/', views.request_delete, name='delete-article'),
]


admin.site.index_title = "E-NEWS Administration"
admin.site.site_header = "E-NEWS Admin"
admin.site.site_title = "E-NEWS"