"""
Enhanced mock data for Accounting Connector with comprehensive accounting data
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

class MockData:
    """Mock data generator for accounting data"""

    @staticmethod
    def get_tally_companies() -> List[str]:
        """Get mock Tally company list"""
        return [
            "ABC Enterprises Pvt. Ltd.",
            "XYZ Manufacturing Co.",
            "Sample Retail Store",
            "Test Corporation Ltd.",
            "Demo Trading Company"
        ]
    
    @staticmethod
    def get_busy_dsns() -> List[str]:
        """Get mock BUSY ODBC DSN list"""
        return [
            "BUSY_DB_01",
            "BUSY_ACCOUNTING",
            "BUSY_TEST_DB",
            "LOCAL_BUSY_DSN"
        ]
    
    @staticmethod
    def get_busy_companies() -> List[str]:
        """Get mock BUSY company list"""
        return [
            "Company A",
            "Company B",
            "Demo Company",
            "Test Organization"
        ]
    
    @staticmethod
    def get_accounting_data() -> List[Dict[str, Any]]:
        """Get accounting data tabs configuration"""
        return [
            {
                "name": "Ledgers",
                "icon": "📊",
                "description": "Chart of Accounts",
                "columns": ["Code", "Name", "Type", "Group", "Opening Balance", "Closing Balance", "Status"],
                "data": MockData.generate_ledgers_data(50)
            },
            {
                "name": "Stocks",
                "icon": "📦",
                "description": "Inventory Items",
                "columns": ["Item Code", "Item Name", "Unit", "Category", "Opening Qty", "Closing Qty", "Rate", "Value", "Godown"],
                "data": MockData.generate_stocks_data(40)
            },
            {
                "name": "Sales",
                "icon": "💰",
                "description": "Sales Vouchers",
                "columns": ["Voucher No", "Date", "Party", "Item", "Quantity", "Rate", "Amount", "Tax", "Total", "Status"],
                "data": MockData.generate_sales_data(60)
            },
            {
                "name": "Purchase",
                "icon": "🛒",
                "description": "Purchase Vouchers",
                "columns": ["Voucher No", "Date", "Supplier", "Item", "Quantity", "Rate", "Amount", "Tax", "Total", "Status"],
                "data": MockData.generate_purchase_data(50)
            },
            {
                "name": "Credit Note",
                "icon": "📝",
                "description": "Credit Notes",
                "columns": ["CN No", "Date", "Party", "Reference", "Amount", "Tax", "Total", "Reason", "Status"],
                "data": MockData.generate_credit_note_data(20)
            },
            {
                "name": "Debit Note",
                "icon": "📋",
                "description": "Debit Notes",
                "columns": ["DN No", "Date", "Party", "Reference", "Amount", "Tax", "Total", "Reason", "Status"],
                "data": MockData.generate_debit_note_data(15)
            },
            {
                "name": "Receipt",
                "icon": "💵",
                "description": "Receipt Vouchers",
                "columns": ["Receipt No", "Date", "Received From", "Amount", "Mode", "Bank", "Cheque No", "Narration", "Status"],
                "data": MockData.generate_receipt_data(30)
            },
            {
                "name": "Payment",
                "icon": "💳",
                "description": "Payment Vouchers",
                "columns": ["Payment No", "Date", "Paid To", "Amount", "Mode", "Bank", "Cheque No", "Narration", "Status"],
                "data": MockData.generate_payment_data(35)
            },
            {
                "name": "Journal",
                "icon": "📒",
                "description": "Journal Vouchers",
                "columns": ["Journal No", "Date", "Debit Account", "Credit Account", "Amount", "Narration", "Status"],
                "data": MockData.generate_journal_data(25)
            },
            {
                "name": "Contra",
                "icon": "🔄",
                "description": "Contra Vouchers",
                "columns": ["Contra No", "Date", "From Account", "To Account", "Amount", "Mode", "Narration", "Status"],
                "data": MockData.generate_contra_data(10)
            }
        ]
    
    def get_accounting_tabs(self, data=None) -> List[Dict[str, Any]]:
        """Get accounting data tabs configuration"""
        accounting_data = {}
        if data:
            accounting_data = data
        
        return [
            {
                "name": "Ledgers",
                "icon": "📊",
                "description": "Chart of Accounts",
                "columns": ["Ledger Name", "Parent", "Ledger Type", "Address", "State", "Pincode", "Country", "Gstin", "Opening Balance"],
                "data": accounting_data.get('ledgers', []) if accounting_data.get('ledgers', []) else []
            },
            {
                "name": "Stocks",
                "icon": "📦",
                "description": "Inventory Items",
                "columns": ["Stock Name", "Group", "Unit", "Gst Rate", "HSN", "Opening Qty", "Opening Rate", "Opening Amt"],
                "data": accounting_data.get('stocks', []) if accounting_data.get('stocks', []) else []
            },
            {
                "name": "Sales",
                "icon": "💰",
                "description": "Sales Vouchers",
                "columns": ["Voucher No", "Date", "Party", "Place Of Supply", "Taxable Amount", "Tax", "Total"],
                "data": accounting_data.get('sales', []) if accounting_data.get('sales', []) else []
            },
            {
                "name": "Purchase",
                "icon": "🛒",
                "description": "Purchase Vouchers",
                "columns": ["Voucher No", "Date", "Supplier Voucher No", "Supplier Voucher Date", "Supplier", "Place Of Supply", "Taxable Amount", "Tax", "Total"],
                "data": accounting_data.get('purchase', []) if accounting_data.get('purchase', []) else []
            },
            {
                "name": "Credit Note",
                "icon": "📝",
                "description": "Credit Notes",
                "columns": ["CN No", "Date", "Party", "Place Of Supply", "Taxable Amount", "Tax", "Total"],
                "data": accounting_data.get('credit_note', []) if accounting_data.get('credit_note', []) else []
            },
            {
                "name": "Debit Note",
                "icon": "📝",
                "description": "Debit Notes",
                "columns": ["DN No", "Date", "Party", "Place Of Supply", "Taxable Amount", "Tax", "Total"],
                "data": accounting_data.get('debit_note', []) if accounting_data.get('debit_note', []) else []
            },
            {
                "name": "Receipt",
                "icon": "💵",
                "description": "Receipt Vouchers",
                "columns": ["Receipt No", "Date", "Received From", "Amount", "Mode", "Bank", "Transaction Type", "Narration"],
                "data": accounting_data.get('receipt', []) if accounting_data.get('receipt', []) else []
            },
            {
                "name": "Payment",
                "icon": "💳",
                "description": "Payment Vouchers",
                "columns": ["Payment No", "Date", "Paid To", "Amount", "Mode", "Bank", "Transaction Type", "Narration"],
                "data": accounting_data.get('payment', []) if accounting_data.get('payment', []) else []
            },
            {
                "name": "Contra",
                "icon": "🔄",
                "description": "Contra Vouchers",
                "columns": ["Contra No", "Date", "From Account", "To Account", "Amount", "Mode", "Transaction Type", "Narration"],
                "data": accounting_data.get('contra', []) if accounting_data.get('contra', []) else []
            },
            {
                "name": "Journal",
                "icon": "📒",
                "description": "Journal Vouchers",
                "columns": ["Journal No", "Date", "Party", "Nature", "Amount", "Narration"],
                "data": accounting_data.get('journal', []) if accounting_data.get('journal', []) else []
            },
            {
                "name": "Sale Order",
                "icon": "📑",
                "description": "Sale Order Vouchers",
                "columns": ["Voucher No", "Date", "Party", "Place Of Supply", "Taxable Amount", "Tax", "Total"],
                "data": accounting_data.get('sale_order', []) if accounting_data.get('sale_order', []) else []
            },
            {
                "name": "Purchase Order",
                "icon": "🧾",
                "description": "Purchase Order Vouchers",
                "columns": ["Voucher No", "Date", "Party", "Place Of Supply", "Taxable Amount", "Tax", "Total"],
                "data": accounting_data.get('purchase_order', []) if accounting_data.get('purchase_order', []) else []
            },
            {
                "name": "Stock Journal",
                "icon": "🏭",
                "description": "Stock Journal",
                "columns": ["Voucher No", "Date", "Amount", "Narration"],
                "data": accounting_data.get('stock_journal', []) if accounting_data.get('stock_journal', []) else []
            },
            {
                "name": "Delivery Challan",
                "icon": "🚚",
                "description": "Delivery Challan Vouchers",
                "columns": ["Voucher No", "Date", "Party", "Place Of Supply", "Taxable Amount", "Tax", "Total"],
                "data": accounting_data.get('delivery_challan', []) if accounting_data.get('delivery_challan', []) else []
            },
        ]
        
    
    # Data generation methods
    @staticmethod
    def generate_ledgers_data(count: int = 50) -> List[List[Any]]:
        """Generate ledger data"""
        ledger_types = ["Asset", "Liability", "Income", "Expense"]
        groups = ["Cash-in-Hand", "Bank Accounts", "Sundry Debtors", "Sundry Creditors", 
                 "Capital Account", "Sales Accounts", "Purchase Accounts", "Direct Expenses", 
                 "Indirect Expenses", "Fixed Assets", "Loans"]
        statuses = ["Active", "Inactive"]
        
        data = []
        for i in range(1, count + 1):
            code = f"L{1000 + i}"
            name = f"Account {i}"
            ledger_type = random.choice(ledger_types)
            group = random.choice(groups)
            opening = random.uniform(1000, 1000000)
            closing = opening + random.uniform(-50000, 200000)
            status = random.choice(statuses)
            
            data.append([code, name, ledger_type, group, f"{opening:,.2f}", f"{closing:,.2f}", status])
        return data
    
    @staticmethod
    def generate_stocks_data(count: int = 40) -> List[List[Any]]:
        """Generate stock data"""
        categories = ["Electronics", "Furniture", "Stationery", "Raw Materials", "Finished Goods", "Consumables"]
        units = ["Nos", "Kg", "Meter", "Liter", "Box", "Packet"]
        godowns = ["Main Godown", "Warehouse A", "Warehouse B", "Store Room", "Production Area"]
        
        data = []
        for i in range(1, count + 1):
            item_code = f"ITM{1000 + i:04d}"
            item_name = f"Product {i}"
            unit = random.choice(units)
            category = random.choice(categories)
            opening_qty = random.randint(10, 1000)
            closing_qty = random.randint(0, opening_qty)
            rate = random.uniform(100, 50000)
            value = closing_qty * rate
            godown = random.choice(godowns)
            
            data.append([item_code, item_name, unit, category, opening_qty, closing_qty, 
                        f"{rate:,.2f}", f"{value:,.2f}", godown])
        return data
    
    @staticmethod
    def generate_sales_data(count: int = 60) -> List[List[Any]]:
        """Generate sales data"""
        parties = ["Customer A", "Customer B", "Customer C", "Customer D", "Customer E", 
                  "Retail Store", "Wholesaler", "Online Customer"]
        items = ["Laptop", "Mobile", "Tablet", "Monitor", "Keyboard", "Mouse", "Printer", "Scanner"]
        statuses = ["Paid", "Pending", "Partially Paid"]
        
        data = []
        for i in range(1, count + 1):
            voucher_no = f"SL{1000 + i}"
            date = (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
            party = random.choice(parties)
            item = random.choice(items)
            quantity = random.randint(1, 50)
            rate = random.uniform(1000, 50000)
            amount = quantity * rate
            tax = amount * 0.18  # 18% GST
            total = amount + tax
            status = random.choice(statuses)
            
            data.append([voucher_no, date, party, item, quantity, f"{rate:,.2f}", 
                        f"{amount:,.2f}", f"{tax:,.2f}", f"{total:,.2f}", status])
        return data
    
    @staticmethod
    def generate_purchase_data(count: int = 50) -> List[List[Any]]:
        """Generate purchase data"""
        suppliers = ["Supplier A", "Supplier B", "Supplier C", "Supplier D", "Supplier E"]
        items = ["Raw Material A", "Raw Material B", "Components", "Packaging", "Consumables"]
        statuses = ["Paid", "Pending", "Partially Paid"]
        
        data = []
        for i in range(1, count + 1):
            voucher_no = f"PR{1000 + i}"
            date = (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
            supplier = random.choice(suppliers)
            item = random.choice(items)
            quantity = random.randint(10, 500)
            rate = random.uniform(50, 5000)
            amount = quantity * rate
            tax = amount * 0.18
            total = amount + tax
            status = random.choice(statuses)
            
            data.append([voucher_no, date, supplier, item, quantity, f"{rate:,.2f}", 
                        f"{amount:,.2f}", f"{tax:,.2f}", f"{total:,.2f}", status])
        return data
    
    @staticmethod
    def generate_credit_note_data(count: int = 20) -> List[List[Any]]:
        """Generate credit note data"""
        parties = ["Customer A", "Customer B", "Customer C"]
        reasons = ["Returned Goods", "Damage", "Discount", "Wrong Billing", "Cancellation"]
        statuses = ["Approved", "Pending", "Rejected"]
        
        data = []
        for i in range(1, count + 1):
            cn_no = f"CN{1000 + i}"
            date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            party = random.choice(parties)
            reference = f"INV{random.randint(1000, 2000)}"
            amount = random.uniform(1000, 50000)
            tax = amount * 0.18
            total = amount + tax
            reason = random.choice(reasons)
            status = random.choice(statuses)
            
            data.append([cn_no, date, party, reference, f"{amount:,.2f}", 
                        f"{tax:,.2f}", f"{total:,.2f}", reason, status])
        return data
    
    @staticmethod
    def generate_debit_note_data(count: int = 15) -> List[List[Any]]:
        """Generate debit note data"""
        parties = ["Supplier A", "Supplier B", "Supplier C"]
        reasons = ["Short Delivery", "Quality Issue", "Price Discrepancy", "Additional Charges"]
        statuses = ["Approved", "Pending", "Rejected"]
        
        data = []
        for i in range(1, count + 1):
            dn_no = f"DN{1000 + i}"
            date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            party = random.choice(parties)
            reference = f"PO{random.randint(1000, 2000)}"
            amount = random.uniform(1000, 50000)
            tax = amount * 0.18
            total = amount + tax
            reason = random.choice(reasons)
            status = random.choice(statuses)
            
            data.append([dn_no, date, party, reference, f"{amount:,.2f}", 
                        f"{tax:,.2f}", f"{total:,.2f}", reason, status])
        return data
    
    @staticmethod
    def generate_receipt_data(count: int = 30) -> List[List[Any]]:
        """Generate receipt data"""
        parties = ["Customer A", "Customer B", "Customer C", "Customer D"]
        modes = ["Cash", "Cheque", "Bank Transfer", "UPI", "Credit Card"]
        banks = ["SBI", "HDFC", "ICICI", "Axis", "Kotak"]
        statuses = ["Cleared", "Pending", "Bounced"]
        
        data = []
        for i in range(1, count + 1):
            receipt_no = f"RC{1000 + i}"
            date = (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")
            party = random.choice(parties)
            amount = random.uniform(5000, 500000)
            mode = random.choice(modes)
            bank = random.choice(banks) if mode != "Cash" else "N/A"
            cheque_no = f"CHQ{random.randint(10000, 99999)}" if mode == "Cheque" else "N/A"
            narration = f"Payment against Invoice {random.randint(100, 999)}"
            status = random.choice(statuses)
            
            data.append([receipt_no, date, party, f"{amount:,.2f}", mode, 
                        bank, cheque_no, narration, status])
        return data
    
    @staticmethod
    def generate_payment_data(count: int = 35) -> List[List[Any]]:
        """Generate payment data"""
        parties = ["Supplier A", "Supplier B", "Supplier C", "Supplier D"]
        modes = ["Cash", "Cheque", "Bank Transfer", "UPI", "Credit Card"]
        banks = ["SBI", "HDFC", "ICICI", "Axis", "Kotak"]
        statuses = ["Cleared", "Pending", "Bounced"]
        
        data = []
        for i in range(1, count + 1):
            payment_no = f"PY{1000 + i}"
            date = (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")
            party = random.choice(parties)
            amount = random.uniform(5000, 500000)
            mode = random.choice(modes)
            bank = random.choice(banks) if mode != "Cash" else "N/A"
            cheque_no = f"CHQ{random.randint(10000, 99999)}" if mode == "Cheque" else "N/A"
            narration = f"Payment for Purchase Order {random.randint(100, 999)}"
            status = random.choice(statuses)
            
            data.append([payment_no, date, party, f"{amount:,.2f}", mode, 
                        bank, cheque_no, narration, status])
        return data
    
    @staticmethod
    def generate_journal_data(count: int = 25) -> List[List[Any]]:
        """Generate journal data"""
        debit_accounts = ["Cash Account", "Bank Account", "Purchase Account", "Expenses Account"]
        credit_accounts = ["Sales Account", "Income Account", "Capital Account", "Loan Account"]
        statuses = ["Posted", "Pending", "Reversed"]
        
        data = []
        for i in range(1, count + 1):
            journal_no = f"JV{1000 + i}"
            date = (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
            debit_acc = random.choice(debit_accounts)
            credit_acc = random.choice(credit_accounts)
            amount = random.uniform(1000, 100000)
            narration = f"Adjustment Entry {i}"
            status = random.choice(statuses)
            
            data.append([journal_no, date, debit_acc, credit_acc, 
                        f"{amount:,.2f}", narration, status])
        return data
    
    @staticmethod
    def generate_contra_data(count: int = 10) -> List[List[Any]]:
        """Generate contra data"""
        from_accounts = ["Cash Account", "Bank Account A", "Bank Account B"]
        to_accounts = ["Bank Account A", "Bank Account B", "Cash Account"]
        modes = ["Cash", "Cheque", "Transfer"]
        statuses = ["Completed", "Pending", "Failed"]
        
        data = []
        for i in range(1, count + 1):
            contra_no = f"CT{1000 + i}"
            date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            from_acc = random.choice(from_accounts)
            to_acc = random.choice(to_accounts)
            amount = random.uniform(5000, 50000)
            mode = random.choice(modes)
            narration = f"Fund Transfer {i}"
            status = random.choice(statuses)
            
            data.append([contra_no, date, from_acc, to_acc, 
                        f"{amount:,.2f}", mode, narration, status])
        return data
    