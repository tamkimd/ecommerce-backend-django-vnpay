# Django E-commerce Backend

This is an e-commerce backend built with Django and VNPay. The API is built using Django REST framework and is equipped with permission handling for different user roles.

## Requirements

- Django
- Django REST Framework
- django-filter
- djangorestframework-simplejwt
- drf-spectacular

## Installation

To run the Django backend locally, follow these steps:

1. Clone the repository:

   ```
   git clone https://github.com/tamkimd/ecommerce-backend-django-vnpay.git
   ```

2. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

3. Run the development server:

   ```
   python manage.py runserver
   ```

## API Endpoints


1. **Account Management** (`account.urls`):

   - `api/register/`: User registration.
   - `api/login/`: User login.
   - `api/token/refresh/`: Refresh authentication token.
   - `api/forgot-password/`: Initiate the password reset process.
   - `api/reset-password/`: Reset user's password.

2. **Product Management** (`product.urls`):

   - `api/product/`: Product list and creation.
   - `api/stock/`: Stock list and creation.
   - `api/stockproduct/`: Association between products and stock.

3. **Order Management** (`order.urls`):

   - `api/shippinginfo/`: Shipping information list and creation.
   - `api/order/`: Order list and creation.
   - `api/cart/`: Cart list and creation.
   - `api/lineitem/`: Line item list and creation.
   - `api/shipment/`: Shipment list and creation.

4. **Payment Management** (`payment.urls`):

   - `api/payment/`: Payment list and creation.
   - `api/payment_create/`: Initiate payment creation.
   - `api/payment_response/`: Handle payment response.

## Schema Documentation

- `/schema/docs`: Swagger documentation for API endpoints.

