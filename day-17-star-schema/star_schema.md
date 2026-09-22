# Star Schema — E-Commerce Orders

One fact table at the center, surrounded by dimension tables that each
describe one aspect of an order. This is the dimensional-modelling
counterpart to Day 7's normalized 5-table MySQL schema: instead of
minimizing redundancy, a star schema deliberately denormalizes each
dimension into one wide, flat table so analytical queries (like Day 13's
rolling revenue and top-customer queries) can run with simple joins
instead of long normalized join chains.

```mermaid
erDiagram
    FACT_ORDERS }o--|| DIM_CUSTOMER : "placed by"
    FACT_ORDERS }o--|| DIM_PRODUCT : "for"
    FACT_ORDERS }o--|| DIM_DATE : "on"
    FACT_ORDERS }o--|| DIM_PAYMENT_METHOD : "paid via"

    FACT_ORDERS {
        int order_key PK
        int order_id
        int customer_key FK
        int product_key FK
        int date_key FK
        int payment_method_key FK
        int quantity
        decimal unit_price
        decimal total_amount
    }

    DIM_CUSTOMER {
        int customer_key PK
        int customer_id
        string customer_name
        string region
        string segment
    }

    DIM_PRODUCT {
        int product_key PK
        int product_id
        string product_name
        string category
        string subcategory
    }

    DIM_DATE {
        int date_key PK
        date full_date
        string day_of_week
        string month
        int quarter
        int year
    }

    DIM_PAYMENT_METHOD {
        int payment_method_key PK
        string payment_method
        string payment_type
    }
```
