import frappe
from frappe import _

def pos_invoice_before_save(doc, method):
    # Check if this is a return invoice
    if doc.is_return == 1:

        doc.custom_enable_partial_posting_returns_only = 1

        # Set amount to zero for each payment row
        if doc.payments:
            for payment in doc.payments:
                payment.amount = 0
                payment.base_amount = 0
        
        # Set the paid amount to zero
        doc.paid_amount = 0

