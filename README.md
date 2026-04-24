# WAMS
Web-Based Automated Manufacturing System (WAMS)

## 📖 About the Project
[cite_start]The Web-Based Automated Manufacturing System (WAMS) is an end-to-end ERP solution designed for manufacturing companies[cite: 8]. [cite_start]It replaces manual ledger-keeping with an automated system that connects three distinct entities: the Manufacturing Company, Dealers, and Suppliers[cite: 27]. [cite_start]The primary goal of WAMS is to streamline workflow by managing orders, stock, and quotations through a centralized web platform[cite: 6]. 

[cite_start]It is designed to be a stand-alone product accessible via standard web browsers[cite: 27].

---

## ✨ Key Features
* [cite_start]**Dealer Management:** Manages dealer stock requests and ensures product availability[cite: 30].
* [cite_start]**Product & Inventory Tracking:** Continuously tracks and updates the levels of finished products in the warehouse[cite: 30].
* [cite_start]**Raw Material Procurement:** Generates requests for raw materials and parts when stock is running low[cite: 30].
* [cite_start]**Supplier Quotation Management:** Allows suppliers to log in and provide cost estimates and lead times for requested materials[cite: 30, 109].
* [cite_start]**Production Order Generation:** Converts active dealer requests into actionable production schedules while verifying raw material availability[cite: 30, 124, 125].
* [cite_start]**Automated Billing & Invoicing:** Automatically calculates taxes, generates PDF invoices for dealers, and records transactions[cite: 30, 137, 138, 139].
* [cite_start]**Decision Support System (DSS):** Predicts future inventory requirements based on past sales trends and generates recommended stock updates[cite: 30, 148, 149].
* [cite_start]**Role-Based Access Control:** Secure, role-specific dashboards for Admin, Dealers, and Suppliers, complete with account lockout features for failed authentications[cite: 30, 159, 164].

---

## 👥 User Roles
1.  [cite_start]**Admin / Production Manager:** Users familiar with manufacturing workflows who manage inventory, trigger production orders, and handle billing[cite: 32, 91, 121, 134].
2.  [cite_start]**Dealer:** A business entity that requests finished products and updates stock levels after completing sale transactions[cite: 16, 66, 72].
3.  [cite_start]**Supplier:** A vendor providing raw materials who reviews open material requests and submits quotations[cite: 17, 106, 108].

---

## 🖥️ User Interface
[cite_start]The web interface features a clean dashboard design, utilizing a navigation pane on the left and a dynamic data display area on the right[cite: 175].

---

## ⚙️ System Requirements & Constraints
* [cite_start]**Network:** Requires a continuous internet connection for real-time updates and a functioning web server/database environment[cite: 37, 40].
* [cite_start]**Performance:** Built to support at least 50 concurrent users without degradation, with 90% of web responses occurring within 2 seconds[cite: 169, 170].
* [cite_start]**Security:** Enforces password encryption and secures files against malicious deformation[cite: 172].
* [cite_start]**Data Integrity & Fault Tolerance:** Maintains strict database integrity to prevent stock-level discrepancies and prevents data corruption in case of a system crash[cite: 37, 173].
