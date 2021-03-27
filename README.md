Candy Delivery App v1

REST API service for Candy delivery service

**Description**

Service accept post request with couriers and orders data in JSON format. Assigns orders for couriers, complete orders and calculate curiers earnings and rating.
See acceptable paths and format data at http://x.x.x.x:8080/docs

**Requirements**

Services build using Fastapi web framework (https://fastapi.tiangolo.com/) and MongoDB (https://www.mongodb.com/)
All dependencies listed in application/requirments.txt

**Installation**

1. Install and configure MongoDB according official documentation
2. Install all requirements using pip
    pip install -r application/requirments.txt
3. Make changes in configuration file if necessary

**Configuration**

All configurations in application/server/constant.py file
1. BIND_IP - IP adress of interface to listen on requests
2. PORT - PORT to listen on
3. COURIER_MAX_WEIGHT max weight per courier
4. COURIER_K earning coefficient per courier
5. MONGO_DETAILS - MongoDB connection string

**Test**

After installation you can test service py running
    pytest application/test.py

**Setup**

To start service run follwing command
    python application/main.py
