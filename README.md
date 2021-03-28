Candy Delivery App v1

REST API service for Candy delivery service

Description

Service accept post request with couriers and orders data in JSON format. Assigns orders for couriers, complete orders and calculate curiers earnings and rating.
See acceptable paths and format data at http://x.x.x.x:8080/docs

Requirements

Services build using Fastapi web framework (https://fastapi.tiangolo.com/) and MongoDB (https://www.mongodb.com/)
All dependencies listed in application/requirments.txt

Installation

1. Install and configure MongoDB according official documentation
2. Install all requirements using pip
    pip install -r application/requirments.txt
3. Make changes in configuration file if necessary

Configuration

All configurations in application/constant.py file
1. COURIER_MAX_WEIGHT max weight per courier
2. COURIER_K earning coefficient per courier
3. MONGO_DETAILS - MongoDB connection string

Test

After installation you can test service py running
    python -m pytest application/test.py
Do not run tests on production database (change MONGO_DETAILS in constant.py to test DB and reload server) - it will remove all data after test.

Setup

To start service run follwing command inside application folder
unvicorn main:app --host 0.0.0.0 --port 8080
