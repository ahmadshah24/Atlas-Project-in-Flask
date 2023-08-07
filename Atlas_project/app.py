from flask import render_template, request, redirect, url_for, flash
from __init__ import db, create_app
from models import Customer, Vendor, Product, Purchase, Sale, Return, Receipt
from datetime import datetime
from sqlalchemy.orm import aliased

app = create_app()

# Routes and route handling go here
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sales')
def sales():
    # Fetch all sales from the database and join with Product and Customer to get product and customer names
    sales = db.session.query(Sale, Product.name.label('product_name'), Customer.name.label('customer_name')) \
        .join(Product, Sale.product_id == Product.id) \
        .join(Customer, Sale.customer_id == Customer.id) \
        .all()
    total_sum = sum(sale[0].total for sale in sales)

    # Fetch all products and customers separately
    products = Product.query.all()
    customers = Customer.query.all()

    return render_template('sales.html', sales=sales, total_sum=total_sum, products=products, customers=customers)

@app.route('/add_sale', methods=['POST', 'GET'])
def add_sale():
    if request.method == 'POST':
        product_name = request.form['product_name']
        customer_name = request.form['customer_name']
        date_str = request.form['date']
        amount = int(request.form['amount'])
        unitprice = float(request.form['unitprice'])

        # Convert the date string to a Python date object
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Find the product and customer objects using their names
        product = Product.query.filter_by(name=product_name).first()
        customer = Customer.query.filter_by(name=customer_name).first()

        # Check if the product and customer exist
        if product is None or customer is None:
            return "Invalid product or customer"

        # Calculate the available quantity of the product
        purchased_quantity = sum([purchase.quantity for purchase in Purchase.query.filter_by(product_id=product.id).all()])
        sold_quantity = sum([sale.amount for sale in Sale.query.filter_by(product_id=product.id).all()])
        available_quantity = purchased_quantity - sold_quantity

        # Check if the requested amount to sell is greater than the available quantity
        if amount > available_quantity:
            return "Not enough stock available for sale"

        # Create the new Sale object and add it to the database
        new_sale = Sale(
            product_id=product.id,
            customer_id=customer.id,
            date=date,
            amount=amount,
            unitprice=unitprice
        )
        db.session.add(new_sale)
        db.session.commit()

        return redirect(url_for('sales'))


    # Fetch all products and customers to pass to the template
    products = Product.query.all()
    customers = Customer.query.all()

    return render_template('add_sale.html', products=products, customers=customers) 

@app.route('/delete_sale/<int:sale_id>', methods=['POST'])
def delete_sale(sale_id):
    sale = Sale.query.get(sale_id)
    if sale:
        db.session.delete(sale)
        db.session.commit()
    return redirect(url_for('sales'))

@app.route('/update_sale/<int:sale_id>', methods=['GET', 'POST'])
def update_sale(sale_id):
    sale = Sale.query.get(sale_id)
    if not sale:
        return "Sale not found", 404

    customers = Customer.query.all()
    products = Product.query.all()

    if request.method == 'POST':
        # Get the updated values from the form data
        customer_id = request.form.get('customer')
        product_id = request.form.get('product')
        date_str = request.form.get('date')
        amount = int(request.form.get('amount'))
        unitprice = float(request.form.get('unitprice'))

        # Convert the date string to a Python date object
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Find the customer and product objects using their IDs
        customer = Customer.query.get(customer_id)
        product = Product.query.get(product_id)

        # Check if the customer and product exist
        if not customer or not product:
            return "Invalid customer or product", 400

        # Update the sale object with the new values
        sale.customer = customer
        sale.product = product
        sale.date = date
        sale.amount = amount
        sale.unitprice = unitprice

        # Commit the changes to the database
        db.session.commit()

        return redirect(url_for('sales'))

    return render_template('update_sale.html', sale=sale, customers=customers, products=products)


@app.route('/purchases')
def purchases():
    purchases = Purchase.query.all()
    vendors = Vendor.query.all()
    products = Product.query.all()
    total_sum = sum(purchase.total for purchase in purchases)
    return render_template('purchases.html', purchases=purchases, total_sum=total_sum, vendors=vendors, products=products)

 
