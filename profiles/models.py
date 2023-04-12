from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image

# uuid: hexadeximal 32 caracteres

def profile_picture_path(instance, filename):
    # Generar un nombre aleatorio usando la libreria uuid
    random_filename = str(uuid.uuid4())
    # Recupero la extensión del archivo de imagen
    extension = os.path.splitext(filename)[1]
    # Devuelvo la ruta completa final del archivo
    return 'users/{}/{}{}'.format(instance.user.username, random_filename, extension)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(default='default.png', upload_to=profile_picture_path)
    location = models.CharField(max_length=80, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Verificar que la imagen que estoy subiendo es diferente a la predeterminada
        if self.pk and self.picture.name != 'default.png':
            old_profile = Profile.objects.get(pk=self.pk)
            default_image_path = os.path.join(settings.MEDIA_ROOT, 'default.png')

            if old_profile.picture.path != self.picture.path and old_profile.picture.path != default_image_path:
                # Voy a eliminar la imagen anterior si es distinta de la actual y distinta de default.png
                default_storage.delete(old_profile.picture.path)
        super(Profile, self).save(*args, **kwargs)

        # Todo el codigo para recortar y redimensionar la imagen
        if self.picture and os.path.exists(self.picture.path):
            # Redimensionar la imagen antes de guardarla
            with Image.open(self.picture.path) as img:
                ancho, alto = img.size

                if ancho > alto:
                    # La imagen es mas ancha que alta
                    nuevo_alto = 300
                    nuevo_ancho = int((ancho/alto) * nuevo_alto)
                    img = img.resize((nuevo_ancho, nuevo_alto))
                    img.save(self.picture.path)
                elif alto > ancho:
                    # La imagen es mas alta que ancha
                    nuevo_ancho = 300
                    nuevo_alto = int((alto/ancho) * nuevo_ancho )
                    img = img.resize((nuevo_ancho, nuevo_alto))
                    img.save(self.picture.path)
                else:
                    # La imagen es cuadrada
                    img.thumbnail((300, 300))
                    img.save(self.picture.path)

            # El recorte de la imagen final
            with Image.open(self.picture.path) as img:
                ancho, alto = img.size

                if ancho > alto:
                    left = (ancho - alto) / 2
                    top = 0
                    right = (ancho + alto) / 2
                    bottom = alto

                else:
                    left = 0
                    top = (alto - ancho) / 2
                    right = ancho
                    bottom = (alto + ancho) / 2

                img = img.crop((left, top, right, bottom))
                img.save(self.picture.path)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['-id']

    def __str__(self):
        return f"Perfil de {self.user.username}"


def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
