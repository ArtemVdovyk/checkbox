# Checkbox Application

This is a Checkbox FastAPI application for managing receipts.

## Features

- CRUD operations for receipts
- Authentication and authorization using JWT tokens
- Pagination support for retrieving receipts
- Text-based receipt generation

## Installation

1. Clone the repository:

```
git clone https://github.com/ArtemVdovyk/checkbox.git
```

2. Navigate to the project directory:
```
cd checkbox
```

3. Install dependencies using pip:
```
pip install -r requirements.txt
```

## Usage

1. Start the FastAPI application:
```
uvicorn main:app --reload
```
2. Once the server is running, you can access the Swagger UI at http://localhost:8000/docs to interact with the API endpoints.

3. Use the provided endpoints to manage receipts, authenticate users, and generate receipt text.

## API Endpoints
### Default
- ***/healthy***: Health check

    **Type:** `GET`

    **Server Responses:**
    - Status code = `200`:
        ```
        {"status": "Healthy"}
        ```
### Admin
- ***/admin/receipts***: Get all receipts

    **Type:** `GET`

    **Query Parameters:**

    - `page`
        - **Type:** Integer
        - **Description:** Specifies the page number for paginated results.
        - **Default:** 1

    - `size`
        - **Type:** Integer
        - **Description:** Specifies the number of items per page for paginated results.
        - **Default:** 50

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated not as an admin
        - Status code = `401`:
            ```
            {"detail": "Authentication failed"}
            ```
    - Authenticated as an admin
        - Status code = `200`:
            ```
            {
                "total_results": 1,
                "page": 1,
                "pages": 1,
                "size": 50,
                "results": [
                    {
                    "id": "daafa0dc-06bb-40fd-8472-c8fa6ed47a43",
                    "products": [
                        {
                            "name": "Bootle of milk",
                            "price": 8.5,
                            "quantity": 2,
                            "total": 17
                        },
                        {
                            "name": "Bottle of water",
                            "price": 5.8,
                            "quantity": 8,
                            "total": 46.4
                        }
                    ],
                    "payment": {
                        "amount": 100,
                        "type": "cashless"
                    },
                    "total": 63,
                    "rest": 37,
                    "created_at": "2024-03-06T17:30:42.809640",
                    "owner_id": 1
                    },
                ]
            }
            ```
        - Status code = `404`:
            ```
            {"detail": "Receipts not found"}
            ```

- ***/admin/receipt/{receipt_id}***: Delete receipt

    **Type:** `DELETE`

    **Query Parameters:**

    - `receipt_id`
        - **Type:** String
        - **Description:** Specifies the receipt id to delete.
        - **Example:** adde4288-e187-42ef-8819-ec07def03ddf

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated not as an admin
        - Status code = `401`:
            ```
            {"detail": "Authentication failed"}
            ```
    - Authenticated as an admin
        - Status code = `204`
        - Status code = `404`:
            ```
            {"detail": "Receipt not found"}
            ```

### Auth
- ***/auth/create_user***: Create user

    **Type:** `POST`

    **Request Body:**
    ```
    {
        "email": "test@gmail.com",
        "first_name": "Test",
        "is_admin": false,
        "last_name": "User",
        "password": "testpassword",
        "username": "testuser"
    }
    ```

    **Server Responses:**
    - Status code = `201` (Response body = null)
    - Status code = `422` (invalid body)

- ***/auth/token***: Get Access Token

    **Type:** `POST`

    **Query Parameters:**

    - `username`
        - **Type:** String
        - **Description:** Specifies the user`s username.

    - `password`
        - **Type:** String
        - **Description:** Specifies the user`s password.

    **Server Responses:**
    - Status code = `200`:
        ```
        {
            "access_token": "...",
            "token_type": "bearer"
        }
        ```
    - Status code = `401`:
        ```
        {"detail": "Could not validate the user"}
        ```

### Receipts
- ***/receipts***: Get all receipts

    **Type:** `GET`

    **Query Parameters:**

    - `page`
        - **Type:** Integer
        - **Description:** Specifies the page number for paginated results.
        - **Default:** 1

    - `size`
        - **Type:** Integer
        - **Description:** Specifies the number of items per page for paginated results.
        - **Default:** 50

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated
        - Status code = `200`:
            ```
            {
                "total_results": 1,
                "page": 1,
                "pages": 1,
                "size": 50,
                "results": [
                    {
                    "id": "daafa0dc-06bb-40fd-8472-c8fa6ed47a43",
                    "products": [
                        {
                            "name": "Bootle of milk",
                            "price": 8.5,
                            "quantity": 2,
                            "total": 17
                        },
                        {
                            "name": "Bottle of water",
                            "price": 5.8,
                            "quantity": 8,
                            "total": 46.4
                        }
                    ],
                    "payment": {
                        "amount": 100,
                        "type": "cashless"
                    },
                    "total": 63,
                    "rest": 37,
                    "created_at": "2024-03-06T17:30:42.809640",
                    "owner_id": 1
                    }
                ]
            }
            ```
        - Status code = `404`:
            ```
            {"detail": "Receipts not found"}
            ```

