# ArzanShop
> ArzanShop is a scalable multi-vendor e-commerce project written fully with django-rest-framework
# Table of Contents
- [About](#about)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)
# About
ArzanShop is a backend multi-vendor e-commerce project.
It enables customers to browse through and buy various products related to different categories.Morover, Vendors are able to sign up and put their products on sale and manage their pruducts.
The purpose of this project is to demonstrate my knowledge of backend development as my first project.
# Tech Stack
- **Django** -> Web framework used for building the backend.
- **Django Rest Framework** -> Framework for creating API.
- **Postgresql** -> Database used in the project.Well known for it's compatibility with django.
- **Redis** -> Key-Value Database used for caching.
- **Docker** -> Used to containerize the application for easy deployment.
- **Pytest** -> Framework for testing the application.
- **Django Filters** -> Package used for filtering.
- **Swagger** -> For documenting APIs
# Features
- ✨ **Multi-Vendor Support**  
Allows vendors to sign up and add products

- 🛒 **Product Management**  
Enables vendors to create, update, and delete their products

- 🔑 **User Authentication**  
A full authentication system was integrated with JWT

- 🔍 **Product Search & Filtering**  
Customers can search for products by keywords and filter by categories, and specific stores.  

- 🛍️ **Shopping Cart**  
Enables customers to interact with the cart without registering for the goal of facilitating payment process.

- 📦 **Order Management**  
Customers can place orders.

- 📜 **Swagger API Documentation**  
Automatically generated, interactive API documentation via Swagger, accessible at `/api/docs/` for testing and reference.

# Installation

To install and set up the project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/shayan-shirani/arzanshop.git
    cd arzanshop
    ```

2. Build and run the Docker containers:
    ```bash
    docker-compose up --build
    ```

3. The application will be available at `http://localhost:8000`.

# Running Locally

To run the project locally without Docker:

1. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Apply migrations:
    ```bash
    python manage.py migrate
    ```

3. Create a superuser to access the admin dashboard:
    ```bash
    python manage.py createsuperuser
    ```

4. Run the Django development server:
    ```bash
    python manage.py runserver
    ```

5. The application will be available at `http://localhost:8000`.

---

# Testing

To run the tests with **Pytest**, simply run:

```bash
pytest
```

---

# **API Documentation**  
The project uses Swagger to automatically generate API documentation.  
- To view the API documentation, visit:
http://localhost:8000/api/docs/
