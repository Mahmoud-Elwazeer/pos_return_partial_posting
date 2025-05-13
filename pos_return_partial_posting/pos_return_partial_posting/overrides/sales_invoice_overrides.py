import frappe
from frappe import _
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
import json

def override_sales_invoice_on_submit():
    """
    Override the on_submit method of SalesInvoice class to intercept GL entries
    """
    # Store the original on_submit method
    original_on_submit = SalesInvoice.on_submit
    
    def custom_on_submit(self):
        """
        Custom on_submit that checks the skip_gl_entries flag before calling make_gl_entries
        """
        # Set flag if needed
        if self.is_return and self.get("custom_skip_gl_entries"):
            self.flags.skip_gl_entries = True

        # Execute original on_submit but handle the GL entries part ourselves
        # First preserve the original make_gl_entries method
        original_invoice_make_gl_entries = self.make_gl_entries
        
        # Define a new make_gl_entries method that checks the flag
        def custom_make_gl_entries(*args, **kwargs):
            if hasattr(self, "flags") and getattr(self.flags, "skip_gl_entries", False):
                frappe.msgprint(_("GL Entry creation skipped as per configuration."))
                gl_entries = self.get_gl_entries()
                frappe.msgprint(f"<pre>{json.dumps(gl_entries, indent=2, default=str)}</pre>")

                stock_accounts_keywords = ["Stock In Hand", "Cost of Goods Sold"]

                # Filter stock-related entries
                stock_gl_entries = [
                    entry for entry in gl_entries
                    if any(keyword in entry.get("account", "") for keyword in stock_accounts_keywords)
                ]
                # frappe.msgprint(f"<pre>{json.dumps(stock_gl_entries, indent=2, default=str)}</pre>")

                # Make only the stock-related GL entries
                from erpnext.accounts.general_ledger import make_gl_entries
                make_gl_entries(stock_gl_entries,  cancel=self.docstatus == 2, update_outstanding="Yes", merge_entries=False)
                return []

            return original_invoice_make_gl_entries(*args, **kwargs)
        
        # Replace the method temporarily
        self.make_gl_entries = custom_make_gl_entries
        # Call the original on_submit
        result = original_on_submit(self)
        
        # Restore the original method
        self.make_gl_entries = original_invoice_make_gl_entries
        
        return result
    
    # Replace the on_submit method
    SalesInvoice.on_submit = custom_on_submit
