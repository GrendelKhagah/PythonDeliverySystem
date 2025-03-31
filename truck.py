"""
Truck.py

:author Taylor Ketterling 3/21/2025 
"""
from package import Package

class Truck:
    """
    Represents a delivery truck in the WGUPS routing system.
    Handles package loading, delivering packages, tracking mileage,
    current location and current time.
    """

    MAX_CAPACITY = 16         # Max number of packages
    SPEED_MPH = 18.0          # Speed in miles/hour

    def __init__(self):
        """
        Constructs a Truck with an empty load, zero mileage,
        location at 'HUB', and time at '08:00'.
        """
        self.loaded_packages = []
        self.mileage = 0.0
        self.current_location = "HUB"
        self.current_time = "08:00"

    def load_package(self, pkg):
        """
        Loads a package onto the truck if capacity allows.
        """
        if len(self.loaded_packages) < Truck.MAX_CAPACITY:
            self.loaded_packages.append(pkg)
            pkg.set_status("En route")
        else:
            print(f"Truck capacity reached, cannot load package #{pkg.get_package_id()}")

    def deliver_package(self, pkg, distance_to_package):
        """
        Delivers a package, updates mileage, location, and delivery timestamp.
        """
        self.mileage += distance_to_package
        pkg.set_status("Delivered")
        pkg.set_delivery_time(self.current_time)
        self.loaded_packages.remove(pkg)
        self.current_location = pkg.get_address()

        # Convert distance to hours traveled at SPEED_MPH
        time_traveled = distance_to_package / Truck.SPEED_MPH
        self._update_current_time(time_traveled)

    def go_home(self, distance_to_home):
        """
        Sends the truck back to the HUB.
        """
        self.mileage += distance_to_home
        self.current_location = "HUB"

        time_traveled = distance_to_home / Truck.SPEED_MPH
        self._update_current_time(time_traveled)

    def _update_current_time(self, hours):
        """
        Updates the truck's current_time (HH:MM) after traveling
        in float hours.
        """
        # Convert current_time to total minutes
        hr, min_ = map(int, self.current_time.split(":"))
        total_current_minutes = hr * 60 + min_

        # Add traveled minutes
        traveled_minutes = int(round(hours * 60))
        total_new_minutes = total_current_minutes + traveled_minutes

        # Convert back to HH:MM (24-hour style)
        new_hr = total_new_minutes // 60
        new_min = total_new_minutes % 60
        self.current_time = f"{new_hr:02d}:{new_min:02d}"

    def get_mileage(self):
        return self.mileage

    def get_current_location(self):
        return self.current_location

    def get_current_time(self):
        return self.current_time

    def get_loaded_packages(self):
        return self.loaded_packages

    def set_current_time(self, current_time):
        self.current_time = current_time
