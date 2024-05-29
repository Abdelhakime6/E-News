from django.contrib import admin
from .models import Custom_Users, journalist_users, registered_users, article, comment

# Register your models here.
admin.site.register(Custom_Users)
admin.site.register(journalist_users)
admin.site.register(article)
admin.site.register(registered_users)
admin.site.register(comment)