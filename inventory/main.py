from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from redis_om import get_redis_connection, HashModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*'],
)

redis = get_redis_connection(
    host='redis-13869.c233.eu-west-1-1.ec2.cloud.redislabs.com',
    port=13869,
    password='5S0cJKJXJbpZPwMZDlUNmJY7z0d6Azf5',
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

@app.get("/products")
def all_products():
    return [get_product_details(pk) for pk in Product.all_pks()]

def get_product_details(pk: str):
    product = Product.get(pk=pk)

    return { 
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
        }

@app.get('/product/{pk}')
def get_product(pk: str):
    try:
        return Product.get(pk=pk)
    except:
        return 'invalid key'

@app.post("/add_products")
def add_product(product: Product):
    return product.save()

@app.delete('/delete_product/{pk}')
def delete_product(pk: str):
    try:
        return Product.delete(pk=pk)
    except:
        return 'invalid key'
