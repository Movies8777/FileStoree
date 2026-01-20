import asyncio
import os
from helper_func import get_tmdb_data

os.environ['TMDB_API_KEY'] = "8a28e8316c0b904c0d131f496738988a" # Using a known key if available or dummy

async def verify():
    res = await get_tmdb_data("The Dark Knight")
    print(f"TMDB Result: {res}")
    if res and res['title'] == 'The Dark Knight':
        print("TMDB verification successful!")
    else:
        print("TMDB verification failed.")

if __name__ == "__main__":
    asyncio.run(verify())
