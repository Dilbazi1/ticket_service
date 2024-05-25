from django.contrib import admin
from ticketapp.models import User,Profile,ChatMessage,CreateTask

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']


class ProfileAdmin(admin.ModelAdmin):
    list_editable = ['verified']
    list_display = ['user', 'full_name' ,'verified']


admin.site.register(User, UserAdmin)
admin.site.register( Profile,ProfileAdmin)
admin.site.register( ChatMessage)
admin.site.register( CreateTask)