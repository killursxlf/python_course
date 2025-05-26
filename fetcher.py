import copy
import requests
from typing import List, Dict, Any
from config import Settings

class TMDBFetcher:
    def __init__(self):
        self.pages_to_fetch = Settings.PAGES_TO_FETCH
        self.base_url = Settings.BASE_URL
        self.genre_url = Settings.GENRE_URL
        token = Settings.TOKEN
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        self.data: List[Dict[str, Any]] = []
        self.genres: Dict[int, str] = {}
        self._initial_data: List[Dict[str, Any]] = []

    def _get_json(self, url: str) -> Dict[str, Any]:
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def fetch_genres(self) -> None:
        payload = self._get_json(self.genre_url)
        self.genres = {g['id']: g['name'] for g in payload.get('genres', [])}

    def fetch_movies(self) -> None:
        for page in range(1, self.pages_to_fetch + 1):
            url = self.base_url.format(page)
            payload = self._get_json(url)
            self.data.extend(payload.get('results', []))

    def fetch_all(self) -> None:
        self.fetch_genres()
        self.fetch_movies()
        self._initial_data = copy.deepcopy(self.data)


