from pymilvus import Collection

class IDManager:
    def __init__(self):
        self.id_collection_name = "ID_Management"
        self.id_collection = Collection(self.id_collection_name)
        
    def initialize_default_ids(self, collection_names: list):
        """Initialize default entries for collections if they don't exist."""
        for name in collection_names:
            existing_entry = self.id_collection.query(f"collection_name == '{name}'", output_fields=["last_id"])
            if not existing_entry:
                self.id_collection.insert([[name], [[0.0, 0.0]], [0]])  # Add initial `last_id` as 0 for the collection

    def get_next_id(self, collection_name: str):
        results = self.id_collection.query(f"collection_name == '{collection_name}'", output_fields=["last_id"])
        current_id = results[0]["last_id"] if results else 0
        next_id = current_id + 1
        return next_id
    
    def update_last_id(self, collection_name: str, new_last_id: int):
        """Update the last_id for a specific collection by deleting and reinserting."""
        self.id_collection.delete(f"collection_name == '{collection_name}'")
        self.id_collection.flush()

        self.id_collection.insert([[collection_name], [[0.0, 0.0]], [new_last_id]])
        self.id_collection.flush()
