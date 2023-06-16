import argparse
import bs4
import lxml
import requests
import sys
import validators
from time import sleep

from util import Node, StackFrontier, QueueFrontier

base_url = "https://tvtropes.org"

def main():

    if len(sys.argv) == 3:
        (initial_work, final_work) = parse_arguments()

    elif len(sys.argv) == 1:
        initial_work = input("TV Tropes URL of the initial work: ")
        final_work = input("TV Tropes URL of the final work: ")

    else:
        sys.exit("Invalid usage.")

    source = validate_work(initial_work)
    if source is None:
        sys.exit("Initial work not found.")
    target = validate_work(final_work)
    if target is None:
        sys.exit("Final work not found.")

    path = shortest_path(source, target)
    
    print_result(path, source)


def shortest_path(source, target):
    """
    Returns the shortest list of tropes
    that connect the source to the target.

    If no possible path, returns None.
    """

    # If source and target coincide, return empty path
    if source == target:
        return ""

    # Keep track of number of states explored
    num_explored = 0

    # Initialize frontier to just the starting position
    start = Node(state=source, parent=None, action=None)
    frontier = StackFrontier()
    frontier.add(start)

    # Initialize an empty explored set
    explored = set()

    # Keep looping until solution found
    while True:

        # If nothing left in frontier, then no path
        if frontier.empty():
            return None

        # Choose a node from the frontier
        node = frontier.remove()
        num_explored += 1

        # Mark node as explored
        explored.add(node.state)

        # Add neighbors to frontier
        for action,state in neighbors_for_work(node.state):

            if not frontier.contains_state(state) and state not in explored:

                child = Node(state=state, parent=node, action=action)
  
                # If node is the goal, then we have a solution
                if child.state == target:
                    tropes = []
                    works = []
                    while child.parent is not None:
                        tropes.append(child.action)
                        works.append(child.state)
                        child = child.parent
                    tropes.reverse()
                    works.reverse()
                    solution = list(zip(tropes, works))
                    return solution
                
                frontier.add(child)


def parse_arguments():
    """
    Parses command-line arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("initial_work", help="the TV Tropes URL of the work from which you want to start the search")
    parser.add_argument("final_work", help="the TV Tropes URL of the work which must be reached")
    args = parser.parse_args()
    return (args.initial_work, args.final_work)


def validate_work(work):
    """
    Validates the work provided by the user
    """

    if not validators.url(work) or "tvtropes.org/pmwiki" not in work or "/Main/" in work:
        return None
    
    res = requests.get(work)
    if res.status_code == 200:
        return work
    
    return None


def neighbors_for_work(work):
    """
    Returns (trope_id, work_id) pairs for works
    who played for the same trope of the given work
    """
    res = requests.get(work)
    soup = bs4.BeautifulSoup(res.text, "lxml")

    tropes_ids = {base_url + page.attrs["href"] for page in soup.select("ul li a[class='twikilink']") if "/Main/" in str(page)}  # set comprehension

    title = get_name(work).replace(" ", "")
    tropes_subpages = [base_url + trope_subpage.attrs["href"] for trope_subpage in soup.select(f"ul li a[class='twikilink'][href*='{title}']")]

    for trope_subpage in tropes_subpages:
        res_subpage = requests.get(trope_subpage)
        soup_subpage = bs4.BeautifulSoup(res_subpage.text, "lxml")
        tropes_ids_subpages = {base_url + page.attrs["href"] for page in soup_subpage.select("ul li a[class='twikilink']") if "/Main/" in str(page)}
        tropes_ids.update(tropes_ids_subpages)

    neighbors = set()

    for trope_id in tropes_ids:
        res = requests.get(trope_id)
        soup = bs4.BeautifulSoup(res.text, "lxml")

        works_ids = {base_url + work.attrs["href"] for work in soup.select("ul li a[class='twikilink']") if not "/Main/" in str(work) and not "/Creator/" in str(work)}

        title = get_name(trope_id).replace(" ", "")
        works_subpages = [base_url + work_subpage.attrs["href"] for work_subpage in soup.select(f"ul li a[class='twikilink'][href*='{title}']")]

        for work_subpage in works_subpages:
            res_subpage = requests.get(work_subpage)
            soup_subpage = bs4.BeautifulSoup(res_subpage.text, "lxml")
            works_ids_subpages = {base_url + page.attrs["href"] for page in soup_subpage.select("ul li a[class='twikilink']") if not "/Main/" in str(page) and not "/Creator/" in str(page)}
            works_ids.update(works_ids_subpages)

        for work_id in works_ids:
            neighbors.add((trope_id, work_id))

        sleep(1)

    return neighbors


def get_name(id):
    """
    Returns the corresponding name for the work / trope provided as a parameter
    """

    res = requests.get(id)
    soup = bs4.BeautifulSoup(res.text, "lxml")
    return soup.select("title")[0].getText().split(" - TV Tropes")[0].split("(")[0].strip()


def print_result(path, source):
    """
    Prints the resulting path
    """

    if path is None:
        print("\nworks are not connected.")
    elif path == "":
        print("\nIt's the same work.")
    else:
        degrees = len(path)
        if degrees == 1:
            print(f"\n{degrees} degree of separation.\n")
        else:
            print(f"\n{degrees} degrees of separation.\n")

        path = [(None, source)] + path

        for i in range(degrees):
            work1 = get_name(path[i][1])
            work2 = get_name(path[i + 1][1])
            trope = get_name(path[i + 1][0])
            print(f"{i + 1}: {work1} and {work2} feature the {trope} trope")


if __name__ == "__main__":
    main()