- ***/receipts/***: Get receipts by payment type

    **Type:** `GET`

    **Query Parameters:**

    - `payment_type`
        - **Type:** String
        - **Description:** Specifies the page number for paginated results.
        - **Allowed Values:** cash, cashless

    - `page`
        - **Type:** Integer
        - **Description:** Specifies the page number for paginated results.
        - **Default:** 1

    - `size`
        - **Type:** Integer
        - **Description:** Specifies the number of items per page for paginated results.
        - **Default:** 50

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated
        - Status code = `200`:
            ```
            {
                "total_results": 1,
                "page": 1,
                "pages": 1,
                "size": 50,
                "results": [
                    {
                    "id": "daafa0dc-06bb-40fd-8472-c8fa6ed47a43",
                    "products": [
                        {
                            "name": "Bootle of milk",
                            "price": 8.5,
                            "quantity": 2,
                            "total": 17
                        },
                        {
                            "name": "Bottle of water",
                            "price": 5.8,
                            "quantity": 8,
                            "total": 46.4
                        }
                    ],
                    "payment": {
                        "amount": 100,
                        "type": "cashless"
                    },
                    "total": 63,
                    "rest": 37,
                    "created_at": "2024-03-06T17:30:42.809640",
                    "owner_id": 1
                    }
                ]
            }
            ```
        - Status code = `404`:
            ```
            {"detail": "Receipts not found"}
            ```

- ***/receipts/last_month***: Get receipts created within last month

    **Type:** `GET`

    **Query Parameters:**

    - `page`
        - **Type:** Integer
        - **Description:** Specifies the page number for paginated results.
        - **Default:** 1

    - `size`
        - **Type:** Integer
        - **Description:** Specifies the number of items per page for paginated results.
        - **Default:** 50

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated
        - Status code = `200`:
            ```
            {
                "total_results": 1,
                "page": 1,
                "pages": 1,
                "size": 50,
                "results": [
                    {
                    "id": "daafa0dc-06bb-40fd-8472-c8fa6ed47a43",
                    "products": [
                        {
                            "name": "Bootle of milk",
                            "price": 8.5,
                            "quantity": 2,
                            "total": 17
                        },
                        {
                            "name": "Bottle of water",
                            "price": 5.8,
                            "quantity": 8,
                            "total": 46.4
                        }
                    ],
                    "payment": {
                        "amount": 100,
                        "type": "cashless"
                    },
                    "total": 63,
                    "rest": 37,
                    "created_at": "2024-03-06T17:30:42.809640",
                    "owner_id": 1
                    }
                ]
            }
            ```
        - Status code = `404`:
            ```
            {"detail": "Receipts not found"}
            ```

- ***/receipts/{total_amount}***: Get receipts more or equal a total_amount

    **Type:** `GET`

    **Query Parameters:**

    - `total_amount`
        - **Type:** Float
        - **Description:** Specifies the total amount of receipt.

    - `page`
        - **Type:** Integer
        - **Description:** Specifies the page number for paginated results.
        - **Default:** 1

    - `size`
        - **Type:** Integer
        - **Description:** Specifies the number of items per page for paginated results.
        - **Default:** 50

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated
        - Status code = `200`:
            ```
            {
                "total_results": 1,
                "page": 1,
                "pages": 1,
                "size": 50,
                "results": [
                    {
                    "id": "daafa0dc-06bb-40fd-8472-c8fa6ed47a43",
                    "products": [
                        {
                            "name": "Bootle of milk",
                            "price": 8.5,
                            "quantity": 2,
                            "total": 17
                        },
                        {
                            "name": "Bottle of water",
                            "price": 5.8,
                            "quantity": 8,
                            "total": 46.4
                        }
                    ],
                    "payment": {
                        "amount": 100,
                        "type": "cashless"
                    },
                    "total": 63,
                    "rest": 37,
                    "created_at": "2024-03-06T17:30:42.809640",
                    "owner_id": 1
                    }
                ]
            }
            ```
        - Status code = `404`:
            ```
            {"detail": "Receipts not found"}
            ```

