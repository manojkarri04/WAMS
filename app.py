import streamlit as st
import pandas as pd

import os
from seed_data import seed_database

from models import User, Product, Order
# Updated Line 4 in app.py
from controllers import session, fetchAvailableProducts, submitRequest, register_user, updateStockAfterSale

# --- SESSION STATE SETUP ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

# --- AUTHENTICATION PORTAL ---
if not st.session_state['logged_in']:
    st.title("Manufacturing System Portal")
    
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])

# -- SIGN IN --
    with tab1:
        st.write("### Welcome Back")
        with st.form("signin_form"):
            email_input = st.text_input("Email Address")
            password_input = st.text_input("Password", type="password")
            
            # 1. ADD THIS: Let the user choose which role portal they want to access
            role_options = ["Dealer", "Supplier", "Admin", "Management Authority"]
            login_role = st.selectbox("Sign in as:", role_options)
            
            submit_signin = st.form_submit_button("Sign In")
            
            if submit_signin:
                # 2. ADD THIS: Map the dropdown choice to your DB's polymorphic identities
                role_identity = login_role.lower()
                if role_identity == "management authority":
                    role_identity = "management"
                    
                # 3. UPDATE THIS: Query by email, password, AND the selected role
                user = session.query(User).filter_by(
                    email=email_input, 
                    _password=password_input,
                    role=role_identity
                ).first()
                
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = user.role # Gets 'admin', 'dealer', etc.
                    st.session_state['user_id'] = user.user_id #
                    st.rerun() #
                else:
                    st.error("Invalid credentials or no account found for this specific role.") #

    # -- SIGN UP --
    with tab2:
        st.write("### Create a New Account")
        with st.form("signup_form"):
            new_email = st.text_input("Email Address")
            new_password = st.text_input("Create Password", type="password")
            
            role_options = ["Dealer", "Supplier", "Admin", "Management Authority"]
            new_role = st.selectbox("I want to register as a:", role_options)
            
            new_name = st.text_input("Full Name (Only required if registering as Admin)")
            submit_signup = st.form_submit_button("Sign Up")
            
            if submit_signup:
                if not new_email or not new_password:
                    st.error("Please fill out both the email and password fields.")
                elif new_role == "Admin" and not new_name:
                    st.error("Admins must provide a full name.")
                else:
                    success, message = register_user(new_email, new_password, new_role, new_name)
                    if success:
                        st.success(message)
                        st.info("Please switch to the 'Sign In' tab to access your portal.")
                        st.balloons()
                    else:
                        st.error(message)

