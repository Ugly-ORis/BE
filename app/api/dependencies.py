from app.db.milvus_client import MilvusClient
from app.db.schemas.customer import get_customer_schema
from app.db.schemas.order import get_order_schema
from app.db.schemas.ice_cream import get_ice_cream_schema
from app.db.schemas.sale_product import get_sale_product_schema
from app.db.schemas.topping import get_topping_schema

customer_client = MilvusClient("Customer", get_customer_schema())
order_client = MilvusClient("Order", get_order_schema())
ice_cream_client = MilvusClient("Ice_cream", get_ice_cream_schema())
sale_product_client = MilvusClient("Sale_product", get_sale_product_schema())
topping_client = MilvusClient("Topping", get_topping_schema())