import urllib.parse
from typing import List
from ..models import Course
from .base import BaseScraper

class CourseraScraper(BaseScraper):
    BASE_URL = "https://www.coursera.org"

    async def search(self, query: str, limit: int = 5) -> List[Course]:
        page = await self.browser_manager.new_page()
        encoded_query = urllib.parse.quote(query)
        url = f"{self.BASE_URL}/search?query={encoded_query}"

        try:
            await page.goto(url, wait_until="domcontentloaded")
            try:
                # Coursera uses algolia or similar, resulting in lists
                await page.wait_for_selector('ul.ais-InfiniteHits-list, div[class*="css-"]', timeout=10000)
            except:
                print("Timeout waiting for Coursera results.")
                return []

            course_elements = await page.evaluate(f'''() => {{
                const courses = [];
                // Selectors for Coursera change often. Using generic checks.
                const cards = document.querySelectorAll('li.ais-InfiniteHits-item, div.cds-ProductCard-content');
                
                for (let i = 0; i < Math.min(cards.length, {limit}); i++) {{
                    const card = cards[i];
                    const titleEl = card.querySelector('h2, h3, a[aria-label]');
                    if (!titleEl) continue;
                    
                    const title = titleEl.innerText;
                    const linkEl = card.querySelector('a');
                    const url = linkEl ? linkEl.href : "";
                    
                    // Rating
                    const ratingEl = card.querySelector('span[class*="cds-119 css-11uuo4b"]'); // Very specific, likely flaky. 
                    // Better to look for text pattern "4.8"
                    const textContent = card.innerText;
                    const ratingMatch = textContent.match(/([0-9]\.[0-9])\s*stars?/);
                    const rating = ratingMatch ? parseFloat(ratingMatch[1]) : 0.0;
                    
                    // Review count
                    const reviewMatch = textContent.match(/\(([0-9,kK]+)\s*reviews?\)/) || textContent.match(/([0-9,kK]+)\s*reviews?/);
                    let reviewCount = 0;
                    if (reviewMatch) {{
                        let numStr = reviewMatch[1].toLowerCase().replace(',', '');
                        if (numStr.includes('k')) {{
                            reviewCount = parseFloat(numStr.replace('k', '')) * 1000;
                        }} else {{
                            reviewCount = parseInt(numStr);
                        }}
                    }}
                    
                    // Instructor (often just partner name like "IBM" or "Yale")
                    const partnerEl = card.querySelector('span.cds-ProductCard-partnerNames');
                    const instructor = partnerEl ? partnerEl.innerText : "Coursera Partner";

                    courses.push({{
                        title: title,
                        url: url,
                        platform: 'Coursera',
                        rating: rating,
                        review_count: reviewCount,
                        instructor: instructor
                    }});
                }}
                return courses;
            }}''')

            courses = []
            for c in course_elements:
                courses.append(Course(**c))
            
            return courses

        except Exception as e:
            print(f"Error scraping Coursera: {e}")
            return []
        finally:
            await page.close()

    async def get_details(self, course: Course) -> Course:
        page = await self.browser_manager.new_page()
        try:
            await page.goto(course.url, wait_until="domcontentloaded")
            # Wait for meaningful content
            await page.wait_for_selector('div.content', timeout=5000) # Generic fallback

            details = await page.evaluate('''() => {
                const descEl = document.querySelector('div.description, div.content-inner');
                const description = descEl ? descEl.innerText.substring(0, 1000) : "";

                const learnEls = document.querySelectorAll('div.Syllabus, ul.bullets li');
                const what_you_will_learn = Array.from(learnEls).slice(0, 5).map(el => el.innerText);

                return {
                    description,
                    what_you_will_learn
                };
            }''')

            course.description = details['description']
            course.what_you_will_learn = details['what_you_will_learn']
            
        except Exception as e:
            print(f"Error getting details for {course.title} on Coursera: {e}")
            # Don't fail the whole course if details fail
        finally:
            await page.close()
        
        return course
