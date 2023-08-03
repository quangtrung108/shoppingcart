from market import app
from flask import render_template, jsonify, request, session

# Sample data for items
items = [
    {
        "id": 1,
        "name": "Bulbasaur",
        "description": "This is the first product",
        "image": "/static/images/bulbasaur.jpeg",
        "price": 10,
        "quantity": 10
    },
    {
        "id": 2,
        "name": "Squirtle",
        "description": "This is the second product",
        "image": "/static/images/squirtle.jpeg",
        "price": 20,
        "quantity": 5
    },
    {
        "id": 3,
        "name": "Charmender",
        "description": "This is the third product",
        "image": "/static/images/charmender.png",
        "price": 40,
        "quantity": 0
    }
]

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market', methods=['GET', 'POST'])
def market_page():
    # Calculate the total of all items in the cart
    total = 0
    cart = session.get('cart', [])

    for item in cart:
        total += item['price'] * item['quantity']

    return render_template('market.html', items=items, cart=cart, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity')

    if not item_id or not quantity:
        return jsonify({"success": False, "message": "Invalid request data."})

    # Retrieve the cart from the session
    cart = session.get('cart', [])

    # Check if the item with the given ID already exists in the cart
    existing_item = next((item for item in cart if item['id'] == item_id), None)

    # Find the item from the items list with the given ID
    item = next((item for item in items if item['id'] == item_id), None)

    if not item:
        return jsonify({"success": False, "message": "Item not found."})

    if existing_item:
        # If the item already exists in the cart, update its quantity
        existing_quantity = existing_item['quantity']
        new_quantity = int(quantity)

        # Check if the total quantity in cart exceeds the available quantity
        if item['quantity'] < (existing_quantity + new_quantity):
            return jsonify({"success": False, "message": "Insufficient quantity available."})

        existing_item['quantity'] += new_quantity
    else:
        # If the item doesn't exist in the cart, add it to the cart
        new_quantity = int(quantity)

        # Check if the requested quantity exceeds the available quantity
        if item['quantity'] < new_quantity:
            return jsonify({"success": False, "message": "Insufficient quantity available."})

        new_item = {
            'id': item['id'],
            'name': item['name'],
            'quantity': new_quantity,
            'price': item['price']
        }
        cart.append(new_item)

    # Reduce the item quantity in the items list
    item['quantity'] -= new_quantity

    # Save the updated cart back to the session
    session['cart'] = cart

    return jsonify({"success": True, "message": "Item added to the cart successfully!"})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    item_id = data.get('item_id')

    if item_id is None:
        return jsonify(success=False, message="Invalid request data.")

    cart = session.get('cart', [])
    cart_item = next((item for item in cart if item['id'] == item_id), None)
    if not cart_item:
        return jsonify(success=False, message="Item not found in the cart.")

    # Remove the item from the cart
    cart.remove(cart_item)

    # Update the item quantity in the items list
    item = next((item for item in items if item['id'] == item_id), None)
    if item:
        item['quantity'] += cart_item['quantity']

    # Save the updated cart back to the session
    session['cart'] = cart

    return jsonify(success=True, message="Item removed from the cart successfully!")

@app.route('/update_cart_item', methods=['POST'])
def update_cart_item():
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity')

    if item_id is None or quantity is None:
        return jsonify(success=False, message="Invalid request data.")

    cart = session.get('cart', [])
    cart_item = next((item for item in cart if item['id'] == item_id), None)
    if not cart_item:
        return jsonify(success=False, message="Item not found in the cart.")

    # Convert the quantity values to integers before performing operations
    cart_item_quantity = int(cart_item['quantity'])
    requested_quantity = int(quantity)

    # Update the item quantity in the cart
    cart_item['quantity'] = quantity

    # Update the item quantity in the items list
    item = next((item for item in items if item['id'] == item_id), None)
    if item:
        # Update the items list quantity based on the difference in cart quantities
        item['quantity'] += cart_item_quantity - requested_quantity

    # Save the updated cart back to the session
    session['cart'] = cart

    return jsonify(success=True, message="Cart item updated successfully!")