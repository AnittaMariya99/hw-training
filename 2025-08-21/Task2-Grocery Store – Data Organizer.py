# Task2-Inventory and Shopping Cart System

# dictionary with items and their prices
inventory = {
    "apple": 30.5,
    "milk": 45.0,
    "bread": 25.0,
    "egg": 5.0
}

# cart with some items (2-3 items)
cart = ["apple", "milk", "cake"]   # cake is not in inventory

# check data types
print("Type of inventory:", type(inventory))
print("Type of one price value:", type(inventory["apple"]))
print("Type of cart:", type(cart))

# total bill calculation
total = 0
for item in cart:
    if item in inventory:   # item is available
        total = total + inventory[item]
    else:                   # item not available
        print("Warning:", item, "is not available in inventory")

print("Total Bill =", total)

# convert cart to set
cart_set = set(cart)
print("Unique items in cart:", cart_set)

# tuple of product categories
categories = ("fruits", "dairy", "bakery")
print("Categories:", categories)
print("Type of categories:", type(categories))

# add item with None price
inventory["unknown_item"] = None
print("Type of unknown_item price:", type(inventory["unknown_item"]))

# discount check
is_discount_applied = False
if total > 100:
    is_discount_applied = True
    print("Discount Applied!")
else:
    print("No Discount")

print("is_discount_applied type:", type(is_discount_applied))

# final bill summary
print("---- Bill Summary ----")
print("Cart items:", cart)
print("Unique items:", cart_set)
print("Total Bill:", total)
print("Discount Applied:", is_discount_applied)