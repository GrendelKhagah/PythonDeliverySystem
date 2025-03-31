"""
App.py
WGUPS Delivery System.

:author Taylor Ketterling 3/21/2025
"""
import csv
from package_hash_table import PackageHashTable
from package import Package
from distance_graph import DistanceGraph
from truck import Truck

def main():
    print("Booting WGUPS Delivery System..", end="")

    # Initialize data structures
    pkg_table = PackageHashTable()
    graph = DistanceGraph()

    print("..Done")

    # Load packages from CSV
    print("Loading Packages..", end="")
    load_packages_from_csv("WGUPS_Package_File.csv", pkg_table)
    print("..Done")

    # Load distances from CSV
    print("Loading Distance Matrix..", end="")
    load_distances_from_csv("WGUPS_Distance_Table.csv", graph)
    print("..Done")

    # Initialize trucks
    truck1 = Truck()
    truck2 = Truck()
    truck3 = Truck()

    # Load packages into trucks
    load_trucks(pkg_table, truck1, truck2, truck3)

    # Deliver packages on truck1 and truck2
    # Trace is enabled on Truck 1, will print its route onto the Terminal
    deliver_all_packages(truck1, pkg_table, graph, trace=True)
    deliver_all_packages(truck2, pkg_table, graph)

    # Let truck3 leave once truck1 or truck2 is done, whichever is earlier
    if time_to_minutes(truck1.get_current_time()) < time_to_minutes(truck2.get_current_time()):
        truck3.set_current_time(truck1.get_current_time())
    else:
        truck3.set_current_time(truck2.get_current_time())

    print(f"Truck3 departs at {truck3.get_current_time()}")
    deliver_all_packages(truck3, pkg_table, graph)

    # Display final statuses
    pkg_table.display_all_packages()

    # Display summary for trucks
    print("----- Truck Summary -----")
    print(f"Truck 1 mileage: {truck1.get_mileage():.2f} miles, Returned to HUB at: {truck1.get_current_time()}")
    print(f"Truck 2 mileage: {truck2.get_mileage():.2f} miles, Returned to HUB at: {truck2.get_current_time()}")
    print(f"Truck 3 mileage: {truck3.get_mileage():.2f} miles, Returned to HUB at: {truck3.get_current_time()}")
    total_miles = truck1.get_mileage() + truck2.get_mileage() + truck3.get_mileage()
    print(f"Total Miles driven by Trucks: {total_miles:.2f} miles")


def load_trucks(pkg_table, truck1, truck2, truck3):
    """
    Loads packages into the three trucks (first two are active;
    third is staged until a driver is free).
    """
    all_packages = []
    loaded_ids = set()

    # Gather all packages from the table
    # Big O: n to check all packages in the table
    for package_id in range(1, pkg_table.size() + 1):
        pkg = pkg_table.get_package(package_id)
        if pkg:
            all_packages.append(pkg)

    # Sort packages by earliest deadline first with EOD considered last
    def deadline_sort_key(pkg):
        d = pkg.get_deadline()
        if d == "EOD":
            return 999999 #arbitrarily large number
        return time_to_minutes(d)


    #Big O :  O(n log n) to sort all packages by deadline
    # This is the most expensive operation in this function
    all_packages.sort(key=deadline_sort_key)

    # Fill trucks in order, grouping if needed
    for pkg in all_packages:
        if pkg.get_package_id() in loaded_ids:
            continue

        target_truck = None
        if len(truck1.get_loaded_packages()) < Truck.MAX_CAPACITY:
            target_truck = truck1
        elif len(truck2.get_loaded_packages()) < Truck.MAX_CAPACITY:
            target_truck = truck2
        elif len(truck3.get_loaded_packages()) < Truck.MAX_CAPACITY:
            target_truck = truck3
        else:
            print("All trucks full, cannot load more at this time.")
            break

        # Check if this package has to be grouped with others
        group_with = pkg.get_group_with()
        if group_with:
            # Attempt to load the entire group
            group = [pkg]
            for group_id in group_with:
                other = pkg_table.get_package(group_id)
                if other and (other.get_package_id() not in loaded_ids):
                    group.append(other)

            # Only load group if there's capacity
            if len(target_truck.get_loaded_packages()) + len(group) <= Truck.MAX_CAPACITY:
                for p in group:
                    target_truck.load_package(p)
                    loaded_ids.add(p.get_package_id())
            # else we skip to next
        else:
            # Single package load
            target_truck.load_package(pkg)
            loaded_ids.add(pkg.get_package_id())

    print(f"Truck1 loaded with {len(truck1.get_loaded_packages())} packages.")
    print(f"Truck2 loaded with {len(truck2.get_loaded_packages())} packages.")
    print(f"Truck3 loaded with {len(truck3.get_loaded_packages())} packages (waiting for driver).")


def load_distances_from_csv(filename, graph):
    """
    Reads a CSV file of distances from WGUPS_Distance_Table.csv
    and populates the DistanceGraph, Assumes row 0 is header.

    O(d^2) to read each address pair and add to the graph.
    """
    try:
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

            # First row is header, skip the first column label
            header = rows[0]
            # all addresses to match indices
            addresses = header[1:]

            # For each subsequent row
            # Big O : d
            for row_i, row in enumerate(rows[1:], start=1):
                if not row:
                    continue
                from_location = clean_address(row[0])
                #Big O: d
                for col_i in range(1, len(row)):
                    dist_str = row[col_i].strip()
                    if dist_str:
                        try:
                            distance_val = float(dist_str)
                            to_location = clean_address(addresses[col_i - 1])
                            graph.add_distance(from_location, to_location, distance_val)
                        except ValueError:
                            print(f"Invalid number at row {row_i}, column {col_i}: {dist_str}")
    except FileNotFoundError:
        print(f"Distance CSV file not found: {filename}")


