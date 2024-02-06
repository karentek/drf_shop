from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage


def profile_avatar_directory_path(instance: "Avatar", filename: str) -> str:
    """
    функция создает директорию пользователя по его username для сохранения аватара
    """
    return "profiles/avatar_{username}/{filename}".format(
        username=instance.profile_rel.user.username,
        filename=filename,
    )


class Avatar(models.Model):
    """
    Модель для аватара пользователя
    """
    image = models.ImageField(null=True, blank=True, upload_to=profile_avatar_directory_path)
    profile_rel = models.ForeignKey('Profile', on_delete=models.CASCADE, null=True, blank=True)


class Profile(models.Model):
    """
    модель профиля пользователя
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=150, null=True, blank=True, )
    phone = models.CharField(max_length=13, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    avatar_image = models.OneToOneField(Avatar, on_delete=models.CASCADE, null=True, blank=True)

    # def __str__(self):
    #     return f"{self.user.username!r}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    функция принимает сигнал при регистрации пользователя
    в этот момент создается пустой связанный с пользователем профиль
    """
    if created:
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)


@receiver(pre_save, sender=Profile)
def delete_old_avatar(sender, instance, **kwargs):
    """
    функция принимает сигнал при создании нового аватара пользователя
    и если существует предыдущий удаляет файл
    """
    try:
        old_profile = Profile.objects.get(pk=instance.id)
        if old_profile.avatar_image and old_profile.avatar_image.image != instance.avatar_image.image:
            # Delete the old avatar file if a new one is provided
            default_storage.delete(old_profile.avatar_image.image.name)
    except Profile.DoesNotExist:
        pass


pre_save.connect(delete_old_avatar, sender=Profile)
