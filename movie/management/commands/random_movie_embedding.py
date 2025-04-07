from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np

class Command(BaseCommand):
    help = "Display the embeddings of a random movie"

    def handle(self, *args, **kwargs):

        # ✅ Fetch all movies from the database
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in the database")

        # Choose a random movie to display its embedding
        random_movie = movies.order_by('?').first()

        # ✅ Iterate through movies and display the embedding of the random movie
        if random_movie:
            try:
                emb = random_movie.emb
                emb = np.frombuffer(emb, dtype=np.float32)  # Convert bytes back to numpy array
                self.stdout.write(self.style.SUCCESS(f"✅ Embedding for: {random_movie.title}"))
                self.stdout.write(f"Embedding: {emb}")
            except Exception as e:
                self.stderr.write(f"❌ Failed to retrieve embedding for {random_movie.title}: {e}")
        else:
            self.stdout.write(self.style.WARNING("No movies found in the database."))
        