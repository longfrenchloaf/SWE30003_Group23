# artproject/app/models/merchandise.py
from typing import Optional, List
from app import data_manager 

class Merchandise:
    def __init__(self, merchandiseID: str, name: str, description: str, price: float, stockLevel: int):
        self.merchandiseID: str = merchandiseID
        self.name: str = name
        self.description: str = description
        self.price: float = price
        self.stockLevel: int = stockLevel

    def update_stock(self, quantity_change: int):
        """Positive for adding stock, negative for reducing."""
        self.stockLevel += quantity_change
        if self.stockLevel < 0:
            print(f"Warning: Stock for {self.name} is now negative: {self.stockLevel}")
            self.stockLevel = 0
        # IMPORTANT: Now we also need to save this change back to the file
        all_merch = data_manager.get_all_merchandise_data()
        for i, item_data in enumerate(all_merch):
            if item_data.get("merchandiseID") == self.merchandiseID:
                all_merch[i]["stockLevel"] = self.stockLevel
                break
        data_manager.save_all_merchandise_data(all_merch)


    def check_availability(self, quantity: int = 1) -> bool:
        return self.stockLevel >= quantity

    def get_price(self) -> float:
        return self.price

    def get_name(self) -> str:
        return self.name

    def __repr__(self):
        return f"<Merchandise {self.merchandiseID} - {self.name}>"

    @staticmethod
    def get_by_id(merchandise_id: str) -> Optional['Merchandise']:
        item_data = data_manager.get_merchandise_by_id_data(merchandise_id)
        if item_data:
            # Create a Merchandise object from the dictionary data
            return Merchandise(**item_data)
        return None

    @staticmethod
    def get_all() -> List['Merchandise']:        
        all_items_data = None # Initialize to see if it gets populated
        try:
            all_items_data = data_manager.get_all_merchandise_data()
        except Exception as e_data_manager:
            print(f"ERROR Merchandise.get_all(): EXCEPTION calling data_manager.get_all_merchandise_data(): {e_data_manager}") # 4. Error from data_manager?
            return [] # Return empty if data_manager failed

        if not isinstance(all_items_data, list):
            print(f"ERROR Merchandise.get_all(): Expected a list from data_manager, but got {type(all_items_data)}. Returning empty list.") # 5. Is it a list?
            return []

        if not all_items_data:
            return []

        merch_objects = []
        
        for i, item_data in enumerate(all_items_data):
            if not isinstance(item_data, dict):
                print(f"ERROR Merchandise.get_all(): Item {i+1} is not a dictionary. Skipping. Item: {item_data}") # 9. Is item a dict?
                continue
            try:
                merch_obj = Merchandise(**item_data)
                merch_objects.append(merch_obj)
            except TypeError as te:
                print(f"ERROR Merchandise.get_all(): TypeError creating Merchandise object from item {i+1}: {item_data}. Error: {te}") # 10. TypeError? (Mismatched keys/args)
            except Exception as e_obj_creation:
                print(f"ERROR Merchandise.get_all(): General Exception creating Merchandise object from item {i+1}: {item_data}. Error: {e_obj_creation}") # 11. Other errors?
        
        return merch_objects

    def to_dict(self):
        """Helper method to convert instance to dictionary for saving."""
        return {
            "merchandiseID": self.merchandiseID,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stockLevel": self.stockLevel
        }

    def save(self):
        """Saves the current merchandise item or updates it in the data file."""
        all_merch_data = data_manager.get_all_merchandise_data()
        item_exists = False
        for i, item_data in enumerate(all_merch_data):
            if item_data.get("merchandiseID") == self.merchandiseID:
                all_merch_data[i] = self.to_dict() # Update existing
                item_exists = True
                break
        if not item_exists:
            all_merch_data.append(self.to_dict()) # Add new
        data_manager.save_all_merchandise_data(all_merch_data)