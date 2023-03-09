import csv
import sys
from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
# {name1: (id1, id2, id3...), name2: (id4,id5,id6)...}
names: dict = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
# {id1: {name, birth, movies=(movie1, movie2, movie3)}, id2: {name, birth, movies=(movie4, movie5, movie6)}}
people: dict = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
# Just $people in reverse
movies: dict = {}


# Pre-Written
def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


# Pre-Written
def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source: str, target: str):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Use BFS so you're guaranteed the shortest path

    # Create a queue for moves path, paths taken
    frontier = QueueFrontier()
    paths_taken = set()
    # Create first Node (a blank one)
    frontier.add(Node(source, None, None))
    # Start checking
    while True:
        # Explored everything? No path...
        if len(frontier.frontier) == 0:
            return None
        # First actor
        person = frontier.remove()
        paths_taken.add(person.state)
        # Discover neighbors from first actor
        neighbors = neighbors_for_person(person.state)
        # Add neighbors to path
        for new_movie_id, new_person_id in neighbors:
            # Has neighbor been explored yet?
            if new_person_id not in paths_taken and not frontier.contains_state(new_person_id):
                new_node = Node(new_person_id, person,
                                new_movie_id)  # (State, Parent, Movie)
                if new_person_id == target:
                    # You found the person, now you just have to note the path
                    node = new_node
                    path = {}
                    while node.parent:
                        path[node.state] = node.action
                        node = node.parent
                    # Reverse order for printing
                    return [(person, movie) for movie, person in path.items()][::-1]
                else:
                    frontier.add(new_node)  # More to explore!


# Pre-Written
def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id: str):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]  # list of IDs
    return set([(movie_id, person_id)
                for movie_id in movie_ids for person_id in movies[movie_id]["stars"]])


if __name__ == "__main__":
    main()
