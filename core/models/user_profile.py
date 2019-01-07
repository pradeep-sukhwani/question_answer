from django_extensions.db.models import models
from django.contrib.auth import get_user_model

User = get_user_model()


def get_image_path(filename):
    return 'user_%s' % filename


class Profile(models.Model):
    user = models.OneToOneField(User)
    location = models.CharField(max_length=225, null=True, blank=True, help_text='Location of user')
    title = models.CharField(max_length=100, help_text='Title/Headline that describes user\'s specialities')
    description = models.TextField("Tell us something about yourself")
    personal_website = models.CharField(max_length=225, null=True, blank=True, help_text='Personal website/portfolio'
                                                                                         'link')
    twitter_username = models.CharField(max_length=100, null=True, blank=True, help_text='Twitter username')
    github_username = models.CharField(max_length=100, null=True, blank=True, help_text='Github username')
    avatar = models.ImageField(upload_to=get_image_path, null=True, blank=True, help_text='User\'s profile pic')

    class Meta:
        verbose_name_plural = 'Profile'

    def __str__(self):
        return u"{user}".format(user=self.user.username)
