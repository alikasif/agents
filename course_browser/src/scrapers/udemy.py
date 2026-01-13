import urllib.parse
from typing import List
from ..models import Course
from .base import BaseScraper
import asyncio

class UdemyScraper(BaseScraper):
    BASE_URL = "https://www.udemy.com"

    async def search(self, query: str, limit: int = 5) -> List[Course]:
        page = await self.browser_manager.new_page()
        encoded_query = urllib.parse.quote(query)
        url = f"{self.BASE_URL}/courses/search/?q={encoded_query}"
        
        try:
            await page.goto(url, wait_until="domcontentloaded")
            # Udemy load can be slow or use skeleton loaders
            try:
                await page.wait_for_selector('h3[data-purpose="course-title-url"]', timeout=10000)
            except:
                print("Timeout waiting for Udemy course cards. Might be a captcha or empty results.")
                return []

            # Extract course elements
            # The selector might vary, but h3[data-purpose="course-title-url"] is usually consistent for the title
            course_elements = await page.evaluate(f'''() => {{
                const courses = [];
                const cards = document.querySelectorAll('div.course-card-module--container--3oS-F, div[class*="course-card-module--container"]'); 
                // Fallback to searching for the titles if the container class changes
                const titles = document.querySelectorAll('h3[data-purpose="course-title-url"]');
                
                // Let's iterate over titles to find their parent containers or just extract from there
                const items = titles.length > 0 ? titles : [];
                
                for (let i = 0; i < Math.min(items.length, {limit}); i++) {{
                    const titleEl = items[i];
                    const container = titleEl.closest('div[class*="course-card-module--container"]') || titleEl.closest('a');
                    
                    const title = titleEl.innerText;
                    const url = titleEl.closest('a').href;
                    
                    // Rating
                    const ratingEl = container.querySelector('span[data-purpose="rating-number"]');
                    const rating = ratingEl ? parseFloat(ratingEl.innerText) : 0.0;
                    
                    // Reviews
                    const reviewsEl = container.querySelector('span[aria-label*="reviews"], span[class*="course-card-module--reviews-text"]');
                    let reviewCount = 0;
                    if (reviewsEl) {{
                        const text = reviewsEl.innerText;
                        const match = text.match(/([0-9,]+)/);
                        if (match) {{
                            reviewCount = parseInt(match[1].replace(/,/g, ''));
                        }}
                    }}
                    
                    // Instructor
                    const instructorEl = container.querySelector('div[class*="course-card-module--instructor"]');
                    const instructor = instructorEl ? instructorEl.innerText : "";

                    courses.push({{
                        title: title,
                        url: url,
                        platform: 'Udemy',
                        rating: rating,
                        review_count: reviewCount,
                        instructor: instructor
                    }});
                }}
                return courses;
            }}''')

            # Convert to Pydantic models
            courses = []
            for c in course_elements:
                courses.append(Course(**c))
            
            return courses

        except Exception as e:
            print(f"Error scraping Udemy: {e}")
            return []
        finally:
            await page.close()

    async def get_details(self, course: Course) -> Course:
        page = await self.browser_manager.new_page()
        try:
            await page.goto(course.url, wait_until="domcontentloaded")
            await page.wait_for_selector('div[data-purpose="course-landing-page"]', timeout=5000)

            details = await page.evaluate('''() => {
                const descEl = document.querySelector('div[data-purpose="course-description"], div[class*="description--description"]');
                const description = descEl ? descEl.innerText.substring(0, 1000) : ""; # Limit length

                const learnEls = document.querySelectorAll('ul[class*="what-you-will-learn--objectives-list"] li');
                const what_you_will_learn = Array.from(learnEls).map(el => el.innerText);

                return {
                    description,
                    what_you_will_learn
                };
            }''')

            course.description = details['description']
            course.what_you_will_learn = details['what_you_will_learn']
            
        except Exception as e:
            print(f"Error getting details for {course.title}: {e}")
        finally:
            await page.close()
        
        return course
