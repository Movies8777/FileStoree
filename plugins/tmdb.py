import aiohttp
from config import TMDB_API_KEY

async def search_tmdb(query):
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('results'):
                    return data['results'][0]
    return None

async def get_movie_details(tmdb_id, media_type):
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={TMDB_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                poster_path = data.get('poster_path')
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                rating = data.get('vote_average', 0)
                genres = [g['name'] for g in data.get('genres', [])]
                return {
                    'poster_url': poster_url,
                    'rating': rating,
                    'genres': genres,
                    'title': data.get('title') or data.get('name'),
                    'overview': data.get('overview')
                }
    return None
