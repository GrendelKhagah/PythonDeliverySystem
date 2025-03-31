"""
DistanceGraph.py

:author Taylor Ketterling 3/21/2025
"""
class DistanceGraph:
    """
    Represents distances between delivery locations using a graph structure.
    Distances are symmetric: distance(A, B) = distance(B, A).
    """

    def __init__(self):
        self.distances = {}  # { str -> { str -> float } }

    def add_distance(self, address1, address2, distance):
        """
        Adds a distance between two locations (symmetric).
        """
        if address1 not in self.distances:
            self.distances[address1] = {}
        if address2 not in self.distances:
            self.distances[address2] = {}

        self.distances[address1][address2] = distance
        self.distances[address2][address1] = distance

    def get_distance(self, address1, address2):
        """
        Retrieves the distance between two addresses or -1 if not found.
        """
        if (address1 in self.distances and
            address2 in self.distances[address1]):
            return self.distances[address1][address2]

        print(f"Distance not found between {address1} and {address2}")
        return -1.0

    def print_all_distances(self):
        """
        Debugging method to print all stored distances.
        """
        print("\n--- All Stored Distances ---")
        for from_loc, to_map in self.distances.items():
            for to_loc, dist in to_map.items():
                print(f"{from_loc} -> {to_loc} : {dist:.2f} miles")
        print("----------------------------\n")
