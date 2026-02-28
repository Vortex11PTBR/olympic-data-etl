"""
API Client Utilities for Olympic Data Ingestion.

Provides clients for various Olympic data sources: Olympics API, Wikidata, OpenOlympics.
"""

import logging
import time
from typing import List, Dict, Optional
from datetime import datetime
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def retry_on_exception(max_retries: int = 3, backoff_factor: float = 0.3):
    """Decorator for retrying failed API calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, Exception) as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Max retries reached for {func.__name__}: {e}")
                        raise
                    wait_time = backoff_factor * (2 ** (retries - 1))
                    logger.warning(
                        f"Retry {retries}/{max_retries} for {func.__name__} after {wait_time}s"
                    )
                    time.sleep(wait_time)
        return wrapper
    return decorator


class BaseAPIClient:
    """Base client for all API sources."""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.session = self._create_session(max_retries)

    @staticmethod
    def _create_session(max_retries: int = 3) -> requests.Session:
        """Create requests session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    @retry_on_exception(max_retries=3)
    def _get(self, url: str, **kwargs) -> Dict:
        """Make GET request with retry logic."""
        response = self.session.get(url, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close the session."""
        self.session.close()


class OlympicsAPIClient(BaseAPIClient):
    """Client for Olympics API (Olympic.net and similar sources)."""

    def __init__(self, base_url: str = "https://api.olym.dev", timeout: int = 30):
        super().__init__(timeout)
        self.base_url = base_url.rstrip("/")

    def get_athletes(self, year: Optional[int] = None, country: Optional[str] = None) -> List[Dict]:
        """
        Fetch athlete data.

        Args:
            year: Filter by Olympic year
            country: Filter by country code

        Returns:
            List of athlete records
        """
        try:
            params = {}
            if year:
                params["year"] = year
            if country:
                params["country"] = country

            response = self._get(f"{self.base_url}/athletes", params=params)
            athletes = response.get("data", [])
            logger.info(f"Fetched {len(athletes)} athletes")
            return athletes
        except Exception as e:
            logger.error(f"Error fetching athletes: {e}")
            return []

    def get_events(self, year: Optional[int] = None, sport: Optional[str] = None) -> List[Dict]:
        """
        Fetch event data.

        Args:
            year: Filter by Olympic year
            sport: Filter by sport type

        Returns:
            List of event records
        """
        try:
            params = {}
            if year:
                params["year"] = year
            if sport:
                params["sport"] = sport

            response = self._get(f"{self.base_url}/events", params=params)
            events = response.get("data", [])
            logger.info(f"Fetched {len(events)} events")
            return events
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return []

    def get_medals(self, year: Optional[int] = None, country: Optional[str] = None) -> List[Dict]:
        """
        Fetch medal data.

        Args:
            year: Filter by Olympic year
            country: Filter by country code

        Returns:
            List of medal records
        """
        try:
            params = {}
            if year:
                params["year"] = year
            if country:
                params["country"] = country

            response = self._get(f"{self.base_url}/medals", params=params)
            medals = response.get("data", [])
            logger.info(f"Fetched {len(medals)} medals")
            return medals
        except Exception as e:
            logger.error(f"Error fetching medals: {e}")
            return []

    def get_results(self, event_id: str) -> List[Dict]:
        """
        Fetch event results.

        Args:
            event_id: The event ID

        Returns:
            List of result records
        """
        try:
            response = self._get(f"{self.base_url}/events/{event_id}/results")
            results = response.get("data", [])
            logger.info(f"Fetched {len(results)} results for event {event_id}")
            return results
        except Exception as e:
            logger.error(f"Error fetching results for event {event_id}: {e}")
            return []


class WikidataClient(BaseAPIClient):
    """Client for Wikidata SPARQL endpoint."""

    def __init__(self, timeout: int = 60):
        super().__init__(timeout)
        self.base_url = "https://query.wikidata.org/sparql"

    def query(self, sparql_query: str) -> List[Dict]:
        """
        Execute a SPARQL query against Wikidata.

        Args:
            sparql_query: SPARQL query string

        Returns:
            List of result dictionaries
        """
        try:
            response = self._get(
                self.base_url,
                params={"query": sparql_query, "format": "json"},
            )
            bindings = response.get("results", {}).get("bindings", [])
            logger.info(f"Wikidata query returned {len(bindings)} results")
            return bindings
        except Exception as e:
            logger.error(f"Wikidata query error: {e}")
            return []

    def get_athlete_info(self, athlete_name: str) -> List[Dict]:
        """
        Get athlete information from Wikidata.

        Args:
            athlete_name: Athlete name

        Returns:
            List of athlete records with metadata
        """
        query = f"""
        SELECT ?athlete ?name ?countryLabel ?birthDate ?occupationLabel
        WHERE {{
            ?athlete rdfs:label "{athlete_name}"@en.
            ?athlete wdt:P31 wd:Q5.
            ?athlete rdfs:label ?name.
            OPTIONAL {{ ?athlete wdt:P27 ?country. }}
            OPTIONAL {{ ?athlete wdt:P569 ?birthDate. }}
            OPTIONAL {{ ?athlete wdt:P106 ?occupation. }}
            SERVICE wikibase:label {{ 
                bd:serviceParam wikibase:language "en".
                ?country rdfs:label ?countryLabel.
                ?occupation rdfs:label ?occupationLabel.
            }}
        }}
        LIMIT 10
        """
        return self.query(query)

    def get_country_info(self, country_code: str) -> Dict:
        """
        Get country information from Wikidata.

        Args:
            country_code: ISO 3166-1 alpha-3 country code

        Returns:
            Country metadata dictionary
        """
        query = f"""
        SELECT ?country ?countryLabel ?population ?area ?region ?continentLabel
        WHERE {{
            ?country wdt:P297 "{country_code}".
            OPTIONAL {{ ?country wdt:P1082 ?population. }}
            OPTIONAL {{ ?country wdt:P2046 ?area. }}
            OPTIONAL {{ ?country wdt:P131 ?region. }}
            OPTIONAL {{ ?country wdt:P30 ?continent. }}
            SERVICE wikibase:label {{ 
                bd:serviceParam wikibase:language "en".
                ?country rdfs:label ?countryLabel.
                ?continent rdfs:label ?continentLabel.
            }}
        }}
        LIMIT 1
        """
        results = self.query(query)
        return results[0] if results else {}


class OpenOlympicsClient(BaseAPIClient):
    """Client for OpenOlympics API."""

    def __init__(self, base_url: str = "https://api.openolympics.org", timeout: int = 30):
        super().__init__(timeout)
        self.base_url = base_url.rstrip("/")

    def get_venues(self, year: Optional[int] = None) -> List[Dict]:
        """
        Fetch venue data.

        Args:
            year: Filter by Olympic year

        Returns:
            List of venue records
        """
        try:
            params = {"year": year} if year else {}
            response = self._get(f"{self.base_url}/venues", params=params)
            venues = response.get("data", [])
            logger.info(f"Fetched {len(venues)} venues")
            return venues
        except Exception as e:
            logger.error(f"Error fetching venues: {e}")
            return []

    def get_sports(self) -> List[Dict]:
        """
        Fetch sport categories.

        Returns:
            List of sport records
        """
        try:
            response = self._get(f"{self.base_url}/sports")
            sports = response.get("data", [])
            logger.info(f"Fetched {len(sports)} sports")
            return sports
        except Exception as e:
            logger.error(f"Error fetching sports: {e}")
            return []

    def get_countries(self) -> List[Dict]:
        """
        Fetch countries that participated in Olympics.

        Returns:
            List of country records
        """
        try:
            response = self._get(f"{self.base_url}/countries")
            countries = response.get("data", [])
            logger.info(f"Fetched {len(countries)} countries")
            return countries
        except Exception as e:
            logger.error(f"Error fetching countries: {e}")
            return []


class APIAggregator:
    """Aggregate data from multiple Olympic data sources."""

    def __init__(self):
        self.olympics_client = OlympicsAPIClient()
        self.wikidata_client = WikidataClient()
        self.openolympics_client = OpenOlympicsClient()

    def fetch_olympics_data(self, year: Optional[int] = None) -> Dict[str, List]:
        """
        Fetch comprehensive Olympic data from all sources.

        Args:
            year: Filter by Olympic year (optional)

        Returns:
            Dictionary with all collected data
        """
        logger.info(f"Fetching Olympic data for year {year or 'all years'}")

        data = {
            "athletes": self.olympics_client.get_athletes(year=year),
            "events": self.olympics_client.get_events(year=year),
            "medals": self.olympics_client.get_medals(year=year),
            "venues": self.openolympics_client.get_venues(year=year),
            "sports": self.openolympics_client.get_sports(),
            "countries": self.openolympics_client.get_countries(),
            "fetched_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Retrieved {sum(len(v) for k, v in data.items() if isinstance(v, list))} "
            f"records from {len(data)} sources"
        )

        return data

    def enrich_athletes_with_wikidata(self, athletes: List[Dict]) -> List[Dict]:
        """
        Enrich athlete data with Wikidata information.

        Args:
            athletes: List of athlete records

        Returns:
            Enriched athlete records
        """
        enriched = []
        for athlete in athletes:
            name = athlete.get("name", "")
            if name:
                wikidata_info = self.wikidata_client.get_athlete_info(name)
                if wikidata_info:
                    athlete["wikidata"] = wikidata_info[0]
            enriched.append(athlete)
        logger.info(f"Enriched {len(enriched)} athletes with Wikidata")
        return enriched

    def close(self):
        """Close all API sessions."""
        self.olympics_client.close()
        self.wikidata_client.close()
        self.openolympics_client.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Example usage
    aggregator = APIAggregator()
    
    # Fetch data
    data = aggregator.fetch_olympics_data(year=2020)
    print(f"Fetched data: {len(data)} sources")

    # Clean up
    aggregator.close()
