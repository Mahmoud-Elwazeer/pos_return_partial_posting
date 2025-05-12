import frappe
from frappe import _
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice


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
            frappe.logger("sales_invoice").info(
                f"Setting skip_gl_entries flag for {self.name} in custom_on_submit"
            )
        
        # Execute original on_submit but handle the GL entries part ourselves
        # First preserve the original make_gl_entries method
        original_invoice_make_gl_entries = self.make_gl_entries
        
        # Define a new make_gl_entries method that checks the flag
        def custom_make_gl_entries(*args, **kwargs):
            if hasattr(self, "flags") and getattr(self.flags, "skip_gl_entries", False):
                frappe.logger("sales_invoice").info(f"Skipping GL entries for {self.doctype} {self.name}")
                frappe.msgprint(_("GL Entry creation skipped as per configuration."))
                return None

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

