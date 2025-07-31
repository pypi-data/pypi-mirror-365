from typing import Type
from pathlib import Path
from pyrfc import Connection
from lib_sap.purchase_order import po_getdetail

class OrderRsp:
    def __init__(self, uid, adress, message, business, subject, text, pdf):
        self.uid = uid
        self.adress = adress
        self.message = message
        self.business = business
        self.subject = subject
        self.text = text
        self.pdf = pdf
    
    def configure_kvpairs(self, kv_pairs: dict):
        """Configures key-value pairs for the order response."""
        self.kvpairs = kv_pairs

class Order:
    def __init__(self):
        self.po_number = None
    
    def configure_order(self, sapconn: Type[Connection], po_number: str):
        self.po_number = po_number
        po_details = po_getdetail(sapconn, po_number)
        kvpairs = self.parse_po_details(po_details)
    
    def parse_po_details(self, po_details: dict):
        """Parses purchase order details."""
        # Implement parsing logic here
        print("Parsing PO details:", po_details)
        pass

