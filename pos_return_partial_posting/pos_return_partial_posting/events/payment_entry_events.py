import frappe
from frappe import _
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry, get_payment_entry

def validate_partial_posting_return(self, method=None):
    """Validate if this payment entry is linked to a partial posting return invoice"""
    if self.reference_no == "Sales Invoice" and self.reference_name:
        # Check if this sales invoice was a partial posting return
        sales_invoice = frappe.get_doc("Sales Invoice", self.reference_name)
        if sales_invoice.is_return and hasattr(sales_invoice, 'custom_skip_gl_entries') and sales_invoice.custom_skip_gl_entries:
            # This is a partial posting return invoice payment
            frappe.msgprint(_("This payment will complete the accounting entries for return invoice {0}").format(
                sales_invoice.name))


def process_partial_posting_return_accounting(self, *args, **kwargs):
    """Create accounting entries for partial posting returns when payment is submitted"""
    sales_invoice = frappe.get_doc("Sales Invoice", self.reference_no)
    if sales_invoice.is_return and hasattr(sales_invoice, 'custom_skip_gl_entries') and sales_invoice.custom_skip_gl_entries:
        # Generate the accounting entries now
        from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
        # Create the GL entries based on the payment entry
        gl_entries = sales_invoice.get_gl_entries()

        frappe.db.set_value("Sales Invoice", sales_invoice.name, {
            "custom_skip_gl_entries": 0,
        })

        if gl_entries:
            sales_invoice.make_gl_entries(gl_entries)


        # Update the sales invoice status
        frappe.db.set_value("Sales Invoice", sales_invoice.name, {
            "custom_skip_gl_entries": 0,
            "status": "Return"
        })

        frappe.msgprint(_("Accounting entries created for return invoice {0}").format(
            sales_invoice.name))
