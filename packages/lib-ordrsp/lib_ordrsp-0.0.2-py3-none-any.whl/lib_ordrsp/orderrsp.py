

class OrderRsp:
    def __init__(self, uid, adress, message, business, subject, text, pdf):
        self.uid = uid
        self.adress = adress
        self.message = message
        self.business = business
        self.subject = subject
        self.text = text
        self.pdf = pdf

class Order:
    def __init__(self):
        self.po_number = None