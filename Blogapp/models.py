from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}'


class UserOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_st = models.DateTimeField(auto_now=True)
    otp = models.SmallIntegerField()


class Category(models.Model):
    cat_name = models.CharField(
        max_length=150, help_text="please don't use any symbols and only lowercase letters allowed")

    class Meta:
        ordering = ['cat_name']

    def __str__(self):
        return f'{self.cat_name}'

    def save(self, *args, **kwargs):
        self.cat_name = self.cat_name.lower()
        return super(Category, self).save(*args, **kwargs)


class Post(models.Model):
    title = models.CharField(max_length=255)
    overview = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    body = RichTextUploadingField(null=True)
    time_upload = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='thumbnails')
    publish = models.BooleanField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    read = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    favourite = models.ManyToManyField(User, related_name='favourite', blank=True)


    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['-pk']

    def total_likes(self):
        return self.likes.count()
        
    def get_absolute_url(self):
        return reverse("post_detail", args=[self.id, self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)


class Subscribe(models.Model):
    email = models.EmailField()

    def __str__(self):
        return f'{self.email}'

    class Meta:
        ordering = ['-pk']


class Contact(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.username}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField(
        null=True, blank=True, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")
    photo = models.ImageField(null=True, blank=True, upload_to='user_profiles')

    def __str__(self):
        return f"Profile of user :  {self.user.username}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    comm = models.TextField()

    def __str__(self):
        return f"{self.post.title} - {self.user.username}"

class SubComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    comm = models.TextField()
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.post.title} - {self.user.username}"

#  Books models 

class BookCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True)

    # override the save method
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(BookCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    cover_image = models.ImageField(upload_to="books_cover_images")
    author = models.CharField(max_length = 50)
    summary = models.TextField()
    category = models.ManyToManyField(BookCategory, related_name="books")
    pdf = models.FileField(upload_to="Books")
    recommanded_book = models.BooleanField(default=False)
    top_proggamming_book = models.BooleanField(default=False)

    # override the save method
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Book, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} written by {self.author}"

    class Meta:
        ordering = ['-pk']


