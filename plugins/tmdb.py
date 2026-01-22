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
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={TMDB_API_KEY}&append_to_response=images"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                backdrops = data.get('images', {}).get('backdrops', [])
                backdrop_urls = [f"https://image.tmdb.org/t/p/original{b['file_path']}" for b in backdrops]

                # If no backdrops in images, try the main backdrop_path
                if not backdrop_urls and data.get('backdrop_path'):
                    backdrop_urls.append(f"https://image.tmdb.org/t/p/original{data['backdrop_path']}")

                rating = data.get('vote_average', 0)
                genres = [g['name'] for g in data.get('genres', [])]
                release_date = data.get('release_date') or data.get('first_air_date')
                return {
                    'backdrop_urls': backdrop_urls,
                    'rating': rating,
                    'genres': genres,
                    'title': data.get('title') or data.get('name'),
                    'overview': data.get('overview'),
                    'release_date': release_date,
                    'language': data.get('original_language', 'N/A').upper()
                }
    return None
