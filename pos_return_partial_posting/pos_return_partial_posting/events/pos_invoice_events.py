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

def pos_invoice_validate(doc, method):
    # Validate that return invoices have zero payment amounts
    if doc.is_return == 1:
        # Check if paid_amount is zero
        if doc.paid_amount != 0:
            frappe.throw(_("Paid amount must be zero for return invoices"), title=_("Validation Error"))
        
        # Check if all payment rows have zero amounts
        if doc.payments:
            for idx, payment in enumerate(doc.payments, 1):
                if payment.amount != 0 or payment.base_amount != 0:
                    frappe.throw(
                        _("Payment amount at row {0} must be zero for return invoices").format(idx),
                        title=_("Validation Error")
                    )

