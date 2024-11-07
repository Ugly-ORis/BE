from pymilvus import connections, Collection, utility, Index

class MilvusClient:
    def __init__(self, collection_name: str, schema):
        self.collection_name = collection_name
        connections.connect("default", host="localhost", port="19530")
        self.collection = self.get_or_create_collection(schema)
        self.create_index()

    def get_or_create_collection(self, schema):
        if not utility.has_collection(self.collection_name):
            collection = Collection(name=self.collection_name, schema=schema)
            print(f"Collection '{self.collection_name}' created.")
        else:
            collection = Collection(name=self.collection_name)
            print(f"Collection '{self.collection_name}' loaded.")
        return collection

    def create_index(self):
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }

        if any(field.name == "feature_vector" for field in self.collection.schema.fields):
            if not self.collection.has_index():
                self.collection.create_index(field_name="feature_vector", index_params=index_params)
                print("Index created for feature_vector.")
            else:
                print("Index already exists.")
        else:
            print("No 'feature_vector' field found; index creation skipped.")