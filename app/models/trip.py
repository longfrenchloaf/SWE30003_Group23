# app/models/trip.py
from typing import List, Optional
from app import data_manager 

class Trip:
    def __init__(self, id: str, route: str, date: str, time: str, price: float, available_seats: int):
        self.id: str = id
        self.route: str = route
        self.date: str = date
        self.time: str = time
        self.price: float = price
        self.available_seats: int = available_seats

    def __repr__(self):
        return f"<Trip {self.id} - {self.route} on {self.date} at {self.time}>"

    def to_dict(self) -> dict:
        """Converts the Trip object to a dictionary."""
        return {
            "id": self.id,
            "route": self.route,
            "date": self.date,
            "time": self.time,
            "price": self.price,
            "available_seats": self.available_seats
        }

    @classmethod
    def from_dict(cls, data: dict) -> Optional['Trip']:
        """Creates a Trip object from a dictionary."""
        if not data:
            return None
        # Ensure all expected keys exist, provide defaults or validation if needed
        return cls(
            id=data.get('id'),
            route=data.get('route'),
            date=data.get('date'),
            time=data.get('time'),
            price=float(data.get('price', 0.0)),
            available_seats=int(data.get('available_seats', 0))
        )

    @staticmethod
    def get_by_id(trip_id: str) -> Optional['Trip']:
        """Loads a specific trip by ID from the data source."""
        trip_data = data_manager.get_trip_by_id_data(trip_id) # Assuming data_manager has this method
        return Trip.from_dict(trip_data)

    @staticmethod
    def get_all() -> List['Trip']:
        """Loads all trips from the data source."""
        all_trips_data = data_manager.get_all_trips_data() # Assuming data_manager has this method
        return [Trip.from_dict(data) for data in all_trips_data if Trip.from_dict(data) is not None]

    # Optional: Add methods for managing seat availability
    def check_availability(self, quantity: int = 1) -> bool:
        return self.available_seats >= quantity

    def update_availability(self, quantity_change: int):
        """Increases (positive) or decreases (negative) available seats."""
        self.available_seats += quantity_change
        if self.available_seats < 0:
            self.available_seats = 0 # Prevent negative stock

        # IMPORTANT: Save the change back to the data source
        all_trips = data_manager.get_all_trips_data()
        for i, trip_data in enumerate(all_trips):
            if trip_data.get("id") == self.id:
                all_trips[i] = self.to_dict() # Update the dictionary in the list
                break
        data_manager.save_all_trips_data(all_trips) # Assuming data_manager has this method