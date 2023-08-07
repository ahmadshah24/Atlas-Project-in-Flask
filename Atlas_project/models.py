from __init__ import db
from datetime import date



class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    receipts = db.relationship('Receipt', backref='customer', lazy=True)

    def __repr__(self):
        return f"<Customer {self.id} - {self.name}>"





class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)

    purchases = db.relationship('Purchase', backref='vendor')
    def __repr__(self):
        return f"<Vendor {self.name}>"
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    PR = db.Column(db.String(20), nullable=False)

    purchases = db.relationship('Purchase', backref='product')
    sales = db.relationship('Sale', backref='product')
    # receipts = db.relationship('Receipt', backref='product')

    def __repr__(self):
        return f"<Product {self.name}>"




 
class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unitprice = db.Column(db.Float, nullable=False)

    # Foreign keys for relationships
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)

    @property
    def total(self):
        return self.quantity * self.unitprice

    def __repr__(self):
        return f"<Purchase {self.product.name} - {self.vendor.name}>"

# models.py

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    unitprice = db.Column(db.Float, nullable=False)

    # Foreign keys for relationships
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

    @property
    def total(self):
        return self.amount * self.unitprice

    def __repr__(self):
        return f"<Sale {self.product.name} - {self.customer.name}>"


class Return(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    unitprice = db.Column(db.Float, nullable=False)
    customer = db.relationship('Customer', backref='returns', foreign_keys=[customer_id])
    product = db.relationship('Product', backref='returns', foreign_keys=[product_id])

    @property
    def total(self):
        return self.amount * self.unitprice

    def __repr__(self):
        return f"<Return {self.id}>"
    


class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    total = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

    def __repr__(self):
        return f"<Receipt {self.id}>"


