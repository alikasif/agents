from pydantic import BaseModel, Field
from typing import List, Optional

class Course(BaseModel):
    title: str
    id: Optional[str] = None
    url: str
    platform: str
    price: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    instructor: Optional[str] = None
    # Details gathered from the specific course page
    description: Optional[str] = None
    what_you_will_learn: Optional[List[str]] = Field(default_factory=list)
    curriculum_preview: Optional[List[str]] = Field(default_factory=list) # Top headings
    relevance_score: Optional[float] = 0.0

class SearchResult(BaseModel):
    query: str
    courses: List[Course]
