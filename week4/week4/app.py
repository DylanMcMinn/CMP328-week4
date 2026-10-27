from flask import Flask, request
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from models import Customer, Order, engine
from query_functions import search_customers, orders_for, total_spent

app = Flask(__name__)


def customer_dict(customer):
    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
    }


def order_dist(customer):
    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone
    }


@app.get("/api/customers")
def list_customers():
    with Session(engine) as sesson:
        stmt = select(Customer).order_by(Customer.name)
        result = []
        for customer in sesson.scalars(stmt):
            result.append(customer_dict(customer))
        return result


@app.get ("/api/customers/<int: customer_id>")
def get_customer(customer_id):
    with Session(engine) as session:
        customer = session.get(Customer, customer_id)
        if customer is None:
            return {"error": "Customer not found"}, 404
        return customer_dict(customer)

@app.get("/api/customers/search")
def search():
    name = request.args.get("name", "")
    if name == "":
        return {"error": "Add ?name= to address"}, 400
    with Session(engine) as session:
        result = []
        for customer in search_customers(session, name):
            result.append(customer_dict(customer))
        return result

@app.get("/api/customers/<int:customer_id>/orders")
def customer_orders(customer_id):
    with Session(engine) as session:
        if session.get(Customer, customer_id) is None:
            return {"error": "Customer not found"}, 404
        result = []
        for order in orders_for(session, customer_id):
            result.append(order_dict(order))
            return result

@app.get("/api/customer/<int:customer_id>/summary")
def customer_summary(customer_id):
    with Session(engine) as session:
        customer = session.get(Customer, customer_id)
        result = []
        for order in orders:
            result.append(order_dict(order))
        return {
            "customer": customer_dict(customer), 
            "orders": result,
            "order_count": len(orders), 
            "total_spent": total_spent(session, customer_id),
        }

@app.get("/api/products")
def products():
    with Session(engine) as session:
        units = func.sum(Order.quantity)
        stmt = (select(Order.product, units)
                .group_by(Order.product)
                .order_by(units.desc()))
        result = []
        for product, total in session.execute(stmt):
            result.append({"product": product, "units": total})
            return result

@app.get("/api/stats")
def stats():
    with Session(engine) as session:
        customers = session.scalar(select(func.count(Customer.id)))
        orders = session.scalar(select(func.count(Order_id)))
        takings = session.scalar(select(func.sum(Order.quantity*Order.price)))
        no_orders = (select(Customer.name)
                    .outerjoin(Customer.orders)
                    .where(Order.id == None)
                    .order_by(Customer.name))
        return {
            "customers": customers, 
            "orders": orders,
            "takings,": takings
            "customers_with_no_orders": session.scalars(no_orders).all(),
        }

@app.get("/api/orders")
def list_orders():
    product = request.args.get("product")
    min_total = request.args.get("min_total", type=int)
    with Session(engine) as session:
        stmt = select(Order).order_by(Order.id)
        if product is not None:
            stmt = stmt.where(Order.product == product)
        if min_total is not None:
            stmt = stmt.where(Order.quantity * Order.price >= min_total)
        result = []
        for order in session.scalars(stmt):
            row ["customer"] = order.customer.name
            result.append(row)
            return result

@app.get("/api/customers/<int;customer_id>/total")
def customer_total(customer_id):
    with session(engine) as session:
        if session.get (Customer, customer_id) is None:
            return "return {"error": "Customer not found}, 404
            