# --- MAIN DASHBOARDS ---
else:
    # Sidebar
    st.sidebar.title(f"Logged in as: {st.session_state['user_role'].title()}")
    if st.sidebar.button("Sign Out"):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.session_state['user_id'] = None
        st.rerun()
    st.sidebar.divider()

    # Routing
    # Replace the routing section at the bottom of app.py with this:

    # Routing
    role = st.session_state['user_role'].lower()

    if role == "dealer":
        st.title("Dealer Portal")
        dealer_tabs = st.tabs(["🛒 Request Products", "📦 Update Stock (Sales)"])
        
        with dealer_tabs[0]:
            st.write("### Submit Product Request")
            products = fetchAvailableProducts()
            if products:
                # Create a simple form for product requests
                with st.form("product_request_form"):
                    prod_options = {p.product_name: p.product_id for p in products}
                    selected_prod_name = st.selectbox("Select Product", list(prod_options.keys()))
                    req_qty = st.number_input("Quantity Required", min_value=1, step=1) # [cite: 81]
                    
                    if st.form_submit_button("Submit Request"):
                        success, msg = submitRequest(st.session_state['user_id'], prod_options[selected_prod_name], req_qty)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg) # Handles the "Insufficient Stock" scenario [cite: 90]
            else:
                st.info("No products currently available in the system catalog.")

        with dealer_tabs[1]:
            st.write("### Record a Sale") # [cite: 100]
            with st.form("update_stock_form"):
                sold_product_id = st.number_input("Product ID", min_value=1, step=1) # [cite: 101]
                sold_qty = st.number_input("Quantity Sold", min_value=1, step=1) # [cite: 101]
                
                if st.form_submit_button("Confirm Sale"):
                    success, msg = updateStockAfterSale(sold_product_id, sold_qty)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    elif role == "admin":
        st.title("Production Manager Dashboard")
        st.write("### Pending Dealer Requests") # 
        
        from controllers import fetchPendingOrders, generateProductionBatch
        pending_orders = fetchPendingOrders()
        
        if pending_orders:
            for order in pending_orders:
                with st.expander(f"Order #{order.order_id} - Product ID: {order.product_id} (Qty: {order.quantity})"):
                    st.write(f"**Requested by Dealer ID:** {order.dealer_id}")
                    st.write(f"**Date:** {order.order_date}")
                    
                    if st.button("Assign Production Batch", key=f"btn_{order.order_id}"): # [cite: 151]
                        # In a full implementation, you'd check raw materials here first [cite: 152]
                        success, msg = generateProductionBatch(order.order_id, order.product_id, order.quantity)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("No dealer requests awaiting production.") # [cite: 155]
            
    # Replace the "elif role == 'supplier':" block in app.py

    elif role == "supplier":
        st.title("Supplier Portal")
        st.write("### Open Material Requests") # Supplier logs in and views open requests [cite: 135]
        
        from controllers import fetchOpenMaterialRequests, submitSupplierQuotation
        open_requests = fetchOpenMaterialRequests()
        
        if open_requests:
            for req in open_requests:
                with st.expander(f"Request #{req.request_id} - Material: {req.material_name} (Qty Required: {req.quantity})"):
                    with st.form(f"quote_form_{req.request_id}"):
                        st.write("Submit your quotation below:")
                        
                        # Supplier enters unit price and lead time [cite: 136]
                        unit_price = st.number_input("Unit Price ($)", min_value=0.00, step=0.50) 
                        lead_time = st.number_input("Lead Time (Days)", min_value=0, step=1)
                        
                        if st.form_submit_button("Submit Quotation"): # Supplier submits the quotation [cite: 137]
                            success, msg = submitSupplierQuotation(st.session_state['user_id'], req.request_id, unit_price, lead_time)
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
        else:
            st.info("There are currently no open material requests.")
        
    # Replace the "elif role == 'management':" block in app.py
    elif role == "management":
        st.title("Decision Support System (DSS)")
        st.write("### Inventory & Sales Trend Analysis")
        
        from controllers import generateStockAnalysis
        import pandas as pd
        
        if st.button("Generate Sales Trend Report"):
            sufficient_data, report_data = generateStockAnalysis()
            
            if report_data:
                df = pd.DataFrame(report_data)
                
                # Alternate Scenario: Insufficient Data
                if not sufficient_data:
                    st.warning("Not enough data to generate trend (less than 1 week of sales history).")
                    st.write("#### Flat Inventory Report")
                    # Show only basic inventory details without recommendations
                    st.dataframe(df[["Product ID", "Product Name", "Current Stock"]], use_container_width=True)
                
                # Main Scenario: Successful Analysis
                else:
                    st.success("Analysis generated successfully based on historical trends.")
                    
                    # Display the full recommendation table
                    st.write("#### Recommended Stock Update")
                    st.dataframe(df, use_container_width=True)
                    
                    st.divider()
                    
                    # Visual Analytics
                    st.write("#### Stock Deficit Analysis")
                    st.caption("Compares current stock levels against recommended restock quantities.")
                    
                    # Filter out products that don't need restocking for a cleaner chart
                    chart_df = df[df["Recommended Restock"] > 0]
                    if not chart_df.empty:
                        chart_data = chart_df.set_index("Product Name")[["Current Stock", "Recommended Restock"]]
                        st.bar_chart(chart_data, color=["#82b366", "#b85450"]) # Green for stock, Red for deficit
                    else:
                        st.info("Inventory levels are currently healthy across all products.")
                        
            else:
                st.info("No products available to analyze.")
                

# Temporary code to seed the cloud database


# Check if the database file exists yet
if not os.path.exists('wams.db'):
    seed_database()