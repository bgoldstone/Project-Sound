import os
from typing import Union, List, Dict, Any
import bertai
import dotenv
from pymongo import MongoClient
import certifi

MONGO_URL = "soundsmith.x5y65kb.mongodb.net"

def get_db_connection() -> Union[MongoClient, None]:
    """Creates and returns db connection.

    Returns:
        Union[MongoClient, None]: MongoClient object, or None if connection fails.
    """
    dotenv.load_dotenv(os.path.join(__file__, ".env"))
    mongo_user = dotenv.dotenv_values().get("MONGO_USER")
    mongo_password = dotenv.dotenv_values().get("MONGO_PASSWORD")
    mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_password}@{MONGO_URL}/"
    client = MongoClient(mongo_uri,tlsCAFile=certifi.where())
    db = client.soundsmith
    try:
        db.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        return
    return db

def import_lyrics(db: MongoClient) -> List[Dict[str, Any]]:
    """Import lyrics from the database.

    Args:
        db (MongoClient): The MongoDB client.

    Returns:
        List[Dict[str, Any]]: List of tracks.
    """
    return list(db.lyrics.find({"sentient_analysis": {"$exists": False}}))

def load_analysis(db: MongoClient, id: str, percentage: Dict[str, Any]) -> None:
    """Load vectors into the database.

    Args:
        db (MongoClient): The MongoDB client.
        id (str): The ID of the track.
        percentage (Dict[str, Any]): The sentiment analysis percentage to be loaded.
    """
    track_query = {"track_id": id}

    # Find or create track
    mongo_track = db.lyrics.find_one_and_update(
        track_query,
        {"$set": {"sentient_analysis": percentage}},
        upsert=True,
        return_document=True,
    )

def main() -> None:
    """Main function for processing lyrics and loading sentiment analysis into the database."""
    client = get_db_connection()
    lyrics = import_lyrics(client)

    for each_lyric in lyrics:
        try:
            sentient_analysis = bertai.get_lyrics_mood(each_lyric["lyrics"])
            load_analysis(client, each_lyric["track_id"], sentient_analysis)
        except Exception as e:
            print(e)
            # If error, set default values
            sentient_analysis = {"positive_percentage": 0, "negative_percentage": 0, "mixed_percentage": 0, "no_impact_percentage": 0}
            load_analysis(client, each_lyric["track_id"], sentient_analysis)

if __name__ == "__main__":
    main()