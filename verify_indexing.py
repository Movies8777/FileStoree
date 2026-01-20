import asyncio
from database.database import db

async def verify():
    # Test add_file
    await db.add_file("test_id", "Test Movie 2023", 1024, "video", "Test Caption", 123)
    print("Added test file.")

    # Test search_files
    results = await db.search_files("Test Movie")
    print(f"Search results: {results}")

    if results and results[0]['file_id'] == "test_id":
        print("Indexing verification successful!")
    else:
        print("Indexing verification failed.")

if __name__ == "__main__":
    asyncio.run(verify())
