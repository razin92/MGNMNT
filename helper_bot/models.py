from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Language(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=3)
    enabled = models.BooleanField(default=True)
    ico = models.CharField(max_length=100)

    def __str__(self):
        return '%s-%s' % (self.code, self.name)

class MenuGroup(models.Model):
    menu_group = {
        ('language', 'language'),
        ('settings', 'settings'),
        ('main_menu', 'main_menu'),
        ('setup_tv', 'setup_tv'),
        ('FAQ', 'FAQ'),
        ('news', 'news'),
    }
    group = models.CharField(max_length=100, choices=menu_group, null=True, unique=True)

    def __str__(self):
        return '%s' % (self.group)

class MenuItem(models.Model):
    menu_item_list = {
        ('language', 'language'),
        ('settings', 'settings'),
        ('main_menu', 'main_menu'),
        ('setup_tv', 'setup_tv'),
        ('FAQ', 'FAQ'),
        ('news', 'news'),
    }
    menu_item = models.CharField(max_length=100, choices=menu_item_list, null=True, unique=True)

    def __str__(self):
        return '%s' % (self.menu_item)

class BaseMenu(models.Model):
    menu_group = models.ManyToManyField(MenuGroup)
    enabled = models.BooleanField(default=True)
    sequence_number = models.PositiveSmallIntegerField(default=1)
    language = models.ForeignKey(Language)
    ico = models.CharField(max_length=100)

class Menu(BaseMenu):
    name = models.CharField(max_length=40)
    menu_item = models.ForeignKey(MenuItem)

    def __str__(self):
        return '%s (%s)' % (self.name, self.language.code)

class New(models.Model):
    name = models.CharField(max_length=20)
    date_pub = models.DateTimeField(auto_now=False)
    date_create = models.DateField(auto_now=True)
    language = models.ForeignKey(Language)
    text = models.CharField(max_length=500)
    creator = models.ForeignKey(User)
    notification = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return '%s - %s (%s)' % (self.name, self.date_pub, self.language)

class FAQ(models.Model):
    question = models.CharField(max_length=50)
    answer = models.CharField(max_length=500)
    position_number = models.PositiveSmallIntegerField(default=1)
    enabled = models.BooleanField(default=True)
    language = models.ForeignKey(Language)
    ico = models.CharField(max_length=100)

    def __str__(self):
        return '%s (%s)' % (self.question, self.language.code)

class TvModel(models.Model):
    vendor = models.CharField(max_length=50)
    position_number = models.PositiveSmallIntegerField(default=1)
    ico = models.CharField(max_length=100)

    def __str__(self):
        return '%s' % (self.vendor)

class TvSettings(models.Model):
    sequence_number = models.PositiveSmallIntegerField(default=1)
    model = models.ForeignKey(TvModel)
    language = models.ForeignKey(Language)
    text = models.CharField(max_length=100)
    image = models.ImageField()
    parent = models.ForeignKey('TvSettings', blank=True, null=True)

    def __str__(self):
        return '%s-%s(%s)' % (self.sequence_number, self.model ,self.language.code)

class TGUser(models.Model):
    tg_id = models.PositiveIntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    language = models.ForeignKey(Language, null=True, blank=True)
    bcast_msg_banned = models.BooleanField(default=False)
    date_registration = models.DateField(auto_now=False)
    last_seen = models.DateField(auto_now=True)

    def __str__(self):
        return '%s: %s, %s' % (self.tg_id, self.first_name, self.last_name)

class SystemMessage(models.Model):
    type_list = {
        ('_error', '_error'),
        ('_description', '_description'),
        ('_success', '_success')
    }
    menu_item = models.ForeignKey(MenuItem)
    type_of_message = models.CharField(max_length=100, choices=type_list, null=True)
    text = models.CharField(max_length=100)
    language = models.ForeignKey(Language)

    class Meta():
        unique_together = ['menu_item', 'type_of_message' ,'language']

    def __str__(self):
        return '%s%s (%s)' % (self.menu_item, self.type_of_message, self.language.code)
