"""
PackageHashTable.py
Transcribed from the Java 'PackageHashTable' class.
"""
from package import Package

class PackageHashTable:
    """
    A simple hash table that stores Package objects by their package_id.
    """

    def __init__(self):
        self.packages = {}  # { int(package_id) -> Package }

    def add_package(self, pkg):
        self.packages[pkg.get_package_id()] = pkg

    def get_package(self, package_id):
        return self.packages.get(package_id)

    def update_package_status(self, package_id, status, delivery_time):
        pkg = self.packages.get(package_id)
        if pkg:
            pkg.set_status(status)
            pkg.set_delivery_time(delivery_time)

    def display_all_packages(self):
        print("----- Package Status -----")
        for pkg in self.packages.values():
            print(pkg)

    def size(self):
        return len(self.packages)
