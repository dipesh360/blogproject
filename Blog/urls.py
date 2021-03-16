"""Blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from Blogapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('blog/', views.blog, name='blog'),
    path('blog/search/', views.search, name='search'),
    path('blog/post_detail/<int:id>/<slug:slug>/',
         views.post_detail, name='post_detail'),

    path('category/<str:cats>/', views.category, name='category'),

    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('signup/', views.signup, name='signup'),
    path('newsletter/', views.newsletter, name='newsletter'),
    path('like/', views.like_post, name='like_post'),
    path('favourite_post/<int:id>/', views.favourite_post, name='favourite_post'),
    path('favourites/', views.post_favourite_list, name='post_favourite_list'),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('login/', views.login, name='login'),
    path('profile/', views.edit_profile, name='edit_profile'),

    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='user/password_change.html'),name='password_change'),
        
    path('password_change/done', auth_views.PasswordChangeDoneView.as_view(
        template_name='user/password_change_done.html'),name='password_change_done'),

    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name='user/password_reset.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='user/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='user/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='user/password_reset_done.html'), name='password_reset_complete'),

    path('resendOTP/', views.resend_otp, name='resend_otp'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('our-story/', views.our_story, name='our_story'),
    path('terms-and-conditions/', views.terms_of_services, name='terms_of_services'),

# books url 
    path('resources/', views.resources, name='resources'),
    path('resources-detail/<str:slug>/', views.resources_detail, name='resources_detail'),
    path('book-search/', views.booksearch, name='booksearch'),
    path('book_detail/<str:slug>/', views.book_detail, name='book_detail'),
    url(r'^download/(?P<path>.*)$', serve, {'document root': settings.MEDIA_ROOT}),


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
