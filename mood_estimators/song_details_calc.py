import pandas as pd
import os
import numpy as np
import ijson
import json
import sys
import matplotlib
import matplotlib.pyplot as plt
import bertai
import dotenv
from pymongo import MongoClient
from max_heap import MaxHeap

MONGO_URL = "soundsmith.x5y65kb.mongodb.net"

def get_db_connection() -> MongoClient | None:
    """Creates and returns db connection.

    Returns:
        MongoClient | None: MongoClient object, or None if connection fails.
    """
    dotenv.load_dotenv(os.path.join(__file__, ".env"))
    mongo_user = dotenv.dotenv_values().get("MONGO_USER")
    mongo_password = dotenv.dotenv_values().get("MONGO_PASSWORD")
    mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_password}@{MONGO_URL}/"
    client = MongoClient(mongo_uri)
    db = client.soundsmith
    try:
        db.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        return
    return db

def import_tracks(db: MongoClient, query = {}):
    """Import tracks from the database.

    Args:
        db (MongoClient): The MongoDB client.

    Returns:
        list: List of tracks.
    """
    return list(db.tracks.find(query))

def import_standard_songs(db: MongoClient, emotion):
    tracks = list(db.tracks.find({"standard": emotion}))
    return [(track["vector"], track["spotify"]["track_id"]) for track in tracks]

def cosine_similarity(vector1, vector2):
    """Calculate the cosine similarity between two vectors.

    Args:
        vector1 (np.ndarray): The first vector.
        vector2 (np.ndarray): The second vector.

    Returns:
        float: The cosine similarity between the two vectors.
    """
    dot_product = np.dot(vector1, vector2)
    magnitude_vector1 = np.linalg.norm(vector1)
    magnitude_vector2 = np.linalg.norm(vector2)
    return dot_product / (magnitude_vector1 * magnitude_vector2)

def main(group):
    client = get_db_connection()
    dict_DB = import_tracks(client)
    heap = MaxHeap()

    stand_vect_dict = {
        "happy" : import_standard_songs(client, "happy"),
        "sad": import_standard_songs(client, "sad"),
        "chill": import_standard_songs(client, "chill"),
        "stressing": import_standard_songs(client, "stressing"),
    }

    for track in dict_DB:
        print(f"Song name: {track["track_name"]} by {track["artist_name"]}")
        print(f"Song dimensions: {track["vector"]}")
        P1 = np.array(list(track["vector"].values()))
        
        # for quadrant in stand_vect_dict:
        #     if quadrant == group:
        #         sum = 0
        #         # print(quadrant, end=": ")
        #         for each_song in stand_vect_dict[quadrant]:
        #             P2 = np.array(list(each_song[0].values()))
        #             sum += cosine_similarity(P1, P2)
                    
        #         similarity = sum / len(stand_vect_dict[quadrant])
        #         heap.insert((similarity, track["track_name"], track["artist_name"]))
        # print("-----------------------------")
        rank = []
        for each_sentiment in group:
            for quadrant in stand_vect_dict:
                if quadrant == each_sentiment:
                    sum = 0
                    # print(quadrant, end=": ")
                    for each_song in stand_vect_dict[quadrant]:
                        P2 = np.array(list(each_song[0].values()))
                        sum += cosine_similarity(P1, P2)
                        
                    similarity = sum / len(stand_vect_dict[quadrant])
                    rank.append(similarity)
            print("-----------------------------")

        heap.insert((rank[0], rank[1], rank[2], track["track_name"], track["artist_name"]))


    heap.print_sorted_heap(20)

def import_emotions_predict(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            keys = list(data.keys())[:3]

            top_three_emotions = []

            for key in keys:
                if (key == "joy") or (key == "amusement") or (key == "surprise") or (key == "love") or (key == "excitement") or (key == "gratitude") or (key == "pride") or (key == "relief"):
                    top_three_emotions.append("happy")
                elif (key == "sadness") or (key == "disappointment") or (key == "grief") or (key == "remorse") or (key == "embarrassment"):
                    top_three_emotions.append("sad")
                elif (key == "neutral") or (key == "curiosity") or (key == "approval") or (key == "admiration") or (key == "realization") or (key == "optimism") or (key == "desire") or (key == "relief"):
                    top_three_emotions.append("chill")
                elif (keys == "anger") or (keys == "annoyance") or (key == "disapproval") or (key == "disgust") or (key == "fear") or (key == "confusion") or (key == "caring") or (key == "nervousness"):
                    top_three_emotions.append("stressing")

        return(top_three_emotions)

    except FileNotFoundError:
        return "File not found"
    except json.JSONDecodeError:
        return "Invalid JSON format"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    two_sentiments = import_emotions_predict('mood_estimators\\emotion_predictions.json')
    # two_sentiments = "happy"
    # print(two_sentiments)
    main(two_sentiments)