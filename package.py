"""
Package.py

:author Taylor Ketterling 3/21/2025
"""

class Package:
    """
    Manages package delivery details in the WGUPS network.
    """

    def __init__(self, package_id, address, city, state,
                 zip_code, deadline, weight, special_note):
        """
        Constructs a new Package with given delivery details.

        :param package_id: unique identifier for the package (int)
        :param address: street address (str)
        :param city: city (str)
        :param state: state abbreviation (str)
        :param zip_code: zip code (str)
        :param deadline: string representing delivery deadline ("EOD" or "HH:MM AM/PM")
        :param weight: package weight in kg (float)
        :param special_note: any special instructions or constraints (str)
        """
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip_code
        self.deadline = deadline
        self.weight = weight
        self.status = "At hub"
        self.delivery_time = "N/A"
        self.special_note = special_note

        # If the package must be delivered with specific other packages, store their IDs
        self.group_with = []
        if "Must be delivered with" in special_note:
            # Try to parse out additional package IDs
            parts = special_note.split("with")
            if len(parts) > 1:
                # remove non-digits & commas, then split by comma
                possible_ids = parts[1].replace("[^0-9,]", "").split(",")
                for pid in possible_ids:
                    pid_clean = ''.join(ch for ch in pid if ch.isdigit())
                    if pid_clean:
                        self.group_with.append(int(pid_clean))

    def get_package_id(self):
        return self.package_id

    def get_address(self):
        return self.address

    def get_city(self):
        return self.city

    def get_state(self):
        return self.state

    def get_zip(self):
        return self.zip

    def get_deadline(self):
        return self.deadline

    def get_weight(self):
        return self.weight

    def get_status(self):
        return self.status

    def get_delivery_time(self):
        return self.delivery_time

    def get_special_note(self):
        return self.special_note

    def get_group_with(self):
        return self.group_with

    def set_address(self, address):
        self.address = address

    def set_status(self, status):
        self.status = status

    def set_delivery_time(self, delivery_time):
        self.delivery_time = delivery_time

    def __str__(self):
        return (f"Package #{self.package_id} to {self.address}, "
                f"Status: {self.status}, Delivered at: {self.delivery_time}")