@app.route('/add_purchase', methods=['POST'])
def add_purchase():
    if request.method == 'POST':
        product_id = request.form['product_id']
        vendor_id = request.form['vendor_id']
        date_str = request.form['date']  # Get the date string from the form

        # Convert the date string to a Python date object
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        quantity = int(request.form['quantity'])
        unitprice = float(request.form['unitprice'])

        # Find the product and vendor objects using their IDs
        product = Product.query.get(product_id)
        vendor = Vendor.query.get(vendor_id)

        # Check if the product and vendor exist
        if product is None or vendor is None:
            return "Invalid product or vendor"

        # Create the new Purchase object and add it to the database
        new_purchase = Purchase(
            date=date,
            quantity=quantity,
            unitprice=unitprice,
            product_id=product_id,
            vendor_id=vendor_id
        )
        db.session.add(new_purchase)
        db.session.commit()

        return redirect(url_for('purchases'))

    # Fetch all products and vendors to pass to the template
    products = Product.query.all()
    vendors = Vendor.query.all()

    return render_template('add_purchase.html', products=products, vendors=vendors)

@app.route('/delete_purchase/<int:purchase_id>', methods=['POST'])
def delete_purchase(purchase_id):
    purchase = Purchase.query.get(purchase_id)
    if purchase:
        db.session.delete(purchase)
        db.session.commit()
    return redirect(url_for('purchases'))


@app.route('/update_purchase/<int:purchase_id>', methods=['POST','GET'])
def update_purchase(purchase_id):
    purchase = Purchase.query.get(purchase_id)
    if not purchase:
        return "Purchase not found", 404

    vendors = Vendor.query.all()
    products = Product.query.all()

    if request.method == 'POST':
        # Get the updated values from the form data
        vendor_id = request.form.get('vendor')
        product_id = request.form.get('product')
        date_str = request.form.get('date')
        quantity = int(request.form.get('quantity'))
        unitprice = float(request.form.get('unitprice'))

        # Convert the date string to a Python date object
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Find the vendor and product objects using their IDs
        vendor = Vendor.query.get(vendor_id)
        product = Product.query.get(product_id)

        # Check if the vendor and product exist
        if not vendor or not product:
            return "Invalid vendor or product", 400

        # Update the purchase object with the new values
        purchase.vendor = vendor
        purchase.product = product
        purchase.date = date
        purchase.quantity = quantity
        purchase.unitprice = unitprice

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the purchases page after updating
        return redirect(url_for('purchases'))
    
    return render_template('update_purchase.html', purchase=purchase, vendors=vendors, products=products)


@app.route('/stock')
def stock():
    products = Product.query.all()

    for product in products:
        # Calculate the purchased_product
        purchased_product = sum([purchase.quantity for purchase in Purchase.query.filter_by(product_id=product.id).all()])
        product.purchased_product = purchased_product

        # Calculate the sold_product
        sold_product = sum([sale.amount for sale in Sale.query.filter_by(product_id=product.id).all()])
        product.sold_product = sold_product

        # Calculate the remaining stock (reminder_product)
        reminder_product = purchased_product - sold_product
        product.reminder_product = reminder_product

    return render_template('stock.html', products=products)


# app.py
# ... (other imports)

@app.route('/products')
def products():
    # Fetch all products from the database
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        size = request.form['size']
        PR = request.form['PR']

        # Create a new Product object with the form data
        new_product = Product(name=name, type=type, size=size, PR=PR)

        # Add the new product to the database
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('products'))  # Redirect to the 'products' page after adding the product

    return render_template('add_product.html')




@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product: 
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('products'))


# Edit Product
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product_obj = Product.query.get(product_id)
    if not product_obj:
        return "Product not found", 404

    if request.method == 'POST':
        # Handle form submission for updating the product data
        # Get the updated values from the form data
        name = request.form.get('name')
        type = request.form.get('type')
        size = request.form.get('size')
        PR = request.form.get('PR')

        # Update the product object with the new values
        product_obj.name = name
        product_obj.type = type
        product_obj.size = size
        product_obj.PR = PR

        # Commit the changes to the database
        db.session.commit()

        return redirect(url_for('products'))

    return render_template('edit_product.html', product_obj=product_obj)


