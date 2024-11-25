from app.db.milvus_client import MilvusClient
from app.db.schemas.customer_schema import get_customer_schema
from app.db.schemas.order_schema import get_order_schema
from app.db.schemas.ice_cream_schema import get_ice_cream_schema
from app.db.schemas.sale_product_schema import get_sale_product_schema
from app.db.schemas.topping_schema import get_topping_schema
from app.db.schemas.robot_topcam_view import get_topcam_schema
from app.db.schemas.aris_robot_schema import aris_robot_schema

customer_client = MilvusClient("Customer", get_customer_schema())
order_client = MilvusClient("Order", get_order_schema())
ice_cream_client = MilvusClient("Ice_cream", get_ice_cream_schema())
sale_product_client = MilvusClient("Sale_product", get_sale_product_schema())
topping_client = MilvusClient("Topping", get_topping_schema())
### top view 추가 
topcam_client = MilvusClient("Topcam", get_topcam_schema())

### aris_robot 추가 
robot_client = MilvusClient("Robot", aris_robot_schema())