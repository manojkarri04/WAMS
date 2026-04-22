from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from sqlalchemy import func

# In controllers.py
# Import all schemas from models.py
from models import Base, User, Dealer, Admin, Supplier, ManagementAuthority, Product, Order, ProductionBatch

# --- DATABASE SETUP ---
engine = create_engine('sqlite:///wams.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# --- AUTHENTICATION LOGIC ---
def register_user(email, password, role_choice, name=""):
    """Registers a new user into their respective database table."""
    existing_user = session.query(User).filter_by(email=email).first()
    if existing_user:
        return False, "This email is already registered. Please sign in."

    try:
        # SQLAlchemy automatically sets the "role" string based on the class we use!
        if role_choice == "Admin":
            new_user = Admin(email=email, _password=password, name=name)
        elif role_choice == "Dealer":
            new_user = Dealer(email=email, _password=password)
        elif role_choice == "Supplier":
            new_user = Supplier(email=email, _password=password)
        elif role_choice == "Management Authority":
            new_user = ManagementAuthority(email=email, _password=password)
        else:
            return False, "Invalid role selected."

        session.add(new_user)
        session.commit()
        return True, f"{role_choice} account created successfully! You can now sign in."
        
    except Exception as e:
        session.rollback()
        return False, f"An error occurred: {str(e)}"

# --- ORDER & PRODUCT LOGIC ---
def fetchAvailableProducts():
    return session.query(Product).all()

def submitRequest(dealer_id, product_id, quantity):
    product = session.query(Product).filter_by(product_id=product_id).first()
    
    if not product:
        return False, "Product not found."

    if product.stock_level >= quantity:
        new_order = Order(
            dealer_id=dealer_id, 
            product_id=product_id, 
            quantity=quantity, 
            order_date=datetime.date.today(),
            status="Pending"
        )
        product.stock_level -= quantity
        session.add(new_order)
        session.commit()
        return True, "Request submitted successfully. Admin notified."
    else:
        return False, f"Insufficient stock. Only {product.stock_level} units available."
    
# Add these functions to controllers.py

def fetchPendingOrders():
    """Retrieves all orders currently awaiting production."""
    return session.query(Order).filter_by(status="Pending").all()

def generateProductionBatch(order_id, product_id, quantity):
    """Admin Use Case 5: Assigns a production batch to a request[cite: 147, 151]."""
    order = session.query(Order).filter_by(order_id=order_id).first()
    if not order:
        return False, "Order not found."
    
    try:
        # Create a new production batch
        new_batch = ProductionBatch(
            quantity=quantity,
            status="In Production",
            end_date=datetime.date.today() + datetime.timedelta(days=7), # Estimated 1 week
            product_id=product_id
        )
        
        # Update the dealer request status
        order.status = "In Production" # [cite: 152]
        
        session.add(new_batch)
        session.commit()
        return True, "Production batch generated and order status updated."
    except Exception as e:
        session.rollback()
        return False, f"Database error: {str(e)}"

def updateStockAfterSale(product_id, quantity_sold):
    """Dealer Use Case 2: Updates inventory after a dealer makes a sale[cite: 92, 99]."""
    product = session.query(Product).filter_by(product_id=product_id).first()
    
    if not product:
        return False, "Invalid ID error." # [cite: 109]
        
    if product.stock_level < quantity_sold:
        return False, "Sale quantity cannot exceed current inventory." # [cite: 113]
        
    try:
        product.stock_level -= quantity_sold # [cite: 103]
        session.commit()
        return True, "Stock updated successfully." # [cite: 106]
    except Exception as e:
        session.rollback()
        return False, "Update Failed: Database Unreachable." # [cite: 115]
    
# Add these functions to controllers.py

from models import MaterialRequest, Quotation

def fetchOpenMaterialRequests():
    """Retrieves all material requests awaiting quotations[cite: 135]."""
    return session.query(MaterialRequest).filter_by(status="Open").all()

def submitSupplierQuotation(supplier_id, request_id, price, lead_time):
    """Supplier Use Case 4: Submits a quotation for a material request[cite: 132, 137]."""
    
    # Alternate Scenario 2(a): Missing Information [cite: 140]
    if price <= 0 or lead_time <= 0:
        return False, "System Error: Price and Time fields cannot be empty or zero." # [cite: 141, 142]
        
    request = session.query(MaterialRequest).filter_by(request_id=request_id).first()
    
    # Alternate Scenario 3(a): Request Expired/Closed [cite: 143, 144]
    if not request or request.status != "Open":
        return False, "Request Closed: This request is no longer accepting quotations." # [cite: 145]
        
    try:
        new_quote = Quotation(
            quoted_price=price,
            lead_time_days=lead_time,
            supplier_id=supplier_id,
            request_id=request_id
        )
        session.add(new_quote)
        session.commit()
        return True, "Quotation submitted successfully!"
    except Exception as e:
        session.rollback()
        return False, f"Database error: {str(e)}"
    

# Add this function to the bottom of controllers.py


def generateStockAnalysis():
    """DSS Use Case 7: Generates sales trend and stock recommendations."""
    # Define the 1-week threshold for the Alternate Scenario
    one_week_ago = datetime.date.today() - datetime.timedelta(days=7)
    
    products = session.query(Product).all()
    report_data = []
    sufficient_data = False

    for product in products:
        # Fetch historical orders (dealer requests) for this product
        past_orders = session.query(Order).filter(
            Order.product_id == product.product_id,
            Order.status != "Pending" # Only count actualized orders
        ).all()
        
        # Check if we have orders older than a week to satisfy the data requirement
        older_orders = [o for o in past_orders if o.order_date < one_week_ago]
        if older_orders:
            sufficient_data = True
            
        total_ordered = sum(o.quantity for o in past_orders)
        
        # DSS Logic: Recommend restocking if current stock is dangerously low compared to historical demand
        recommended_restock = 0
        if product.stock_level < (total_ordered * 0.4): # Reorder threshold
            # Recommend ordering enough to cover historical demand plus a 20% buffer
            recommended_restock = int(total_ordered * 1.2) - product.stock_level
            recommended_restock = max(0, recommended_restock)

        report_data.append({
            "Product ID": product.product_id,
            "Product Name": product.product_name,
            "Current Stock": product.stock_level,
            "Historical Demand": total_ordered,
            "Recommended Restock": recommended_restock
        })
        
    return sufficient_data, report_data