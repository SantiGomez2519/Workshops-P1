import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Assign images to movies from the media folder"

    def handle(self, *args, **kwargs):
        media_path = 'media/movie/images/'  # Ruta donde se encuentran las imágenes
        updated_count = 0

        # ✅ Verifica si la carpeta de imágenes existe
        if not os.path.exists(media_path):
            self.stderr.write(f"Image directory '{media_path}' not found.")
            return

        # 🔍 Recorre todas las películas en la base de datos
        for movie in Movie.objects.all():
            image_filename = f"m_{movie.title}.png"
            image_path = os.path.join(media_path, image_filename)

            if os.path.exists(image_path):
                # ✍️ Actualizar la ruta de la imagen en la base de datos
                movie.image = f"movie/images/{image_filename}"
                movie.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated image for: {movie.title}"))
            else:
                self.stderr.write(f"Image not found for: {movie.title}")

        # ✅ Muestra cuántas películas se actualizaron
        self.stdout.write(self.style.SUCCESS(f"Finished updating images for {updated_count} movies."))
