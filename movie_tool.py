from collections import defaultdict
from datetime import datetime, timedelta
from fetcher import TMDBFetcher
import copy
import csv

class MovieDataTool:
    def __init__(self):
        self.fetcher = TMDBFetcher()
        self.data = []
        self.genres = {}
        self._initial_data = []

    def fetch_data(self):
        self.fetcher.fetch_all()
        self.data = self.fetcher.data
        self.genres = self.fetcher.genres
        self._initial_data = copy.deepcopy(self.data)

    def get_all_data(self):
        return self.data

    def get_movies_by_step(self):
        return self.data[3:20:4]

    def get_most_popular_title(self):
        return max(
            self.data, key=lambda m: m['popularity']
        )['title']

    def search_by_keywords(self, *keywords):
        return [
            movie['title'] for movie in self.data
            if 'overview' in movie and any(
                kw.lower() in movie['overview'].lower() for kw in keywords
            )
        ]

    def get_unique_genres(self):
        return frozenset(
            self.genres.get(g, g) 
            for movie in self.data
            for g in movie['genre_ids']
        )

    def delete_by_genre(self, genre_id):
        self.data = [
            m for m in self.data if genre_id not in m['genre_ids']
        ]

    def get_most_common_genres(self):
        genre_count = defaultdict(int)
        for movie in self.data:
            for g in movie['genre_ids']:
                genre_count[g] += 1
        return sorted(
            [(self.genres.get(k, k), v) for k, v in genre_count.items()],
            key=lambda x: x[1], reverse=True
            
        )

    def get_genre_based_pairs(self):
        groups = defaultdict(list)
        for movie in self.data:
            for genre in movie['genre_ids']:
                groups[genre].append(movie['title'])
        return frozenset(
            pair
            for titles in groups.values()
            for pair in zip(titles[::2], titles[1::2])
        )

    def get_initial_and_modified_data(self):
        modified = copy.deepcopy(self._initial_data)
        for movie in modified:
            if movie['genre_ids']:
                movie['genre_ids'][0] = 22
        return self._initial_data, modified

    def get_structured_movie_data(self):
        result = []
        for movie in self._initial_data:
            try:
                title = movie['title']
                popularity = round(float(movie.get('popularity', 0)), 1)
                score = int(movie.get('vote_average', 0))
                release_date = datetime.strptime(
                    movie.get('release_date', '2000-01-01'),
                    '%Y-%m-%d'
                )
                last_day = release_date + timedelta(weeks=10)
                result.append({
                    'title': title,
                    'popularity': popularity,
                    'score': score,
                    'last_day_in_cinema': last_day.strftime('%Y-%m-%d')
                })
            except Exception:
                continue
        return sorted(result, key=lambda x: (-x['score'], -x['popularity']))

    def write_structured_data_to_csv(self, filepath):
        structured_data = self.get_structured_movie_data()
        
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=structured_data[0].keys())
            writer.writeheader()
            writer.writerows(structured_data)
