from datetime import datetime, timezone
from typing import Optional
from db.models import remove_timezone
import uuid
from pydantic import BaseModel, Field


class ReviewModel(BaseModel):
    id: uuid.UUID
    rating: int = Field(ge=1, le=5)
    review_text : str  
    user_id : Optional[uuid.UUID]
    book_id : Optional[uuid.UUID]
    created_at: datetime 
    
 
class ReviewCreateModel(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_text : str
    created_at : datetime = Field(default_factory=lambda: remove_timezone(datetime.now(timezone.utc)))