# Update Product
@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    product_obj = Product.query.get(product_id)
    if not product_obj:
        return "Product not found", 404

    # Get the updated values from the form data
    name = request.form.get('name')
    type = request.form.get('type')
    size = request.form.get('size')
    PR = request.form.get('PR')

    # Update the product object with the new values
    product_obj.name = name
    product_obj.type = type
    product_obj.size = size
    product_obj.PR = PR

    # Commit the changes to the database
    db.session.commit()

    return redirect(url_for('products'))


 
@app.route('/vendors')
def vendors():
    vendors = Vendor.query.all()
    return render_template('vendors.html', vendors=vendors)

@app.route('/add_vendor', methods=['GET', 'POST'])
def add_vendor():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        phone = request.form['phone']

        new_vendor = Vendor(name=name, address=address, email=email, phone=phone)
        db.session.add(new_vendor)
        db.session.commit()

        return redirect(url_for('vendors'))

    return render_template('vendor.html')

@app.route('/delete_vendor/<int:vendor_id>', methods=['POST'])
def delete_vendor(vendor_id):
    vendor =  Vendor.query.get(vendor_id)
    if vendor: 
        db.session.delete(vendor)
        db.session.commit()
    return redirect(url_for('vendors'))


@app.route('/edit_vendor/<int:vendor_id>', methods=['GET', 'POST'])
def edit_vendor(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return "Vendor not found", 404

    if request.method == 'POST':
        # Handle form submission for updating the vendor data
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')

        # Update the vendor object with the new values
        vendor.name = name
        vendor.phone = phone
        vendor.address = address

        # Commit the changes to the database
        db.session.commit()

        return redirect(url_for('vendors'))

    return render_template('edit_vendor.html', vendor=vendor)

@app.route('/customers')
def customers():
    customers = Customer.query.all()

    for customer in customers:
        customer.sale_total = sum([sale.total for sale in Sale.query.filter_by(customer_id=customer.id).all()])
        returns_total = sum([ret.total for ret in Return.query.filter_by(customer_id=customer.id).all()])
        customer.return_total = returns_total
        # receipt_total = db.session.query(func.sum(Receipt.total)).filter_by(customer_id=customer.id).scalar()
        receipt_total = sum([receipt.total for receipt in Receipt.query.filter_by(customer_id=customer.id).all()])
        customer.receipt_total = receipt_total if receipt_total else 0


    return render_template('customer.html', customers=customers)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        # receipt = request.form['receipts']

        new_customer = Customer(name=name, phone=phone, address=address)
        
        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for('customers'))

    return render_template('customer.html')

@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if customer : 
        db.session.delete(customer)
        db.session.commit()
    return redirect(url_for('customers'))

@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return "Customer not found", 404

    if request.method == 'POST':
        # Handle form submission for updating the vendor data
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')

        # Update the vendor object with the new values
        customer.name = name
        customer.phone = phone
        customer.address = address

        # Commit the changes to the database
        db.session.commit()

        return redirect(url_for('customers'))

    return render_template('edit_customer.html', customer=customer)

@app.route('/returns')
def returns():
    # Create aliased constructs for the Product and Customer models
    product_alias = aliased(Product)
    customer_alias = aliased(Customer)

    # Fetch all returns from the database and join with Product and Customer to get product and customer names
    returns = db.session.query(Return, product_alias.name.label('product_name'), customer_alias.name.label('customer_name')) \
        .join(product_alias, Return.product_id == product_alias.id) \
        .join(customer_alias, Return.customer_id == customer_alias.id) \
        .all()

    # Fetch all products and customers separately
    products = Product.query.all()
    customers = Customer.query.all()

    return render_template('returns.html', returns=returns, products=products, customers=customers)


@app.route('/add_return', methods=['GET', 'POST'])
def add_return():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        product_id = request.form['product_id']
        date_str = request.form['date']
        amount = int(request.form['amount'])
        unitprice = float(request.form['unitprice'])

        # Convert the date string to a Python date object
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Find the product and customer objects using their IDs
        product = Product.query.get(product_id)
        customer = Customer.query.get(customer_id)

        # Check if the product and customer exist
        if product is None or customer is None:
            return "Invalid product or customer"

        # Create the new Return object and add it to the database
        new_return = Return(
            customer_id=customer.id,
            product_id=product.id,
            date=date,
            amount=amount,
            unitprice=unitprice
        )
        db.session.add(new_return)
        db.session.commit()

        return redirect(url_for('returns'))

    # Fetch all products and customers to pass to the template
    products = Product.query.all()
    customers = Customer.query.all()

    return render_template('add_return.html', products=products, customers=customers)


