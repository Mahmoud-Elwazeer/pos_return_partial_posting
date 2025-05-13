import frappe
from frappe.utils import cint, flt, get_time, getdate, nowdate, nowtime
from erpnext.accounts.doctype.pos_invoice_merge_log.pos_invoice_merge_log import POSInvoiceMergeLog

def override_pos_merge_on_submit():
    """
    Override the on_submit method of POSInvoiceMergeLog class
    """
    def custom_on_submit(self):
        pos_invoice_docs = [frappe.get_cached_doc("POS Invoice", d.pos_invoice) for d in self.pos_invoices]
        returns_partial_posting = [d for d in pos_invoice_docs if d.get("is_return") == 1 and d.get("custom_enable_partial_posting_returns_only") == 1]
        returns_normal = [d for d in pos_invoice_docs if d.get("is_return") == 1 and not d.get("custom_enable_partial_posting_returns_only")]
        sales = [d for d in pos_invoice_docs if d.get("is_return") == 0]

        sales_invoice, credit_note = "", ""
        sales_invoice_doc = None

        if sales:
            sales_invoice_doc = self.process_merging_into_sales_invoice(sales)
            sales_invoice = sales_invoice_doc.name

        if returns_normal:
            # Process normal returns with both stock and accounting entries
            credit_note = self.process_merging_into_credit_note(returns_normal, sales_invoice_doc)

        if returns_partial_posting:
            # Process returns with partial posting (stock only)
            credit_note = process_partial_posting_returns(self, returns_partial_posting, sales_invoice_doc)

        self.save()  # save consolidated_sales_invoice & consolidated_credit_note ref in merge log

        # Update all POS invoices with references
        self.update_pos_invoices(pos_invoice_docs, sales_invoice, credit_note)
    
    POSInvoiceMergeLog.on_submit = custom_on_submit

def process_partial_posting_returns(self, return_invoices, sales_invoice_doc=None):
        """
        Process return invoices with partial posting:
        1. Create sales invoice (return) with status "Return"
        2. Update stock ledger
        3. Skip accounting entries initially
        """
        # Create credit note but prevent GL entries
        credit_note = self.get_new_sales_invoice()
        credit_note.is_return = 1
        credit_note = self.merge_pos_invoice_into(credit_note, return_invoices)
        references = {}

        # Set reference to original sales invoice if available
        if sales_invoice_doc:
            credit_note.return_against = sales_invoice_doc.name
            
            for d in sales_invoice_doc.items:
                references[d.item_code] = d.name
                
            for d in credit_note.items:
                d.sales_invoice_item = references.get(d.item_code)


        credit_note.is_consolidated = 1
        credit_note.set_posting_time = 1
        credit_note.posting_date = getdate(self.posting_date)
        credit_note.posting_time = get_time(self.posting_time)

        # Add custom flag to prevent accounting entries during submission
        credit_note.custom_skip_gl_entries = 1

        # Save and submit the credit note
        credit_note.save()
        credit_note.submit()

        # Store the credit note reference
        self.consolidated_credit_note = credit_note.name
            
        return credit_note.name
