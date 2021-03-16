import re
import os
import random
import datetime
from django.db.models import Q
from django.urls import reverse
from django.http import Http404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from django.contrib.auth import login as auth_login
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, UserEditForm, ProfileEditForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def home(request):
    context = {'title': 'codeDM | Home'}
    return render(request, 'index.html', context)


def blog(request):

    # local
    category_posts = Category.objects.all()
    a = []
    for i in category_posts:
        a.append(Post.objects.filter(category_id=i.id, publish=True).count())
    category_posts = zip(category_posts, a)

    # Trending post
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    trends = Post.objects.filter(
        time_upload__gte=week_ago, publish=True).order_by('-read')[:4]

    # popular post
    popular_posts = Post.objects.filter(publish=True).order_by('-read')

    # paginator
    all_post = Paginator(Post.objects.filter(publish=True), 3)
    page = request.GET.get('page')

    try:
        posts = all_post.page(page)
    except PageNotAnInteger:
        posts = all_post.page(1)
    except EmptyPage:
        posts = all_post.page(all_post.num_pages)

    if page is None:
        start_index = 0
        end_index = 7
    else:
        (start_index, end_index) = proper_pagination(posts, index=4)

    page_range = list(all_post.page_range)[start_index:end_index]

    context = {
        'title': 'codeDM | Blog',
        'category_posts': category_posts,
        'posts': posts,
        'page_range': page_range,
        'trends': trends,
        'popular_posts': popular_posts,
    }
    return render(request, 'blog.html', context)


def proper_pagination(posts, index):
    start_index = 0
    end_index = 7
    if posts.number > index:
        start_index = posts.number - index
        end_index = start_index + end_index
    return (start_index, end_index)


def search(request):
    # search articles
    q = request.GET.get('q')
    posts = Post.objects.filter(Q(title__icontains=q) | Q(
        overview__icontains=q), publish=True).distinct()

    # local
    category_posts = Category.objects.all()
    a = []
    for i in category_posts:
        a.append(Post.objects.filter(category_id=i.id, publish=True).count())
    category_posts = zip(category_posts, a)

    # parameters
    context = {
        'title': f'codeDM | Blog',
        'posts': posts,
        'category_posts': category_posts,
        'q_title': f'{q}',
        'popular_posts': Post.objects.filter(publish=True).order_by('-read'),
    }
    return render(request, 'all.html', context)


def category(request, cats):
    posts = Post.objects.filter(publish=True)[:4]
    category_posts = Post.objects.filter(
        category__cat_name=cats.replace('-', ' '), publish=True)

    context = {
        'title': 'codeDM | Category',
        'category_posts': category_posts,
        'category_name': cats.title().replace('-', ' '),
        'posts': posts,
        'popular_posts': Post.objects.filter(publish=True).order_by('-read')
    }

    return render(request, 'category.html', context)


def post_detail(request, id, slug):
    post = get_object_or_404(Post, id=id, slug=slug)
    comments_count1 = Comment.objects.filter(post=post).order_by('-id')
    subcomments_count1 = SubComment.objects.filter(post=post).order_by('-id')
    comments_count = comments_count1.count() + subcomments_count1.count()

    post.read += 1
    post.save()

    is_liked = False
    is_favourite = False
    if post.likes.filter(id=request.user.id).exists():
        is_liked = True

    if post.favourite.filter(id=request.user.id).exists():
        is_favourite = True

    if request.method == 'POST':
        comm = request.POST.get('comm')
        comm_id = request.POST.get('comm_id')  # None

        if comm_id:
            SubComment(post=post,
                       user=request.user,
                       comm=comm,
                       comment=Comment.objects.get(id=int(comm_id))
                       ).save()
        else:
            Comment(post=post, user=request.user, comm=comm).save()

    comments = []
    for c in Comment.objects.filter(post=post).order_by('-id'):
        comments.append([c, SubComment.objects.filter(comment=c)])

    context = {
        'title': 'codeDM | Post Detail',
        'comments_count': comments_count,
        'comments': comments,
        'post': post,
        'is_liked': is_liked,
        'is_favourite': is_favourite,
        'total_likes': post.total_likes(),
    }
    if request.is_ajax():
        html = render_to_string('comments.html', context, request=request)
        return JsonResponse({'form': html})

    return render(request, 'post_detail.html', context)


def like_post(request):
    post = get_object_or_404(Post, id=request.POST.get('id'))
    is_liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True

    context = {
        'post': post,
        'is_liked': is_liked,
        'total_likes': post.total_likes(),
    }
    if request.is_ajax():
        html = render_to_string('like_section.html', context, request=request)
        return JsonResponse({'form': html})


