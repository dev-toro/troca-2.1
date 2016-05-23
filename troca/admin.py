from django.contrib import admin
from models import Project, Skills, Skills_categories, UserProfile, Collaboration, CambioContrasena, Comment, Respond

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(Skills)
admin.site.register(Skills_categories)
admin.site.register(Collaboration)
admin.site.register(CambioContrasena)
admin.site.register(Comment)
admin.site.register(Respond)
