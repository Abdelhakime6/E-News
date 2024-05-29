from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from autoslug import AutoSlugField
from tinymce.models import HTMLField
from taggit.managers import TaggableManager



class Custom_Users(AbstractUser):
    email = models.EmailField(unique = True)
    is_registered_user = models.BooleanField(default=False)
    is_journalist_user = models.BooleanField(default=False)
    is_approved = models.BooleanField(default = False)
 
class registered_users(models.Model):
    user = models.OneToOneField(Custom_Users, on_delete=models.CASCADE, primary_key=True, related_name='registered_user')
    bio = models.CharField(max_length=400)
    created_at = models.DateTimeField(default=timezone.now)


class journalist_users(models.Model):
    user = models.OneToOneField(Custom_Users, on_delete=models.CASCADE, primary_key=True, related_name='journalist_user')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.CharField(max_length=400)
    created_at = models.DateTimeField(default=timezone.now)

class article(models.Model):
    image=models.ImageField(upload_to = "images/")
    title = models.CharField(max_length=100)
    slug = models.SlugField(null=True, unique=True)
    content = HTMLField(null=True)
    journalist_users = models.ForeignKey(journalist_users, on_delete=models.CASCADE, related_name='article')
    likes = models.ManyToManyField(Custom_Users,blank=True, related_name='liked_by_user')
    dislikes = models.ManyToManyField(Custom_Users,blank=True, related_name='disliked_by_user')
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    admin_approved = models.BooleanField(default= False)
    tags = TaggableManager()

    def total_likes(self):
        return self.likes.count()
    
class comment(models.Model):
    article =  models.ForeignKey(article, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)



    

    

