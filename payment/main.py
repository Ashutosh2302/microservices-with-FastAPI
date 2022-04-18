from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests
import time

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

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis

@app.get('/order/{pk}')
def get_order(pk: str):
    return Order.get(pk=pk)

@app.post('/orders')
async def orders(request: Request,  background_tasks: BackgroundTasks):
    body = await request.json()
    req = requests.get(f"http://localhost:8000/product/{body['id']}")

    product = req.json()

    order = Order(
        product_id = body['id'],
        price = product['price'],
        fee = 0.2 * product['price'],
        total = 1.2 * product['price'],
        quantity = body['quantity'],
        status = 'pending'
    )

    order.save()

    background_tasks.add_task(order_completed, order)

    return order


def order_completed(order: Order):
    time.sleep(10)
    order.status = 'completed'
    order.save()