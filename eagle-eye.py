"""
Eagle-Eye Web Scanner - KIIT CSE Faculty Scraper
-----------------------------------------------
Bypasses protection and extracts complete faculty data
"""
import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import random
from urllib.parse import urljoin

class FacultyScraper:
    def __init__(self, output_file="cse_faculty.csv"):
        self.output_file = output_file
        self.session = requests.Session()
        self._configure_session()
        self._prepare_storage()
        self.retry_count = 3
        self.request_timeout = 10

    def _configure_session(self):
        """Configure browser-mimicking session with rotating fingerprints"""
        self.session.headers = {
            "authority": "cse.kiit.ac.in",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "dnt": "1",
            "referer": "https://kiit.ac.in/",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": self._get_random_user_agent()
        }
        self.session.cookies.update({
            'cookie_consent': 'true',
            'session_token': 'dummy_' + str(random.randint(1000, 9999))
        })

    def _prepare_storage(self):
        """Initialize CSV with comprehensive headers"""
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Name', 'Designation', 'Qualification',
                    'Research Interest', 'Email', 'Phone',
                    'Experience', 'Image URL', 'Google Scholar',
                    'LinkedIn', 'Other Links', 'Profile URL'
                ])

    def _get_random_user_agent(self):
        """Return modern user agents with random selection"""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
        ]
        return random.choice(agents)

    def _random_delay(self):
        """Generate human-like random delays"""
        time.sleep(random.uniform(1.2, 3.5) + random.expovariate(1/1.2))

    def _decode_cf_email(self, encoded):
        """Decode Cloudflare email protection"""
        try:
            key = int(encoded[:2], 16)
            decoded = []
            for i in range(2, len(encoded), 2):
                decoded.append(chr(int(encoded[i:i+2], 16) ^ key))
            return ''.join(decoded)
        except Exception as e:
            print(f"Email decode error: {e}")
            return None

    def _make_request(self, url):
        """Request handling with retry logic"""
        for attempt in range(self.retry_count):
            try:
                self._random_delay()
                response = self.session.get(
                    url,
                    timeout=self.request_timeout,
                    headers={
                        **self.session.headers,
                        "user-agent": self._get_random_user_agent()
                    }
                )
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f"Attempt {attempt+1}: Bypassing 403...")
                    self._rotate_fingerprint()
                else:
                    print(f"HTTP Error {e.response.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {str(e)}")
                return None
        return None

    def _rotate_fingerprint(self):
        """Change session fingerprint to bypass blocking"""
        self.session.headers.update({
            "sec-ch-ua": f'"Not.A/Brand";v="24", "Chromium";v="{random.randint(120, 124)}", "Google Chrome";v="{random.randint(120, 124)}"',
            "user-agent": self._get_random_user_agent()
        })
        self.session.cookies.update({
            'session_token': 'dummy_' + str(random.randint(1000, 9999))
        })

    def _parse_faculty_card(self, card):
        """Extract data from individual faculty member card"""
        data = {
            'name': None,
            'designation': None,
            'qualification': None,
            'research_interest': None,
            'email': None,
            'phone': None,
            'experience': None,
            'image_url': None,
            'scholar': None,
            'linkedin': None,
            'other_links': [],
            'profile_url': None
        }

        try:
            # Name and Profile URL
            name_tag = card.find('h3', class_='elementor-heading-title')
            if name_tag:
                data['name'] = name_tag.get_text(strip=True)
                profile_link = name_tag.find_parent('a', href=True)
                if profile_link:
                    data['profile_url'] = urljoin("https://cse.kiit.ac.in", profile_link['href'])

            # Designation
            designation_tag = card.find('span', class_='designation')
            if designation_tag:
                data['designation'] = designation_tag.get_text(strip=True)

            # Qualifications
            qual_tag = card.find('div', class_='qualification')
            if qual_tag:
                data['qualification'] = ' | '.join([p.get_text(strip=True) for p in qual_tag.find_all('p')])

            # Research Interests
            research_tag = card.find('div', class_='research-interests')
            if research_tag:
                data['research_interest'] = research_tag.get_text(' | ', strip=True)

            # Contact Information
            contact_div = card.find('div', class_='faculty-contact')
            if contact_div:
                # Email
                email_tag = contact_div.find('span', class_='__cf_email__')
                if email_tag and 'data-cfemail' in email_tag.attrs:
                    data['email'] = self._decode_cf_email(email_tag['data-cfemail'])
                
                # Phone
                phone_tag = contact_div.find('span', class_='phone')
                if phone_tag:
                    data['phone'] = phone_tag.get_text(strip=True)

            # Image
            img_div = card.find('div', class_='elementor-image')
            if img_div and img_div.img:
                data['image_url'] = img_div.img.get('data-src') or img_div.img.get('src')

            # Social Links
            social_div = card.find('div', class_='social-media')
            if social_div:
                for link in social_div.find_all('a', href=True):
                    url = urljoin("https://cse.kiit.ac.in", link['href'])
                    if 'scholar.google' in url:
                        data['scholar'] = url
                    elif 'linkedin.com' in url:
                        data['linkedin'] = url
                    else:
                        data['other_links'].append(url)

        except Exception as e:
            print(f"Parsing error: {str(e)}")

        data['other_links'] = ' | '.join(data['other_links'])
        return data

    def scrape_faculty(self):
        """Main scraping controller"""
        base_url = "https://cse.kiit.ac.in/faculty/"
        print(f"🚀 Starting scrape/Eagling: {base_url}")

        response = self._make_request(base_url)
        if not response:
            print("❌ Critical: Failed to retrieve faculty page")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        faculty_cards = soup.find_all('div', class_='elementor-widget-wrap')
        
        if not faculty_cards:
            print("⚠️ No faculty cards found - check page structure")
            return

        print(f"🦅 Found {len(faculty_cards)} faculty members")

        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            for card in faculty_cards:
                faculty_data = self._parse_faculty_card(card)
                writer.writerow([
                    faculty_data['name'],
                    faculty_data['designation'],
                    faculty_data['qualification'],
                    faculty_data['research_interest'],
                    faculty_data['email'],
                    faculty_data['phone'],
                    faculty_data['experience'],
                    faculty_data['image_url'],
                    faculty_data['scholar'],
                    faculty_data['linkedin'],
                    faculty_data['other_links'],
                    faculty_data['profile_url']
                ])
                print(f"✅ Saved: {faculty_data['name'] or 'Unknown'}")

if __name__ == "__main__":
    scraper = FacultyScraper()
    scraper.scrape_faculty()
    print("\n🎉 Scraping complete! Data saved to:", os.path.abspath(scraper.output_file))