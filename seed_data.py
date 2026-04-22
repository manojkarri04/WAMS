from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from models import Base, Product, MaterialRequest

# Connect to your existing database
engine = create_engine('sqlite:///wams.db')
Session = sessionmaker(bind=engine)
session = Session()

def seed_database():
    # 1. Create some initial Products for Dealers to request
    products = [
        Product(product_name="Industrial Motor V1", category="Machinery", unit_price=450.00, stock_level=50),
        Product(product_name="Conveyor Belt (10m)", category="Parts", unit_price=120.00, stock_level=10),
        Product(product_name="Control Panel Unit", category="Electronics", unit_price=850.00, stock_level=5)
    ]
    
    # 2. Create some initial Material Requests for Suppliers to quote on
    materials = [
        MaterialRequest(material_name="Raw Steel (100kg)", quantity=5, status="Open"),
        MaterialRequest(material_name="Copper Wiring (500m)", quantity=2, status="Open"),
        MaterialRequest(material_name="Microchips (Batch of 1000)", quantity=1, status="Open")
    ]

    # Add everything to the database
    try:
        session.add_all(products)
        session.add_all(materials)
        session.commit()
        print("✅ Database successfully seeded! You can now test your UI.")
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")

if __name__ == "__main__":
    seed_database()