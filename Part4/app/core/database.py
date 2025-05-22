from typing import Callable
from contextlib import contextmanager
from fastapi import FastAPI
from pymongo import MongoClient
from app.core.config import settings


class MongoDB:
    """
    MongoDB class to hold a single MongoClient instance for the application.
    """
    client: MongoClient = None

# Create a global MongoDB instance
mongo_db = MongoDB()

def mongodb_startup(app: FastAPI) -> None:
    """
    Establishes a connection to the MongoDB database on application startup.

    Args:
        app (FastAPI): The FastAPI application instance.

    This function sets the MongoDB client instance in the app state, allowing 
    other parts of the application to access the MongoDB connection.
    """
    print('connect to the MongoDB...')
    # Initialize MongoDB client with connection pooling
    mongo_client = MongoClient(
        settings.MONGODB_URL,
        MaxPoolSize = settings.MONGODB_MAX_CONNECTIONS_COUNT,
        MinPoolSize = settings.MONGODB_MIN_CONNECTIONS_COUNT,
    )
    mongo_db.client = mongo_client
    app.state.mongo_client = mongo_client
    print('MongoDB connection succeeded! ')

def mongodb_shutdown(app: FastAPI) -> None:
    """
    Closes the MongoDB connection on application shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.

    Ensures that the MongoDB connection is gracefully closed when the application stops.
    """
    print('Closing the MongoDB connection...')
    app.state.mongo_client.close()
    print('MondoDB connection closed! ')


def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Creates an application startup handler that connects to MongoDB.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        Callable: A function that starts the MongoDB connection on application startup.
    """
    def start_app() -> None:
        mongodb_startup(app)
    return start_app

def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    Creates an application shutdown handler that disconnects from MongoDB.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        Callable: A function that stops the MongoDB connection on application shutdown.
    """

    def stop_app() -> None:
        mongodb_shutdown(app)
    return stop_app