@app.route('/delete_return/<int:return_id>', methods=['POST','GET'])
def delete_return(return_id):
    return_obj = Return.query.get(return_id)
    if return_obj:
        db.session.delete(return_obj)
        db.session.commit()
    return redirect(url_for('returns'))

@app.route('/edit_return/<int:return_id>', methods=['GET', 'POST'])
def edit_return(return_id):
    return_obj = Return.query.get(return_id)
    if not return_obj:
        return "Return not found", 404

    # Access the associated Customer and Product objects using the 'customer' and 'product' relationships
    customer_obj = return_obj.customer
    product_obj = return_obj.product

    customers = Customer.query.all()
    products = Product.query.all()

    if request.method == 'POST':
        # Handle form submission for updating the return data
        # ...

        # After processing the POST request, you should redirect to the 'returns' page
        return redirect(url_for('returns'))

    return render_template('edit_return.html', return_obj=return_obj, customer_obj=customer_obj, product_obj=product_obj, customers=customers, products=products)

 
@app.route('/update_return/<int:return_id>', methods=['POST','GET'])
def update_return(return_id):
    return_obj = Return.query.get(return_id)
    if not return_obj:
        return "Return not found", 404

    # Get the updated values from the form data
    customer_id = request.form.get('customer')
    product_id = request.form.get('product')
    date_str = request.form.get('date')
    amount = int(request.form.get('amount'))
    unitprice = float(request.form.get('unitprice'))

    # Convert the date string to a Python date object
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Find the customer and product objects using their IDs
    customer = Customer.query.get(customer_id)
    product = Product.query.get(product_id)

    # Check if the customer and product exist
    if not customer or not product:
        return "Invalid customer or product", 400

    # Update the return object with the new values
    return_obj.customer = customer
    return_obj.product = product
    return_obj.date = date
    return_obj.amount = amount
    return_obj.unitprice = unitprice

    # Commit the changes to the database
    db.session.commit()

    return redirect(url_for('returns'))

@app.route('/receipts')
def receipts():
    receipts = Receipt.query.all()
    total_sum = sum(receipt.total for receipt in receipts)
    customers = Customer.query.all()

    return render_template('receipts.html', receipts=receipts, customers=customers, total_sum=total_sum)


@app.route('/add_receipt', methods=['POST', 'GET'])
def add_receipt():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        date_str = request.form['date']
        total = float(request.form['total'])

        # Convert the date string to a Python date object
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Find the customer object using the provided customer_id
        customer = Customer.query.get(customer_id)

        if customer is None:
            return "Invalid customer ID"

        # Create the new Receipt object and add it to the database
        new_receipt = Receipt(date=date, total=total, customer=customer)
        db.session.add(new_receipt)
        db.session.commit()

        return redirect(url_for('receipts'))
    else:
        customers = Customer.query.all()
        return render_template('add_receipt.html', customers=customers)



@app.route('/delete_receipt/<int:receipt_id>', methods=['POST'])
def delete_receipt(receipt_id):
    receipt = Receipt.query.get(receipt_id)
    if receipt:
        db.session.delete(receipt)
        db.session.commit()
    return redirect(url_for('receipts'))

@app.route('/update_receipt/<int:receipt_id>', methods=['GET', 'POST'])
def update_receipt(receipt_id):
    receipt = Receipt.query.get(receipt_id)
    if not receipt:
        return "Sale not found", 404

    customers = Customer.query.all()

    if request.method == 'POST':
        # Get the updated values from the form data
        customer_id = request.form.get('customer')
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        customer = Customer.query.get(customer_id)

        # Check if the customer and product exist
        if not customer:
            return "Invalid customer or product", 400

        receipt.customer = customer
        receipt.date = date

        # Commit the changes to the database
        db.session.commit()

        return redirect(url_for('receipts'))

    return render_template('update_receipt.html', receipt=receipt, customers=customers)

# Define similar routes for other pages (stock, products, customers)...
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)