import asyncio
from src.models import Course
from src.browser import BrowserManager
from src.scrapers.udemy import UdemyScraper
from src.scrapers.coursera import CourseraScraper
from src.ranker import rank_courses
import argparse
import sys

async def main(topic: str):
    print(f"Searching for courses on topic: '{topic}'...")
    
    courses: list[Course] = []
    
    async with BrowserManager(headless=True) as browser:
        udemy = UdemyScraper(browser)
        coursera = CourseraScraper(browser)
        
        # 1. Search in parallel
        print("Scraping search results...")
        results = await asyncio.gather(
            udemy.search(topic, limit=5),
            coursera.search(topic, limit=5)
        )
        
        udemy_courses = results[0]
        coursera_courses = results[1]
        
        all_courses = udemy_courses + coursera_courses
        print(f"Found {len(all_courses)} initial courses.")
        
        if not all_courses:
            print("No courses found.")
            return

        # 2. Rank preliminarily to pick top candidates for deep dive
        # We don't want to visit 10 pages deep if we only want the best.
        ranked_initial = rank_courses(all_courses, topic)
        top_picks = ranked_initial[:6] # Top 6 total
        
        print(f"Deep scraping details for top {len(top_picks)} courses...")
        
        # 3. Get Details for top picks
        # We can't easily parallelize sharing the SAME browser instance across pages perfectly without 
        # risking detection or resource limits, but Playwright handles multiple pages well.
        # Let's do it sequentially per scraper to be safe, or just parallelize tasks.
        
        detail_tasks = []
        for course in top_picks:
            if course.platform == 'Udemy':
                detail_tasks.append(udemy.get_details(course))
            else:
                detail_tasks.append(coursera.get_details(course))
        
        detailed_courses = await asyncio.gather(*detail_tasks)
        
        # 4. Final Rank
        final_list = rank_courses(detailed_courses, topic)
        
        # 5. Output
        print("\n=== Recommended Courses ===\n")
        for i, course in enumerate(final_list, 1):
            print(f"{i}. [{course.platform}] {course.title}")
            print(f"   Rating: {course.rating} ({course.review_count} reviews)")
            print(f"   Instructor: {course.instructor}")
            print(f"   URL: {course.url}")
            print(f"   Description: {course.description[:150]}...")
            print("")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Course Browser Agent")
    parser.add_argument("topic", help="Topic to search for")
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        # manual run for debug
        asyncio.run(main("Python"))
    else:
        asyncio.run(main(args.topic))
