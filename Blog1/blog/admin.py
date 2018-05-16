from django.contrib import admin

from blog.models import BlogsBlog, BlogComments

# Register your models here.

class BlogsBlogAdmin(admin.ModelAdmin):
	list_display = ['users_userinfo', 'text', 'createtime']
	list_filter = ['users_userinfo', 'createtime']
	ordering = ['createtime',]
admin.site.register(BlogsBlog, BlogsBlogAdmin)

class BlogCommentsAdmin(admin.ModelAdmin):
	list_display = ['creator', 'text', 'blog', 'createtime']
	list_filter = ['creator', 'blog', 'createtime']
	ordering = ['createtime',]
admin.site.register(BlogComments, BlogCommentsAdmin)
