import os
from movie_tool import MovieDataTool  

def print_menu():
    print("""
=== MovieDataTool Menu ===
1. Set number of pages to fetch and load data
2. Show all movies
3. Get movies by step (3:20:4)
4. Get the most popular movie
5. Search by keywords
6. Show all unique genres
7. Delete movies by genre (ID)
8. Show most common genres
9. Show genre-based movie pairs
10. Show original and modified data (replace first genre_id with 22)
11. Show structured movie data (title, popularity, score, last_day_in_cinema)
12. Save structured data to CSV
0. Exit
""")

def require_data(func):
    """Decorator: if data not loaded, prints a message and does not call the function."""
    def wrapper(state):
        if state['tool'] is None:
            print("Please load data first (option 1).\n")
        else:
            return func(state)
    return wrapper

@require_data
def cmd_show_all(state):
    for m in state['tool'].get_all_data():
        print(f"{m.get('title')} ({m.get('release_date')})")
    print()

@require_data
def cmd_step(state):
    print(state['tool'].get_movies_by_step(), "\n")

@require_data
def cmd_popular(state):
    print("Most popular movie:", state['tool'].get_most_popular_title(), "\n")

@require_data
def cmd_search(state):
    kws = input("Enter keywords separated by spaces: ").split()
    results = state['tool'].search_by_keywords(*kws)
    print("Movies found:", len(results))
    for title in results:
        print("-", title)
    print()

@require_data
def cmd_unique_genres(state):
    print("Unique genres:", state['tool'].get_unique_genres(), "\n")

@require_data
def cmd_delete_genre(state):
    gid = input("Enter genre ID to delete: ").strip()
    try:
        before = len(state['tool'].get_all_data())
        state['tool'].delete_by_genre(int(gid))
        after = len(state['tool'].get_all_data())
        print(f"Deleted {before - after} movies.\n")
    except ValueError:
        print("Invalid genre ID.\n")

@require_data
def cmd_common_genres(state):
    for name, cnt in state['tool'].get_most_common_genres():
        print(f"{name}: {cnt}")
    print()

@require_data
def cmd_pairs(state):
    for a, b in state['tool'].get_genre_based_pairs():
        print(f"{a} ⇄ {b}")
    print()

@require_data
def cmd_initial_modified(state):
    orig, mod = state['tool'].get_initial_and_modified_data()
    print("Original first genre_ids:", orig[0]['genre_ids'])
    print("Modified first genre_ids:", mod[0]['genre_ids'], "\n")

@require_data
def cmd_structured(state):
    for rec in state['tool'].get_structured_movie_data():
        print(rec)
    print()

@require_data
def cmd_save_csv(state):
    path = input("Enter CSV file path (e.g., movies.csv): ").strip()
    try:
        state['tool'].write_structured_data_to_csv(path)
        print(f"Saved structured data to {path}\n")
    except Exception as e:
        print("Error writing CSV:", e, "\n")

def main():
    state = {'tool': None}

    commands = {
        "2": cmd_show_all,
        "3": cmd_step,
        "4": cmd_popular,
        "5": cmd_search,
        "6": cmd_unique_genres,
        "7": cmd_delete_genre,
        "8": cmd_common_genres,
        "9": cmd_pairs,
        "10": cmd_initial_modified,
        "11": cmd_structured,
        "12": cmd_save_csv,
    }

    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            try:
                pages = int(input("How many pages to fetch? ").strip())
                state['tool'] = MovieDataTool(pages)
                print("Fetching data…")
                state['tool'].fetch_data()
                print(f"Loaded {len(state['tool'].get_all_data())} movies.\n")
            except ValueError:
                print("Please enter an integer.\n")

        elif choice == "0":
            print("Exiting.")
            break

        elif choice in commands:
            commands[choice](state)

        else:
            print("Invalid choice. Please try again.\n")

if __name__ == "__main__":
    if not os.getenv("TOKEN"):
        print("Error: TOKEN environment variable not set.")
    else:
        main()
