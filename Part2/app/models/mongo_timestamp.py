from pydantic import BaseModel

class MongoTimestamp(BaseModel):
    t: int
    i: int