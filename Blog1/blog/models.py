from django.db import models
from users.models import UsersUserinfo
# Create your models here.

class BlogComments(models.Model):
    text = models.CharField(max_length=200)
    creator = models.ForeignKey('users.UsersUserinfo', models.DO_NOTHING)
    blog = models.ForeignKey('BlogsBlog', models.DO_NOTHING)
    createtime = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'blog_comments'
        verbose_name='Blog Comment'



class BlogPhoto(models.Model):
    photo = models.CharField(max_length=100)
    blog = models.ForeignKey('BlogsBlog', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'blog_photo'


class BlogsBlog(models.Model):
    users_userinfo = models.ForeignKey('users.UsersUserinfo', models.DO_NOTHING)
    text = models.CharField(max_length=200, blank=True, null=True)
    createtime = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'blogs_blog'
        verbose_name = 'Blog'
