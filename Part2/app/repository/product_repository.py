from bson import ObjectId
from pymongo import MongoClient
from typing import Dict, Any, List, Optional

from app.models.product import ProductModel
from app.repository.base_repository import BaseRepository

class ProductRepository(BaseRepository):
    """
    ProductRepository is a class that provides methods to interact with the product collection in MongoDB.
    It inherits from BaseRepository and provides basic CRUD operations.
    """
    def __init__(self, mongo: MongoClient):
        self._mongo = mongo
        super().__init__(mongo)

    def get_all(
        self,
        filter: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 10,
        sort: Optional[List[tuple]] = None
    ):
        """
        Retrieve products from the products collection with optional filtering, pagination, and sorting.

        Returns:
            Tuple[List[ProductModel], int]: List of products and total count.
        """
        query = filter or {}
        cursor = self.database.products.find(query)
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.skip(skip).limit(limit)
        products = [ProductModel(**doc) for doc in cursor]
        total = self.database.products.count_documents(query)
        return products, total
    
    def get_by_id(self, product_id: str) -> Optional[ProductModel]:
        """
        Retrieve a product by its ID.

        Args:
            product_id (str): The ID of the product to retrieve.

        Returns:
            Optional[ProductModel]: The product if found, otherwise None.
        """
        product = self.database.products.find_one({"_id": ObjectId(product_id)})
        if product:
            return ProductModel(**product)
        return None