- ***/receipt/{receipt_id}***: Get receipt by id

    **Type:** `GET`

    **Query Parameters:**

    - `receipt_id`
    - **Type:** String
    - **Description:** Specifies the receipt id
    - **Example:** adde4288-e187-42ef-8819-ec07def03ddf

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated
        - Status code = `200`:
            ```
            {
                "total": 38,
                "payment": {
                    "amount": 40,
                    "type": "cashless"
                },
                "created_at": "2024-03-11T09:12:18.393446",
                "owner_id": 1,
                "rest": 3,
                "id": "8878c286-4d02-4028-afd0-c0f7ea81f18d",
                "products": [
                    {
                        "name": "Bar of chocolate",
                        "price": 10.5,
                        "quantity": 2,
                        "total": 21
                    },
                    {
                        "name": "Bottle of sparkling water",
                        "price": 5.5,
                        "quantity": 3,
                        "total": 16.5
                    }
                ]
            }
            ```
        - Status code = `404`:
            ```
            {"detail": "Receipt not found"}
            ```

- ***/receipt/{receipt_id}***: Delete receipt

    **Type:** `DELETE`

    **Query Parameters:**

    - `receipt_id`
        - **Type:** String
        - **Description:** Specifies the receipt id to delete.
        - **Example:** adde4288-e187-42ef-8819-ec07def03ddf

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated
        - Status code = `204`
        - Status code = `404`:
            ```
            {"detail": "Receipt not found"}
            ```

- ***/receipt***: Create receipt

    **Type:** `POST`

    **Request Body:**
    ```
    {
        "payment": {
            "amount": 100,
            "type": "cashless"
        },
        "products": [
            {
                "name": "Bar of chocolate",
                "price": 2.5,
                "quantity": 1
            },
            {
                "name": "Bottle of sparkling water",
                "price": 5.5,
                "quantity": 1
            }
        ]
    }
    ```

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated
        - Status code = `201`:
            ```
            {
                "products": [
                    {
                        "name": "Bar of chocolate",
                        "price": 2.5,
                        "quantity": 1,
                        "total": 2.5
                    },
                    {
                        "name": "Bottle of sparkling water",
                        "price": 5.5,
                        "quantity": 1,
                        "total": 5.5
                    }
                ],
                "payment": {
                    "amount": 100,
                    "type": "cashless"
                },
                "total": 8,
                "rest": 92,
                "created_at": "2024-03-11T09:27:30.499808",
                "id": "e3610215-b519-44d2-81ba-2e8f6453a156"
            }
            ```
        - Status code = `422` (invalid body)

- ***/receipt/{receipt_id}/text***: Get text view of receipt

    **Type:** `GET`

    **Query Parameters:**

    - `receipt_id`
        - **Type:** String
        - **Description:** Specifies the receipt id
        - **Example:** adde4288-e187-42ef-8819-ec07def03ddf

    - `max_characters_per_line`
        - **Type:** Integer
        - **Description:** Specifies the max number of characters per line
        - **Default:** 50

    **Server Responses:**
    - Status code = `200`:
        ```
                          ФОП TEST USER
        ==================================================
        1.00 x 2.50
        Bar of chocolate                              2.50
        --------------------------------------------------
        1.00 x 5.50
        Bottle of sparkling water                     5.50
        --------------------------------------------------
        ==================================================
        СУМА                                          8.00
        Картка                                      100.00
        Решта                                        92.00
        ==================================================
                    11.03.2024 09:12:39
                    Дякуємо за покупку!
        ```
    - Status code = 404:
        ```
        {"detail": "Receipt not found"}
        ```

### User
- ***/user***: Get user

    **Type:** `GET`

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated
        - Status code = `200`:
            ```
            {
                "email": "test@gmail.com",
                "username": "testuser",
                "id": 1,
                "hashed_password": "",
                "first_name": "Test",
                "last_name": "User",
                "is_admin": true
            }
            ```
- ***/user/password***: Create receipt

    **Type:** `POST`

    **Request Body:**
    ```
    {
        "password": "testpassword",
        "new_password": "newpassword"
    }
    ```

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated
        - Status code = `201`
        - Status code = `401` (invalid username or password)
            ```
            {"detail": "Error on password change"}
            ```
        - Status code = `422` (invalid body)

- ***/user/delete***: Delete user

    **Type:** `DELETE`

    **Server Responses:**
    - Not authenticated
        - Status code = `401`:
            ```
            {"detail": "Not authenticated"}
            ```
    - Authenticated
        - Status code = `204`

## Environment Variables
Make sure to set the following environment variables in **.env** file:
```
SECRET_KEY: Secret key for JWT token generation
ALGORITHM: Algorithm used for JWT token encoding
DB_USERNAME: username for connecting to the database
DB_PASSWORD: password for connecting to the database
DB_NAME: database name for connecting to the database
DB_HOST: database host for connecting to the database
DB_PORT: database port for connecting to the database
```

## Contributing
Contributions are welcome! Please feel free to submit issues and pull requests.