def favourite_post(request, id):
    post = get_object_or_404(Post, id=id)
    if post.favourite.filter(id=request.user.id).exists():
        post.favourite.remove(request.user)
    else:
        post.favourite.add(request.user)

    return HttpResponseRedirect(post.get_absolute_url())


def post_favourite_list(request):
    user = request.user
    favourite_posts = user.favourite.all()
    context = {
        'title': 'codeDM | Favoutite posts',
        'favourite_posts': favourite_posts,
    }
    return render(request, 'user/post_favourite_list.html', context)


def about(request):
    posts = Post.objects.all()
    context = {'title': 'codeDM | About', 'posts': posts}

    return render(request, 'about.html', context)


def contact(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        message = request.POST['message']

        value = {
            'username': username,
            'email': email,

        }
        error_message = None
        if(not username):
            error_message = "Name Required !!"
        elif len(username) < 3:
            error_message = "Name must be 3 char long !!"
        elif (not re.search("^[A-Za-z]+$", username)):
            error_message = "Name field only contains alphabets !!"
        elif (not email):
            error_message = "Email Required !!"
        elif not (re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email)):
            error_message = "Your Email is Invalid !!"
        elif (not message):
            error_message = "Message field can not be empty !!"

        if not error_message:
            contact_obj = Contact(
                username=username, email=email, message=message)
            contact_obj.save()
            messages.success(request, "Thank you for Your Feedback !!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render(request, 'contact.html', data)
    else:
        context = {'title': 'codeDM | Contact'}
        return render(request, 'contact.html', context)


def newsletter(request):
    
    if request.method == "POST":

        email = request.POST['email']

        form = Subscribe(email=email)
        form.save()
        template = render_to_string('email_template/email_template.html', {'email' : email})
        msg = EmailMessage(
            'Thank you for subscribing our newsletter!',
            template,
            settings.EMAIL_HOST_USER, [email]
            )

        msg.content_subtype = "html"
        msg.send()
        messages.success(
            request, f"Thank you for subscribing our newsletter {email} !!")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('home')


def signup(request):
    if request.method == 'POST':
        get_otp = request.POST.get('otp')

        if get_otp:
            get_usr = request.POST.get('usr')
            usr = User.objects.get(username=get_usr)
            if int(get_otp) == UserOTP.objects.filter(user=usr).last().otp:
                usr.is_active = True
                usr.save()
                # newtask Start
                Profile.objects.create(user=usr)
                # end
                messages.success(
                    request, f'Account is created for {usr.username}')
                return redirect('login')
            else:
                messages.warning(request, f'You Entered a wrong OTP')
                return render(request, 'user/signup.html', {'otp': True, 'usr': usr})

        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            name = form.cleaned_data.get('name').split(' ')

            usr = User.objects.get(username=username)
            usr.email = username
            usr.is_active = False
            usr.save()
            usr_otp = random.randint(100000, 999999)
            UserOTP.objects.create(user=usr, otp=usr_otp)
            mess = f"Hello {usr.username},\nYour OTP is {usr_otp}\nThanks!"

            send_mail(
                "Welcome to codeDM - Verify Your Email",
                mess,
                settings.EMAIL_HOST_USER,
                [usr.email],
                fail_silently=False
            )
            messages.success(request, f"OTP is sent to your email Address : {usr.email}")

            return render(request, 'user/signup.html', {'title': 'codeDM | Signup', 'otp': True, 'usr': usr})
    else:
        form = SignUpForm()

    return render(request, 'user/signup.html', {'title': 'codeDM | Signup', 'form': form})


def resend_otp(request):
    if request.method == "GET":
        get_usr = request.GET.get('usr')
        if User.objects.filter(username=get_usr).exists() and not User.objects.get(username=get_usr).is_active:
            usr = User.objects.get(username=get_usr)
            usr_otp = random.randint(100000, 999999)
            UserOTP.objects.create(user=usr, otp=usr_otp)
            mess = f"Hello {usr.username},\nYour OTP is {usr_otp}\nThanks!"

            send_mail(
                "Welcome to codeDM - Verify Your Email",
                mess,
                settings.EMAIL_HOST_USER,
                [usr.email],
                fail_silently=False
            )
    else:
        return HttpResponse("Please check your internet connection or try again!!")


def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        get_otp = request.POST.get('otp')

        if get_otp:
            get_usr = request.POST.get('usr')
            usr = User.objects.get(username=get_usr)
            if int(get_otp) == UserOTP.objects.filter(user=usr).last().otp:
                usr.is_active = True
                usr.save()
                auth_login(request, usr)
                return redirect('home')
            else:
                messages.warning(request, f'You Entered a wrong OTP')
                return render(request, 'user/login.html', {'title': 'codeDM | Login', 'otp': True, 'usr': usr})

        usrname = request.POST['username']
        passwd = request.POST['password']

        user = authenticate(request, username=usrname, password=passwd)
        if user is not None:
            messages.success(request, f"Login successfully as {usrname} !!")
            auth_login(request, user)
            return redirect('home')
        elif not User.objects.filter(username=usrname).exists():
            messages.warning(
                request, f'Please enter a correct username and password. Note that both the fields may be case-sensitive.')
            return redirect('login')
        elif not User.objects.get(username=usrname).is_active:
            usr = User.objects.get(username=usrname)

            usr_otp = random.randint(100000, 999999)
            UserOTP.objects.create(user=usr, otp=usr_otp)
            mess = f"Hello {usr.username},\nYour OTP is {usr_otp}\nThanks!"

            send_mail(
                "Welcome to codeDM - Verify Your Email",
                mess,
                settings.EMAIL_HOST_USER,
                [usr.email],
                fail_silently=False
            )
            return render(request, 'user/signup.html', {'title': 'codeDM | Login', 'otp': True, 'usr': usr})
        else:
            messages.warning(
                request, f'Please enter a correct username and password. Note that both the fields may be case-sensitive.')
            return redirect('login')

    form = AuthenticationForm()
    return render(request, 'user/login.html', {'title': 'codeDM | Login', 'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            data=request.POST or None, instance=request.user)
        profile_form = ProfileEditForm(
            data=request.POST or None, instance=request.user.profile, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully !!")
            return HttpResponseRedirect(reverse("edit_profile"))
        else:
            messages.warning(request, "Invalid details, Please try again !!")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    context = {
        'title': 'codeDM | Edit Profile',
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'user/edit_profile.html', context)


def terms_of_services(request):
    # Trending post
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    trends = Post.objects.filter(
        time_upload__gte=week_ago, publish=True).order_by('-read')[:4]

    # popular post
    popular_posts = Post.objects.filter(publish=True).order_by('-read')

    # local
    category_posts = Category.objects.all()
    a = []
    for i in category_posts:
        a.append(Post.objects.filter(category_id=i.id, publish=True).count())
    category_posts = zip(category_posts, a)

    context = {
        'title': 'codeDM | Terms of services',
        'trends': trends,
        'popular_posts': popular_posts,
        'category_posts': category_posts,
    }
    return render(request, "terms_of_services.html", context)


def our_story(request):
    context = {'title': 'codeDM | Our story'}
    return render(request, "our_story.html", context)


def privacy_policy(request):
    # Trending post
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    trends = Post.objects.filter(
        time_upload__gte=week_ago, publish=True).order_by('-read')[:4]

    # popular post
    popular_posts = Post.objects.filter(publish=True).order_by('-read')

    # local
    category_posts = Category.objects.all()
    a = []
    for i in category_posts:
        a.append(Post.objects.filter(category_id=i.id, publish=True).count())
    category_posts = zip(category_posts, a)

    context = {
        'title': 'codeDM | Privacy policy',
        'trends': trends,
        'popular_posts': popular_posts,
        'category_posts': category_posts,
    }
    return render(request, "privacy_policy.html", context)


# books function based views

def resources(request):
    category = BookCategory.objects.all()
    recommanded_books = Book.objects.filter(recommanded_book = True)
    top_proggamming_book = Book.objects.filter(top_proggamming_book = True)
    context = {
        'title': 'codeDM | resources',
        'recommanded_books' : recommanded_books,
        'top_proggamming_book' : top_proggamming_book,
        'category' : category,
        }

    return render(request, 'Books/resources.html', context)


def resources_detail(request, slug):
    resources_category = BookCategory.objects.get(slug = slug)
    
    category = BookCategory.objects.all()
    context = {
        'title' : 'codeDM | resources',
        'resources_category' : resources_category,
        'category' : category,
    }
    return render(request, "Books/resources_detail.html", context)


def booksearch(request):
    q = request.GET.get('q')
    books = Book.objects.filter(Q(title__icontains=q) | Q(
        author__icontains=q)).distinct()

    context = {
        'q_title': f'{q}',
        'books' : books,
    }
    return render(request, 'Books/resources_search.html', context)


def book_detail(request, slug):
    book = get_object_or_404(Book, slug = slug)
    books = Book.objects.all()[:2]
    top_proggamming_book = Book.objects.filter(top_proggamming_book = True)

    context = {
        'title' : 'codeDM | book detail',
        'recent_book' : 'recent_book',
        'book' : book,
        'books' : books,
        'top_proggamming_book' : top_proggamming_book,
    }
    return render(request, 'Books/book_detail.html', context)


def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


