# Little Lemon API test plan

Base URL: `http://127.0.0.1:8000`

## Start the project

```bash
pipenv install
pipenv run python manage.py migrate
pipenv run python manage.py seed_demo
pipenv run python manage.py runserver
```

Use `POST /auth/token/login/` with JSON `{"username":"admin","password":"AdminDemo123!"}` (or another demo account) to receive `auth_token`. For protected requests, set header `Authorization: Token <auth_token>`.

## Tests mapped to the 21 grading requirements

1. **Admin assigns manager:** authenticate as `admin`; `POST /api/groups/manager/users` with `{"username":"customer"}`; expect 200 and a success message.
2. **Admin accesses manager group:** `GET /api/groups/manager/users` as admin; expect 200 and a JSON list.
3. **Admin adds menu item:** `POST /api/menu-items/` as admin with `{"title":"Demo Item","price":"9.50","category":1,"featured":false}`; expect 201.
4. **Admin adds category:** `POST /api/categories/` as admin with `{"title":"Drinks","slug":"drinks"}`; expect 201.
5. **Manager logs in:** `POST /auth/token/login/` with manager credentials; expect `auth_token`.
6. **Manager updates item of the day:** `PATCH /api/menu-items/1/` as manager with `{"featured":true}`; expect 200 and `featured: true`.
7. **Manager assigns delivery crew:** `POST /api/groups/delivery-crew/users` as manager with `{"username":"customer"}`; expect 200.
8. **Manager assigns an order:** create an order as customer, then `PATCH /api/orders/<id>` as manager with `{"delivery_crew":<delivery-user-id>}`; expect 200.
9. **Crew sees assigned orders:** `GET /api/orders` as delivery crew; expect only orders assigned to that user.
10. **Crew marks delivered:** `PATCH /api/orders/<id>` as the assigned crew member with `{"status":true}`; expect 200 and `status: true`.
11. **Customer registers:** `POST /auth/users/` with `{"username":"newcustomer","password":"SafeDemoPass123!"}`; expect user details / 201.
12. **Customer logs in:** `POST /auth/token/login/` with customer username/password; expect `auth_token`.
13. **Browse categories:** `GET /api/categories/`; expect category list.
14. **Browse menu items:** `GET /api/menu-items/`; expect paginated results.
15. **Filter by category:** `GET /api/menu-items/?category=1`; expect items in category 1.
16. **Pagination:** `GET /api/menu-items/?page=2`; expect page results and pagination links/fields.
17. **Sort by price:** `GET /api/menu-items/?ordering=price`; expect ascending price order. Use `?ordering=-price` for descending.
18. **Add to cart:** `POST /api/cart/menu-items` as customer with `{"menuitem":1,"quantity":2}`; expect cart item.
19. **View cart:** `GET /api/cart/menu-items` as same customer; expect their cart items.
20. **Place order:** `POST /api/orders` as customer after adding cart items; expect 201 and the cart to be emptied.
21. **View own orders:** `GET /api/orders` as customer; expect only that customer's orders.

## Negative permission checks

- Unauthenticated `POST /api/menu-items/` should be rejected.
- Customer attempts to assign manager/delivery-crew group members should receive 403.
- A delivery crew member should not be able to read or update another crew member's assigned order.
- A customer should not be able to update or delete orders.

If any request differs, record the URL, method, status code, response body, and account role. Test using disposable local accounts only.
