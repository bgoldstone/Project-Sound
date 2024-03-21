from datetime import datetime
from typing import Dict, List, Optional
import sys
import pathlib

from pymongo import MongoClient

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from auth import hasher


def get_user(username: str, db: MongoClient) -> str | None:
    """Get user from database from username asyncrously

    Args:
        username (str): Username

    Returns:
        str: User ID
    """
    return db["users"].find_one({"username": username})


def create_user(username: str, password: str, db: MongoClient) -> str:
    """Create user in database

    Args:
        username (str): Username
        password (str): Password

    Returns:
        str: User ID
    """
    user = {"username": username, "password": hasher.hash_password(password)}
    user["time"] = datetime.now()
    return db["users"].insert_one(user).inserted_id


def create_spotify_user(username: str, spotify_id: str, db: MongoClient) -> str:
    """Create user in database

    Args:
        username (str): Username
        spotify_id (str): Spotify ID
    """
    user = {"username": username}
    user["time"] = datetime.now()
    user["spotify_id"] = spotify_id
    db["users"].insert_one(user)
    return get_spotify_user(spotify_id, db)


def get_spotify_user(spotify_id: str, db: MongoClient) -> str | None:
    """Get user from database from username asyncrously

    Args:
        username (str): Username

    Returns:
        str: User ID
    """
    return db["users"].find_one({"spotify_id": spotify_id})


def update_user(
    user_id: str,
    db: MongoClient,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> None:
    """Update user in database

    Args:
        user_id (str): User ID
        username (Optional[str]): Username
        password (Optional[str]): Password
    """
    if username is None:
        db["users"].update_one(
            {"_id": user_id},
            {
                "$set": {"password": hasher.hash_password(password)},
                "time": datetime.now(),
            },
        )
        return
    if password is None:
        db["users"].update_one(
            {"_id": user_id}, {"$set": {"username": username, "time": datetime.now()}}
        )
        return
    db["users"].update_one(
        {"_id": user_id},
        {
            "$set": {
                "username": username,
                "password": hasher.hash_password(password),
                "time": datetime.now(),
            }
        },
    )


def delete_user(username: str, db: MongoClient) -> None:
    """Delete user in database

    Args:
        db (MongoClient): Database
        username (str): Username
    """
    db["users"].delete_one({"username": username})


def get_playlist_by_name(
    playlist_name: str, db: MongoClient, user_id: Optional[str] = None
) -> Dict | None:
    """Searches database for Playlist with Playlist Name.

    Args:
        playlist_name (str): Playlist Name.
        user_id (str): User ID.

    Returns:
        Dict: Playlist Object or None if not found.
    """
    if user_id is None:
        return db["playlists"].find_one({"playlist_name": playlist_name})
    return db["playlists"].find_one(
        {"playlist_name": playlist_name, "user_id": user_id}
    )


def get_playlist_by_id(playlist_id: str, db: MongoClient) -> Dict | None:
    """Searches database for Playlist with Playlist ID.

    Args:
        playlist_id (str): Playlist ID.

    Returns:
        Dict: Playlist Object or None if not found.
    """
    return db["playlists"].find_one({"_id": playlist_id})


def create_playlist(
    user_id: str, playlist_name: str, tracks: List[str], db: MongoClient
) -> str:
    """Create playlist in database

    Args:
        user_id (str): User ID
        playlist_name (str): Playlist Name
        tracks (List[str]): Track IDs

    Returns:
        str: Playlist ID
    """
    playlist = {"playlist_name": playlist_name, "user_id": user_id, "tracks": tracks}
    playlist["time"] = datetime.now()
    return db["playlists"].insert_one(playlist).inserted_id


def delete_playlist(playlist_id: str, db: MongoClient) -> None:
    """Deletes Playlist from the database.

    Args:
        playlist_id (str): Playlist ID.
    """
    db["playlists"].delete_one({"_id": playlist_id})


def update_playlist_by_id(
    playlist_id: str,
    db: MongoClient,
    playlist_name: Optional[str] = None,
    tracks: Optional[List[str]] = None,
) -> None:
    """Updates Playlist in the database.

    Args:
        playlist_id (str): Playlist ID.
        playlist_name (Optional[str]): Playlist Name.
        tracks (Optional[List[str]]): Track IDs.

    Returns:
        Nones
    """
    # if playlist_name is None, update only tracks
    if playlist_name is None:
        return db.update_one(
            {"_id": playlist_id}, {"$set": {"tracks": tracks, "time": datetime.now()}}
        )
    # if tracks is None, update only playlist_name
    if tracks is None:
        return db.update_one(
            {"_id": playlist_id},
            {"$set": {"playlist_name": playlist_name, "time": datetime.now()}},
        )
    # if both playlist_name and tracks are not None, update both
    return db.update_one(
        {"_id": playlist_id},
        {
            "$set": {
                "playlist_name": playlist_name,
                "tracks": tracks,
                "time": datetime.now(),
            }
        },
    )


def get_track(track_id: str, db: MongoClient) -> Dict | None:
    """Searches database for Track with Track ID.

    Args:
        track_id (str): Track ID.

    Returns:
        Dict: Track Object or None if not found.
    """
    return db["tracks"].find_one({"_id": track_id})


def get_track_by_name_artist(
    track_name: str, artist_name: str, db: MongoClient
) -> Dict | None:
    """Searches database for Track with Track Name and Artist Name.

    Args:
        track_name (str): Track Name.
        artist_name (str): Artist Name.

    Returns:
        Dict: Track Object or None if not found.
    """
    return db["tracks"].find_one(
        {"track.track_name": track_name, "track.artist_name": artist_name}
    )


def create_track(track: Dict[str, str], db: MongoClient) -> str:
    """Creates Track in the database

    Args:
        track (Dict[str, str]): Track

    Returns:
        str: Track ID
    """
    track["time"] = datetime.now()
    return db["tracks"].insert_one(track).inserted_id


def update_track(track_id: str, track: Dict[str, str], db: MongoClient) -> None:
    """Updates Track in the database

    Args:
        track_id (str): Track ID
        track (Dict[str, str]): Track
    """
    db["tracks"].update_one({"_id": track_id}, {"$set": track, "time": datetime.now()})


def delete_track(track_id: str, db: MongoClient) -> None:
    """Deletes Track from the database

    Args:
        track_id (str): Track ID
    """
    db["tracks"].delete_one({"_id": track_id})


# aggregations


def get_playlist_with_tracks(playlist_name: str, db: MongoClient) -> Dict | None:
    """Searches database for Playlist with Playlist Name.

    Args:
        playlist_name (str): Playlist Name.

    Returns:
        Dict: Playlist Object or None if not found.
    """
    return (
        db["playlists"]
        .aggregate(
            [
                {"$match": {"playlist_name": f"{playlist_name}"}},
                {
                    "$lookup": {
                        "from": "tracks",
                        "localField": "tracks",
                        "foreignField": "_id",
                        "as": "linkedTracks",
                    }
                },
                {
                    "$set": {
                        "tracks": {
                            "$map": {
                                "input": "$tracks",
                                "as": "t",
                                "in": {
                                    "$first": {
                                        "$filter": {
                                            "input": "$linkedTracks",
                                            "cond": {"$eq": ["$$t", "$$this._id"]},
                                        }
                                    }
                                },
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "tracks.track_name": 1,
                        "tracks.artist_name": 1,
                        "tracks.album_name": 1,
                        "tracks.spotify": 1,
                        "user_id": 1,
                        "playlist_name": 1,
                    }
                },
            ]
        )
        .next()
    )
