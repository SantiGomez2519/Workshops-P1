from django.shortcuts import render
from django.http import HttpResponse

from .models import Movie

import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

import os
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv

# Create your views here.
def home(request):
    # return HttpResponse('<h1>Welcome to Home Page</h1>')
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'name': 'Santi Gómez', 'searchTerm': searchTerm, 'movies': movies})

def about(request):
    # return HttpResponse('<h1>Welcome to About Page</h1>')
    return render(request, 'about.html')

def statistics_view(request):
    matplotlib.use('Agg')

    # Gráfica de películas por año
    years = Movie.objects.values_list('year', flat=True).distinct().order_by('year')
    movie_counts_by_year = {}
    for year in years:
        if year:
            movies_in_year = Movie.objects.filter(year=year)
        else:
            movies_in_year = Movie.objects.filter(year__isnull=True)
            year = 'none'
        count = movies_in_year.count()
        movie_counts_by_year[year] = count

    bar_positions_year = range(len(movie_counts_by_year))
    plt.figure()
    plt.bar(bar_positions_year, list(movie_counts_by_year.values()), width=0.5, align='center')
    plt.title('Movies per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.xticks(bar_positions_year, list(movie_counts_by_year.keys()), rotation=90)
    plt.subplots_adjust(bottom=0.3)

    buffer_year = io.BytesIO()
    plt.savefig(buffer_year, format='png')
    buffer_year.seek(0)
    plt.close()

    image_year_png = buffer_year.getvalue()
    buffer_year.close()
    graphic_year = base64.b64encode(image_year_png).decode('utf-8')

    # Gráfica de películas por género (solo considerando el primer género)
    genre_counts = {}
    for movie in Movie.objects.all():
        if movie.genre:
            # La cadena contiene los géneros separados por comas
            first_genre = movie.genre.split(',')[0].strip()
        else:
            first_genre = 'Unknown'
        genre_counts[first_genre] = genre_counts.get(first_genre, 0) + 1

    bar_positions_genre = range(len(genre_counts))
    plt.figure()
    plt.bar(bar_positions_genre, list(genre_counts.values()), width=0.5, align='center')
    plt.title('Movies per Genre')
    plt.xlabel('Genre')
    plt.ylabel('Number of Movies')
    plt.xticks(bar_positions_genre, list(genre_counts.keys()), rotation=90)
    plt.tight_layout()

    buffer_genre = io.BytesIO()
    plt.savefig(buffer_genre, format='png')
    buffer_genre.seek(0)
    plt.close()

    image_genre_png = buffer_genre.getvalue()
    buffer_genre.close()
    graphic_genre = base64.b64encode(image_genre_png).decode('utf-8')

    return render(
        request,
        'statistics.html',
        {'graphic_year': graphic_year, 'graphic_genre': graphic_genre}
    )

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email': email})

def recommendations(request):
    if request.method == 'POST':
        # Recoger el prompt ingresado por el usuario desde el formulario
        prompt = request.POST.get('prompt')
        if not prompt:
            return render(request, 'recommendations.html', {'error': "No se proporcionó descripción", 'movie': None})

        # Cargar la API Key
        load_dotenv('./api_keys.env')
        client = OpenAI(api_key=os.environ.get('openai_api_key'))

        # Función para calcular similitud de coseno
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        # Generar embedding del prompt
        response = client.embeddings.create(
            input=[prompt],
            model="text-embedding-3-small"
        )
        prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)

        # Recorrer la base de datos y calcular la similitud para encontrar la mejor coincidencia
        best_movie = None
        max_similarity = -1
        for movie in Movie.objects.all():
            movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
            similarity = cosine_similarity(prompt_emb, movie_emb)
            if similarity > max_similarity:
                max_similarity = similarity
                best_movie = movie

        # Retornar la película recomendada a la plantilla
        return render(request, 'recommendations.html', {'movie': best_movie, 'prompt': prompt})
    else:
        # Mostrar el formulario para que el usuario ingrese un prompt
        return render(request, 'recommendations.html')