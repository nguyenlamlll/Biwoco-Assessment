# Dependency to retrieve the MongoClient from the request
from typing import AsyncGenerator, Callable, Type
from fastapi import Depends, Request
from pymongo import MongoClient

from app.repository.base_repository import BaseRepository


def _get_mongo_client(request: Request) -> MongoClient:
    return request.app.state.mongo_client


# Get a repository instance with the MongoDB client
def get_mongodb_repo(repo_type: Type[BaseRepository]) -> Callable:
    async def _get_repo(
         mongo_client: MongoClient = Depends(_get_mongo_client),
    ) -> AsyncGenerator[BaseRepository, None]:
        yield repo_type(mongo_client)

    return _get_repo