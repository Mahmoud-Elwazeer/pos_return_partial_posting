# POS Return Partial Posting


## Getting Started

To get a local copy up and running, follow these steps.

### Prerequisites
- Python 3.x
- Frappe Framework
- MySQL or MariaDB

### Installation

1. **Set up Frappe Bench** (if you don't have one):
   ```bash
   bench init frappe-bench --frappe-branch version-15
   ```

2. **Get the App**:
   
   ```
   bench get-app pos_return_partial_posting https://github.com/Mahmoud-Elwazeer/pos_return_partial_posting.git
   ```
   
3. **Create a New Site** (if you don't have one):
   
   ```
   bench new-site <site_name>
   ```
   
4. **Run Migrate Command**:
   
   ```
   bench migrate
   ```
   
5. **Install the App**:
   
   ```
   bench --site <site_name> install-app pos_return_partial_posting
   ```
   
6. **Set the Site as Default**:
   
   ```
   bench use <site_name>
   ```
   
7. **( OR ) Add to hosts**

   ```
   bench --site <site_name> add-to-hosts
   ```

8. **Export Fixtures** 
   
   ```
   bench export-fixtures
   ```
   
9. **Run the App**:
   ```
   bench start
   ```


## 🧾 How to Use Partial Posting for Return POS Invoices

This feature allows you to process return POS invoices with **stock-only posting**, skipping accounting entries initially, and completing them later via manual payment entry.

### 🔁 Step-by-Step Guide

1. **Create a Return POS Invoice**
    - Go to the POS interface and create a return invoice as usual.
    - Open the return invoice in **Form View**.
2. **Enable Partial Posting**
    - Enable the checkbox labeled `Partial Posting (Stock Only)` (see screenshot for reference).
    - This ensures only stock entries are posted at first, without any GL (General Ledger) entries.
3. **Submit the Return POS Invoice**
    - Submit the invoice like any other.
    - When the **POS Closing Entry** is submitted, the system will merge the invoice and generate a corresponding **Sales Invoice** (of type Return).
4. **Check the Stock Update**
    - Go to **Stock Entry** to verify that stock quantities have been updated as per the return.
    - No accounting (GL) entries will be created at this point.
5. **Record Manual Payment**
    - Navigate to **Accounts > Payment Entry**.
    - Create a new Payment Entry manually:
        - Select the **Customer**.
        - In the reference table, link the previously generated **Sales Invoice**.
        - ⚠️ **Important**: In the *Reference No.* field, enter the number of the Sales Invoice to ensure it links correctly.
    - Submit the payment.
6. **Final Result**
    - After submitting the Payment Entry, the **General Ledger** will be updated.
    - At this point, both the **Sales Invoice** and **Payment Entry** are reflected properly in accounting.

## 📺 Video Tutorial

Watch a step-by-step video demonstration of how to use the Partial Posting feature:

👉 [Click here to watch on YouTube](https://www.youtube.com/watch?v=mvJCrA6vddo&t=8s)