"""
Enhanced mock data for Accounting Connector with comprehensive accounting data
"""

from typing import List, Dict, Any

class MockData:
    """Mock data generator for accounting data"""

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
                "columns": ["Ledger Name", "Parent", "Address", "State", "Pincode", "Country", "Contact no.", "Email"],
                "data": accounting_data.get('ledgers', []) if accounting_data.get('ledgers', []) else []
            },
            {
                "name": "Journal",
                "icon": "📒",
                "description": "Journal Vouchers",
                "columns": ["Journal No", "Date", "Party", "Nature", "Amount", "Narration"],
                "data": accounting_data.get('journal', []) if accounting_data.get('journal', []) else []
            }
        ]
        
    
    