from typing import List
from .models import Course
import math

def calculate_relevance(course: Course, topic: str) -> float:
    """
    Calculates a heuristic relevance score.
    Higher is better.
    """
    score = 0.0
    
    # 1. Text match (Simple)
    topic_lower = topic.lower()
    if topic_lower in course.title.lower():
        score += 10
    
    # 2. Rating & Reviews
    # Log scale for reviews to avoid skewing by massive numbers
    # Rating is typically 0-5
    rating = course.rating or 0
    reviews = course.review_count or 0
    
    # Heuristic: Rating * log10(reviews + 1)
    # A 4.8 with 100 reviews ~= 4.8 * 2 = 9.6
    # A 4.5 with 10000 reviews ~= 4.5 * 4 = 18
    # This favors popular courses, which is usually a good proxy for "relevance" in these marketplaces.
    popularity_score = rating * math.log10(reviews + 1)
    
    score += popularity_score
    
    return score

def rank_courses(courses: List[Course], topic: str) -> List[Course]:
    for course in courses:
        course.relevance_score = calculate_relevance(course, topic)
    
    # Sort descending
    return sorted(courses, key=lambda x: x.relevance_score, reverse=True)
