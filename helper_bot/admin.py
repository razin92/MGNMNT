from django.contrib import admin
from .models import Language, Menu, New, FAQ, TvModel, TvSettings, TGUser, SystemMessage
# Register your models here.
admin.site.register(Language)
admin.site.register(Menu)
admin.site.register(New)
admin.site.register(FAQ)
admin.site.register(TvModel)
admin.site.register(TvSettings)
admin.site.register(TGUser)
admin.site.register(SystemMessage)
