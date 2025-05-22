from bson import ObjectId
from pymongo import MongoClient
from typing import Dict, Any, List, Optional
from fastapi.encoders import jsonable_encoder
from app.models.order import OrderModel
from app.repository.base_repository import BaseRepository

class OrderRepository(BaseRepository):
    """
    OrderRepository provides methods to interact with the orders collection in MongoDB.
    Inherits from BaseRepository and provides basic CRUD operations.
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
        Retrieve orders from the orders collection with optional filtering, pagination, and sorting.

        Returns:
            Tuple[List[OrderModel], int]: List of orders and total count.
        """
        query = filter or {}
        cursor = self.database.orders.find(query)
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.skip(skip).limit(limit)
        orders = [OrderModel(**doc) for doc in cursor]
        total = self.database.orders.count_documents(query)
        return orders, total

    def get_by_id(self, order_id: str) -> Optional[OrderModel]:
        """
        Retrieve an order by its ID.

        Args:
            order_id (str): The ID of the order to retrieve.

        Returns:
            Optional[OrderModel]: The order if found, otherwise None.
        """
        order = self.database.orders.find_one({"_id": ObjectId(order_id)})
        if order:
            return OrderModel(**order)
        return None
    
    def create_new_order(self, order_data: OrderModel) -> OrderModel:
        """
        Create a new order in the orders collection.

        Args:
            order_data (OrderModel): The order data to insert.

        Returns:
            OrderModel: The created order.
        """
        #order_data.id = ObjectId()
        model_in_json = jsonable_encoder(order_data)
        
        model_in_json["_id"] = ObjectId() 
        if "customerId" in model_in_json and not isinstance(model_in_json["customerId"], ObjectId):
            model_in_json["customerId"] = ObjectId(model_in_json["customerId"])

        result = self.database.orders.insert_one(model_in_json)
        created_order = self.database.orders.find_one({"_id": result.inserted_id})
        return OrderModel(**created_order)

    def get_orders_by_customer_id(self, customer_id: str) -> List[OrderModel]:
        """
        Retrieve all orders for a specific customer by their ID.

        Args:
            customer_id (str): The ID of the customer.

        Returns:
            List[OrderModel]: List of orders for the specified customer.
        """
        orders = self.database.orders.find({"customerId": ObjectId(customer_id)})
        return [OrderModel(**order) for order in orders]