def load_packages_from_csv(filename, pkg_table):
    """
    Reads WGUPS_Package_File.csv lines and creates Package objects,
    storing them into the PackageHashTable. Expects columns in this order:
        ID, Address, City, State, Zip, Deadline, Weight, SpecialNote
    skips header rows if needed.

    O(n) to read row by row per package.
    """
    try:
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            line_num = 0
            # Big-O O(n) to read row by row per package
            for row in reader:
                line_num += 1
                if line_num <= 8:
                    continue

                package_id = int(row[0].strip())
                address = clean_address(row[1].strip())
                city = row[2].strip()
                state = row[3].strip()
                zip_code = row[4].strip()
                deadline = row[5].strip()
                weight = float(row[6].strip())
                special_note = row[7].strip() if len(row) > 7 else ""

                pkg = Package(package_id, address, city, state,
                              zip_code, deadline, weight, special_note)
                pkg_table.add_package(pkg)
    except FileNotFoundError:
        print(f"Package CSV file not found: {filename}")
    except ValueError as e:
        print(f"Error parsing CSV data: {str(e)}")


#non polymorphic method, uses python default value to make input 4 optional.
def deliver_all_packages(truck, pkg_table, graph, trace=False):
    """
    Delivers all packages loaded onto a truck using nearest-neighbor logic.
    Then sends the truck back to the HUB.
    """
    if trace:
        print("----- Delivery Trace -----")
        print("Truck starting at HUB\n")

    # While truck still has packages
    while truck.get_loaded_packages():
        next_pkg = find_nearest_package(truck, graph)
        if not next_pkg:
            if trace:
                print(f"No valid package found from {truck.get_current_location()}")
            break

        distance = graph.get_distance(
            clean_address(truck.get_current_location()),
            clean_address(next_pkg.get_address())
        )
        if trace:
            print(f"Driving from '{truck.get_current_location()}' "
                  f"to '{next_pkg.get_address()}' [{distance:.2f} miles]")

        truck.deliver_package(next_pkg, distance)
        pkg_table.update_package_status(next_pkg.get_package_id(),
                                        "Delivered", truck.get_current_time())

        if trace:
            print(f"Delivered Package #{next_pkg.get_package_id()} at {truck.get_current_time()}")
            print(f"Truck mileage: {truck.get_mileage():.2f} miles\n")

    # Return to HUB after finishing
    distance_back = graph.get_distance(
        clean_address(truck.get_current_location()),
        "HUB"
    )
    if trace:
        print(f"Returning from '{truck.get_current_location()}' to HUB [{distance_back:.2f} miles]")

    truck.go_home(distance_back)

    if trace:
        print(f"Truck returned to HUB at {truck.get_current_time()}, "
              f"Total mileage: {truck.get_mileage():.2f} miles")
        print("--------------------------\n")


def find_nearest_package(truck, graph):
    """
    Finds the nearest package to the truck's current location.
    """
    nearest_pkg = None
    min_distance = float("inf")

    # Big O: n to check all packages in the truck
    # Big O: d to check all distances in the graph

    # Big O: n * d to check all packages in the truck and all distances in the graph  
    for pkg in truck.get_loaded_packages():
        distance = graph.get_distance(
            clean_address(truck.get_current_location()),
            clean_address(pkg.get_address())
        )
        if distance >= 0 and distance < min_distance:
            min_distance = distance
            nearest_pkg = pkg

    return nearest_pkg


def clean_address(raw):
    """
    Cleans a raw address string:
    - Removes surrounding quotes
    - Removes parentheses
    - Strips whitespace
    """
    if not raw:
        return ""
    raw = raw.replace('"', '').strip()
    # Optionally remove anything inside parentheses
    import re
    raw = re.sub(r"\(.*?\)", "", raw).strip()
    # Normalize multiple spaces
    raw = re.sub(r"\s+", " ", raw)
    return raw


def parse_complex_line(line):
    """
    Parses a line with potential commas inside quotes.
    Splits by commas, respecting quoted sections.
    """
    result = []
    in_quotes = False
    current = []

    for ch in line:
        if ch == '"':
            in_quotes = not in_quotes
        elif ch == ',' and not in_quotes:
            result.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    result.append("".join(current).strip())
    return result


def time_to_minutes(time_str):
    """
    Converts 'HH:MM' or 'HH:MM AM/PM' to integer minutes.
    EOD => a large number.
    """
    if time_str.upper() == "EOD":
        return 999999  #arbitrarily large number

    time_str = time_str.strip().upper()

    # If no AM/PM
    if ("AM" not in time_str) and ("PM" not in time_str):
        hr, mn = time_str.split(":")
        return int(hr) * 60 + int(mn)

    # If there's AM/PM
    parts = time_str.split()
    if len(parts) != 2:
        raise ValueError(f"Invalid time format: {time_str}")
    hh_mm, period = parts
    hr, mn = hh_mm.split(":")
    hr = int(hr)
    mn = int(mn)

    if period == "PM" and hr != 12: hr += 12
    if period == "AM" and hr == 12: hr = 0

    return hr * 60 + mn


if __name__ == "__main__":
    main()
