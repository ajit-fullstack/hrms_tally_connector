"""
Application controller for Accounting Connector
"""

import requests, json, asyncio, httpx, logging, re
from utils.tdl import *
from utils.drop_down import *
from utils.utils import Utils
import xml.etree.ElementTree as ET
from datetime import date, datetime
from typing import List, Optional
from PySide6.QtCore import QObject, Signal, QTimer

from src.models import (
    ConnectorStatus, LogLevel, LogEntry,
    TallyConfig, BusyConfig
)

class MainController(QObject):
    """Main application controller"""
    
    # Signals for UI updates
    log_updated = Signal(LogEntry)
    tally_status_changed = Signal(ConnectorStatus)
    busy_status_changed = Signal(ConnectorStatus)
    
    def __init__(self):
        super().__init__()
        
        # Initialize configurations
        self.tally_config = TallyConfig()
        self.busy_config = BusyConfig()
        
        # Initialize status
        self.tally_status = ConnectorStatus.DISCONNECTED
        self.busy_status = ConnectorStatus.DISCONNECTED
        
        # Initialize logs
        self.logs: List[LogEntry] = []
        
        # Mock last sync time
        self.last_sync_time = datetime.now()
        
        # Add initial log
        self._add_log(LogLevel.INFO, "Application started", "System")

        # Manually added
        self.url = ""
        # self.exported_data = dict()
    
    def _add_log(self, level: LogLevel, message: str, source: str):
        """Add a log entry and emit signal"""
        entry = LogEntry(datetime.now(), level, message, source)
        self.logs.append(entry)
        self.log_updated.emit(entry)
    
    # Tally Connector Methods
    def connect_tally(self, host: str, port: int, user_name: str, password: str) -> bool:
        """Mock Tally connection"""
        self.tally_status = ConnectorStatus.PENDING
        self.tally_status_changed.emit(self.tally_status)
        
        self.url = f"http://{host}:{port}"
        login_url = "http://127.0.0.1:8000/login"

        self._add_log(LogLevel.INFO, f"Attempting to connect to Tally at {host}:{port}", "Tally")
        self._add_log(LogLevel.INFO, f"Attempting to api at {login_url}", "Startup khata")

        try:
            response = requests.post(
                login_url,
                data={   # ✅ OAuth2 form data
                    "username": user_name,
                    "password": password,
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()

                # save token if returned
                self.access_token = result.get("access_token")

                self._add_log(LogLevel.INFO, "Login successful", "Startup khata")
                QTimer.singleShot(1000, self._tally_connection)
                return True
            else:
                self._add_log(LogLevel.ERROR, f"Login failed: {response.text}", "Tally")
                self.tally_status = ConnectorStatus.ERROR
                self.tally_status_changed.emit(self.tally_status)
                return False

        except Exception as e:
            self._add_log(LogLevel.ERROR, f"Connection error: {str(e)}", "Tally")
            self.tally_status = ConnectorStatus.ERROR
            self.tally_status_changed.emit(self.tally_status)
            return False
    
    def _tally_connection(self):
        """Simulate Tally connection result"""
        try:
            success = self.get_tally_companies()
            
            if success:
                self.tally_status = ConnectorStatus.CONNECTED
                self._add_log(LogLevel.SUCCESS, "Tally connection successful", "Tally")
            else:
                self.tally_status = ConnectorStatus.ERROR
                self._add_log(LogLevel.ERROR, "Tally connection failed", "Tally")
            
            self.tally_status_changed.emit(self.tally_status)

            # return success
        except Exception as e:
            self.tally_status = ConnectorStatus.ERROR
            self.tally_status_changed.emit(self.tally_status)
            self._add_log(LogLevel.ERROR, "Tally connection failed", "Tally")

            raise Exception(str(e))
    
    def disconnect_tally(self):
        """Disconnect Tally"""
        self.tally_status = ConnectorStatus.DISCONNECTED
        self.tally_status_changed.emit(self.tally_status)
        self._add_log(LogLevel.INFO, "Tally disconnected", "Tally")
    
    # async def export_tally_data(self, config: TallyConfig) -> bool:
    #     """Mock Tally data export"""
    #     self._add_log(LogLevel.INFO, "Starting Tally data export...", "Tally")
        
    #     self.url = f"http://{config.host}:{config.port}"

    #     final_data = {}
    #     if "Ledgers" in config.selected_data_types:
    #         ledgers = await self.get_tally_ledgers(config.date_from)
    #         final_data.update({ "ledgers": ledgers })
    #     if "Stocks" in config.selected_data_types:
    #         stocks = await self.get_tally_stocks(config.date_from)
    #         final_data.update({ "stocks": stocks })
    #     if "Sales" in config.selected_data_types:
    #         sales = await self.get_tally_sales(config.date_from, config.date_to)
    #         final_data.update({ "sales": sales })
    #     if "Purchase" in config.selected_data_types:
    #         purchase = await self.get_tally_purchase(config.date_from, config.date_to)
    #         final_data.update({ "purchase": purchase })
    #     if "Credit Note" in config.selected_data_types:
    #         credit_note = await self.get_tally_creditNote(config.date_from, config.date_to)
    #         final_data.update({ "credit_note": credit_note })
    #     if "Debit Note" in config.selected_data_types:
    #         debit_note = await self.get_tally_debitNote(config.date_from, config.date_to)
    #         final_data.update({ "debit_note": debit_note })
    #     if "Sale Order" in config.selected_data_types:
    #         sale_order = await self.get_sales_order(config.date_from, config.date_to)
    #         final_data.update({ "sale_order": sale_order })
    #     if "Purchase Order" in config.selected_data_types:
    #         purchase_order = await self.get_purchase_order(config.date_from, config.date_to)
    #         final_data.update({ "purchase_order": purchase_order })
    #     if "Delivery Challan" in config.selected_data_types:
    #         delivery_challan = await self.get_delivery_challan(config.date_from, config.date_to)
    #         final_data.update({ "delivery_challan": delivery_challan })
    #     if "Receipt" in config.selected_data_types:
    #         receipt = await self.get_tally_receipt(config.date_from, config.date_to)
    #         final_data.update({ "receipt": receipt })
    #     if "Payment" in config.selected_data_types:
    #         payment = await self.get_tally_payment(config.date_from, config.date_to)
    #         final_data.update({ "payment": payment })
    #     if "Journal" in config.selected_data_types:
    #         journal = await self.get_tally_journal(config.date_from, config.date_to)
    #         final_data.update({ "journal": journal })
    #     if "Stock Journal" in config.selected_data_types:
    #         stock_journal = await self.get_stock_jurnal(config.date_from, config.date_to)
    #         final_data.update({ "stock_journal": stock_journal })
     
    #     QTimer.singleShot(7000, lambda: self._complete_export("Tally"))
    #     return final_data
    
    async def export_tally_data(self, config: TallyConfig) -> dict:
        """Parallel Tally data export"""

        self._add_log(LogLevel.INFO, "Starting Tally data export...", "Tally")

        self.url = f"http://{config.host}:{config.port}"

        tasks = []
        task_keys = []

        try:
            if "Ledgers" in config.selected_data_types:
                tasks.append(self.get_tally_ledgers(config.date_from))
                task_keys.append("ledgers")

            if "Stocks" in config.selected_data_types:
                tasks.append(self.get_tally_stocks(config.date_from))
                task_keys.append("stocks")

            if "Sales" in config.selected_data_types:
                tasks.append(
                    self.get_tally_sales(config.date_from, config.date_to)
                )
                task_keys.append("sales")

            if "Purchase" in config.selected_data_types:
                tasks.append(
                    self.get_tally_purchase(config.date_from, config.date_to)
                )
                task_keys.append("purchase")

            if "Credit Note" in config.selected_data_types:
                tasks.append(
                    self.get_tally_creditNote(config.date_from, config.date_to)
                )
                task_keys.append("credit_note")

            if "Debit Note" in config.selected_data_types:
                tasks.append(
                    self.get_tally_debitNote(config.date_from, config.date_to)
                )
                task_keys.append("debit_note")

            if "Sale Order" in config.selected_data_types:
                tasks.append(
                    self.get_sales_order(config.date_from, config.date_to)
                )
                task_keys.append("sale_order")

            if "Purchase Order" in config.selected_data_types:
                tasks.append(
                    self.get_purchase_order(config.date_from, config.date_to)
                )
                task_keys.append("purchase_order")

            if "Delivery Challan" in config.selected_data_types:
                tasks.append(
                    self.get_delivery_challan(config.date_from, config.date_to)
                )
                task_keys.append("delivery_challan")

            if "Receipt" in config.selected_data_types:
                tasks.append(
                    self.get_tally_receipt(config.date_from, config.date_to)
                )
                task_keys.append("receipt")

            if "Payment" in config.selected_data_types:
                tasks.append(
                    self.get_tally_payment(config.date_from, config.date_to)
                )
                task_keys.append("payment")

            if "Journal" in config.selected_data_types:
                tasks.append(
                    self.get_tally_journal(config.date_from, config.date_to)
                )
                task_keys.append("journal")

            if "Stock Journal" in config.selected_data_types:
                tasks.append(
                    self.get_stock_jurnal(config.date_from, config.date_to)
                )
                task_keys.append("stock_journal")

            # ✅ PARALLEL EXECUTION
            results = await asyncio.gather(*tasks, return_exceptions=True)

            final_data = {}

            for key, result in zip(task_keys, results):
                if isinstance(result, Exception):
                    # logging.exception(result)
                    raise Exception(result)

                final_data[key] = result

            QTimer.singleShot(7000, lambda: self._complete_export("Tally"))

            return final_data

        except Exception as e:
            # logging.exception(e)
            raise Exception(e)

    # Export Data Form Tally
    def get_tally_companies(self):
        request = requests.post(self.url, data=company_details_xml)
        response = request.text

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        list_of_companies = []
        for company in root.findall(".//COMPANY"):
            address = ", ".join(
                a.text for a in company.findall("ADDRESS") if a.text
            )

            list_of_companies.append(company.findtext("NAME"))
            
            print({
                "name": company.findtext("NAME"),
                "state": company.findtext("STATENAME"),
                "country": company.findtext("COUNTRYNAME"),
                "gstin": company.findtext("GSTIN"),
                "address": address
            })
            
        return list_of_companies

    async def get_tally_ledgers(self, start_date):
        request = requests.post(self.url, data=ledger_tdl)
        response = request.text

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        formated_json = []
        for ledger in root.findall(".//LEDGER"):
            temp_dict = {}

            # Ledger name
            for lang in ledger.findall(".//LANGUAGENAME.LIST"):
                for child in lang.findall(".//NAME.LIST/NAME"):
                    temp_dict["ledger_name"] = child.text
                
            if not temp_dict.get("ledger_name"):
                continue

            temp_dict["parent"] = (ledger.findtext("PARENT") or "")
            temp_dict["tax_type"] = (ledger.findtext("TAXTYPE") or "")

            # address
            address = ""
            for addr in ledger.findall(".//ADDRESS.LIST/ADDRESS"):
                if address:
                    address += " "
                address += addr.text
            
            temp_dict["address"] = address

            temp_dict["state"] = (ledger.findtext("PRIORSTATENAME") or "")
            temp_dict["pincode"] = (ledger.findtext("PINCODE") or "")
            temp_dict["country"] = (ledger.findtext("COUNTRYNAME") or "")
            temp_dict["gstin"] = ""
            temp_dict["open_bal"] = ledger.findtext("OPENINGBALANCE")
            temp_dict["open_bal"] = ledger.findtext("OPENINGBALANCE")
            temp_dict["open_date"] = start_date

            # for child in ledger:
            #   print(child.tag, child.text)

            formated_json.append(temp_dict)

        return formated_json

    async def get_tally_stocks(self, start_date):
        request = requests.post(self.url, data=stocks_tdl)
        response = request.text

        # print("response", response)

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        formated_json = []
        for item in root.findall(".//STOCKITEM"):
            temp_dict = {}

            for lang in item.findall(".//LANGUAGENAME.LIST"):
                for child in lang.findall(".//NAME.LIST/NAME"):
                    temp_dict["inventory_name"] = child.text
            
            if not temp_dict.get('inventory_name'):
                continue
            
            temp_dict["parent"] = item.findtext("PARENT")
            temp_dict["base_unit"] = item.findtext("BASEUNITS")
            
            gst_rates = 0
            for rate in item.findall(".//GSTDETAILS.LIST/STATEWISEDETAILS.LIST/RATEDETAILS.LIST"):
                duty = rate.findtext("GSTRATEDUTYHEAD")
                value = rate.findtext("GSTRATE")

                if not duty or not value:
                    continue

                duty = duty.upper()

                if duty == "CGST":
                    gst_rates += float(value)
                elif duty in ("SGST/UTGST", "UTGST"):
                    gst_rates += float(value)
                elif duty == "IGST":
                    gst_rates = float(value)
                # elif duty == "CESS":
                #   gst_rates["CESS"] = float(value)

            temp_dict["gst_rates"] = gst_rates
            temp_dict["hsn"] = ""
            temp_dict["opening_qty"] = float(item.findtext("OPENINGBALANCE")[:-4] or 0)
            temp_dict["opening_rate"] = float(item.findtext("OPENINGRATE")[:-4] or 0)
            temp_dict["opening_amt"] = abs(float(item.findtext("OPENINGVALUE")) or 0)
            temp_dict["category"] = item.findtext("GSTTYPEOFSUPPLY")
            temp_dict["opening_date"] = start_date

            formated_json.append(temp_dict)

        # print(formated_json)
        return formated_json

    def get_gst_rate(self, voucher, sales):
        gst_rate = 0
        tax_type = ""

        check = "No" if sales else "Yes"
        for item in voucher.findall(".//LEDGERENTRIES.LIST"):
            if item.findtext("ISDEEMEDPOSITIVE") == check:
                ledger = item.findtext("LEDGERNAME")
                match = re.search(r'(.+?)\s*@?\s*(\d+(?:\.\d+)?)\s*%', ledger)
                if match:
                    tax_type = match.group(1).strip()
                    if tax_type == "IGST":
                        gst_rate = float(match.group(2))
                    else:
                        gst_rate += float(match.group(2))
        return gst_rate, tax_type

    async def get_tally_sales(self, start_date, end_date):
        from_date = start_date.strftime("%d-%b-%Y")
        to_date   = end_date.strftime("%d-%b-%Y")

        xml_request  = sales_tdl.format(from_date=from_date, to_date=to_date)
        request = requests.post(self.url, data=xml_request)
        response = request.text

        # print("response", response)

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        # Sales
        invoices = []
        for voucher in root.findall(".//VOUCHER"):
            temp_dict = {}

            if not voucher.findtext("VOUCHERNUMBER"):
                continue

            temp_dict["invoice_no"] = voucher.findtext("VOUCHERNUMBER")
            invoice_date = voucher.findtext("DATE")
            temp_dict["invoice_date"] = datetime.strptime(invoice_date, "%Y%m%d").strftime("%d-%m-%Y")
            temp_dict["customer_name"] = voucher.findtext("PARTYLEDGERNAME")
            temp_dict["placeOfSupply"] = voucher.findtext("PLACEOFSUPPLY")

            items = []
            for item in voucher.findall(".//ALLINVENTORYENTRIES.LIST"):
                temp_item = {}
                temp_item["item_name"] = item.findtext("STOCKITEMNAME")
                temp_item["category"] = "Inventory"

                uml = item.findtext("BILLEDQTY")[-3:]
                uml = uml.lower()
                uml = measurement[uml]
                temp_item["uml"] = uml

                temp_item["qty"] = float(item.findtext("BILLEDQTY")[:-4] or 0)
                temp_item["rate"] = float(item.findtext("RATE")[:-4] or 0)
                temp_item["taxable_value"] = abs(float(item.findtext("AMOUNT") or 0))

                if float(item.findtext("DISCOUNT") or 0):
                    temp_item["discount_type"] = "%"
                    temp_item["discount"] = float(item.findtext("DISCOUNT") or 0)

                gst_rate, tax_type = self.get_gst_rate(voucher, True)
                
                temp_item["gst_rate"] = gst_rate
                if tax_type == "IGST":
                    temp_item["igst"] = round((temp_item["taxable_value"] * gst_rate) / 100, 2)
                else:
                    temp_item["cgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)
                    temp_item["sgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)

                temp_item["invoice_value"] = round((temp_item["taxable_value"] or 0) + (temp_item.get("igst") or 0) + (temp_item.get("cgst") or 0) + (temp_item.get("sgst") or 0), 2)
                items.append(temp_item)

            temp_dict["items"] = items
            invoices.append(temp_dict)

        # print("invoices", invoices)
        return invoices

    async def get_tally_purchase(self, start_date, end_date):
        from_date = start_date.strftime("%d-%b-%Y")
        to_date   = end_date.strftime("%d-%b-%Y")
        
        xml_request  = purchase_tdl.format(from_date=from_date, to_date=to_date)
        request = requests.post(self.url, data=xml_request)
        response = request.text

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        # Purchase
        vouchers = []
        for voucher in root.findall(".//VOUCHER"):
            temp_dict = {}

            if not voucher.findtext("VOUCHERNUMBER"):
                continue
            
            temp_dict["voucher_no"] = voucher.findtext("VOUCHERNUMBER")
            invoice_date = voucher.findtext("DATE")
            temp_dict["invoice_date"] = datetime.strptime(invoice_date, "%Y%m%d").strftime("%d-%m-%Y")
            temp_dict["supplier_voucher_no"] = voucher.findtext("REFERENCE")
            supplier_voucher_date = voucher.findtext("REFERENCEDATE")
            temp_dict["supplier_voucher_date"] = datetime.strptime(supplier_voucher_date, "%Y%m%d").strftime("%d-%m-%Y")
            # temp_dict["supplier_voucher_date"] = voucher.findtext("REFERENCEDATE")
            temp_dict["party_name"] = voucher.findtext("PARTYLEDGERNAME")

            # placeOfSupply = voucher.findtext("PLACEOFSUPPLY")
            # placeOfSupply = tally_mapping_state[placeOfSupply]
            # temp_dict["placeOfSupply"] = placeOfSupply.get('id')
            temp_dict["placeOfSupply"] = voucher.findtext("PLACEOFSUPPLY")

            items = []
            for item in voucher.findall(".//ALLINVENTORYENTRIES.LIST"):
                temp_item = {}
                temp_item["item_name"] = item.findtext("STOCKITEMNAME")
                temp_item["category"] = "Inventory"

                uml = item.findtext("BILLEDQTY")[-3:]
                uml = uml.lower()
                uml = measurement[uml]
                temp_item["uml"] = uml
                
                temp_item["qty"] = float(item.findtext("BILLEDQTY")[:-4] or 0)
                temp_item["rate"] = float(item.findtext("RATE")[:-4] or 0)
                temp_item["taxable_value"] = abs(float(item.findtext("AMOUNT") or 0))

                if float(item.findtext("DISCOUNT") or 0):
                    temp_item["discount_type"] = "%"
                    temp_item["discount"] = float(item.findtext("DISCOUNT") or 0)
                
                gst_rate = 0
                tax_type = ""
                for rate_item in item.findall("RATEDETAILS.LIST"):
                    tax_type = rate_item.findtext("GSTRATEDUTYHEAD")
                    if tax_type in ["CGST", "SGST/UTGST", "SGST"]:
                        gst_rate += float(rate_item.findtext("GSTRATE"))
                    elif tax_type == "IGST":
                        gst_rate = float(rate_item.findtext("GSTRATE"))

                temp_item["gst_rate"] = gst_rate
                if tax_type == "IGST":
                    temp_item["igst"] = round((temp_item["taxable_value"] * gst_rate) / 100, 2)
                else:
                    temp_item["cgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)
                    temp_item["sgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)

                temp_item["invoice_value"] = (temp_item["taxable_value"] or 0) + (temp_item.get("igst") or 0) + (temp_item.get("cgst") or 0) + (temp_item.get("sgst") or 0)

                items.append(temp_item)
            
            temp_dict["items"] = items
            vouchers.append(temp_dict)

        # print("vouchers", vouchers)
        return vouchers

    async def get_tally_receipt(self, start_date, end_date):
        from_date = start_date.strftime("%d-%b-%Y")
        to_date   = end_date.strftime("%d-%b-%Y")

        xml_request  = receipt_tdl.format(from_date=from_date, to_date=to_date)
        request = requests.post(self.url, data=xml_request)
        response = request.text

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        # Sales
        invoices = []
        for voucher in root.findall(".//VOUCHER"):
            temp_dict = {}

            if not voucher.findtext("VOUCHERNUMBER"):
                continue

            temp_dict["invoice_no"] = voucher.findtext("VOUCHERNUMBER")
            invoice_date = voucher.findtext("DATE")
            temp_dict["invoice_date"] = datetime.strptime(invoice_date, "%Y%m%d").strftime("%d-%m-%Y")
            temp_dict["customer_name"] = voucher.findtext("PARTYLEDGERNAME")
            
            amount = 0 
            bank_name =""
            transaction_type = ""
            for item in voucher.findall(".//ALLLEDGERENTRIES.LIST"):
                ledger_name = item.findtext("LEDGERNAME")
                if ledger_name != temp_dict.get('customer_name'):
                    bank_name = item.findtext("LEDGERNAME")

                for sub_item in item.findall(".//BANKALLOCATIONS.LIST"):
                    transaction_type = sub_item.findtext("TRANSACTIONTYPE")
                
                amount = abs(float(item.findtext("AMOUNT") or 0)) 

            tally_transaction_type_map = {
                "ATM": "Others", 
                "Card": "Others", 
                "Cash": "Cash/Deposit", 
                "Cheque/DD": "Cheque/DDNo", 
                "ECS": "Others", 
                "e-Fund Transfer": "Others", 
                "Electronic Cheque": "Others", 
                "Electronic DD/PO": "Others", 
                "UPI": "Others", 
                "Others": "Others"
            }

            temp_dict["amount"] = amount
            temp_dict["mode"] = "On Account"
            temp_dict["bank_name"] = bank_name
            temp_dict["transaction_type"] = tally_transaction_type_map[transaction_type]
            temp_dict["narration"] = voucher.findtext("NARRATION")

            temp_dict["items"] = []
            invoices.append(temp_dict)

        # print("invoices", invoices)
        return invoices

    async def get_tally_payment(self, start_date, end_date):
        from_date = start_date.strftime("%d-%b-%Y")
        to_date   = end_date.strftime("%d-%b-%Y")

        xml_request  = payment_tdl.format(from_date=from_date, to_date=to_date)
        request = requests.post(self.url, data=xml_request)
        response = request.text

        # print("response", response)

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        # Sales
        invoices = []
        for voucher in root.findall(".//VOUCHER"):
            temp_dict = {}

            if not voucher.findtext("VOUCHERNUMBER"):
                continue

            temp_dict["invoice_no"] = voucher.findtext("VOUCHERNUMBER")
            invoice_date = voucher.findtext("DATE")
            temp_dict["invoice_date"] = datetime.strptime(invoice_date, "%Y%m%d").strftime("%d-%m-%Y")
            temp_dict["customer_name"] = voucher.findtext("PARTYLEDGERNAME")

            amount = 0 
            bank_name =""
            transaction_type = ""
            for item in voucher.findall(".//ALLLEDGERENTRIES.LIST"):
                ledger_name = item.findtext("LEDGERNAME")
                if ledger_name != temp_dict.get('customer_name'):
                    bank_name = item.findtext("LEDGERNAME")

                for sub_item in item.findall(".//BANKALLOCATIONS.LIST"):
                    transaction_type = sub_item.findtext("TRANSACTIONTYPE")
                
                amount = abs(float(item.findtext("AMOUNT") or 0)) 

            tally_transaction_type_map = {
                "ATM": "Others", 
                "Card": "Others", 
                # "Cash": "Cash/Deposit", 
                "Cheque": "Cheque/DDNo", 
                "ECS": "Others", 
                "e-Fund Transfer": "Others", 
                "Electronic Cheque": "Others", 
                "Electronic DD/PO": "Others", 
                "UPI": "Others", 
                "Others": "Others"
            }

            temp_dict["amount"] = amount
            temp_dict["mode"] = "On Account"
            temp_dict["bank_name"] = bank_name
            temp_dict["transaction_type"] = tally_transaction_type_map[transaction_type]
            temp_dict["narration"] = voucher.findtext("NARRATION")

            temp_dict["items"] = []
            invoices.append(temp_dict)

        # print("invoices", invoices)
        return invoices

    async def get_tally_debitNote(self, start_date, end_date):
        from_date = start_date.strftime("%d-%b-%Y")
        to_date   = end_date.strftime("%d-%b-%Y")

        xml_request  = debitNote_tdl.format(from_date=from_date, to_date=to_date)
        request = requests.post(self.url, data=xml_request)
        response = request.text

        # print("response", response)

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        # Sales
        invoices = []
        for voucher in root.findall(".//VOUCHER"):
            temp_dict = {}

            if not voucher.findtext("VOUCHERNUMBER"):
                continue

            temp_dict["invoice_no"] = voucher.findtext("VOUCHERNUMBER")
            invoice_date = voucher.findtext("DATE")
            temp_dict["invoice_date"] = datetime.strptime(invoice_date, "%Y%m%d").strftime("%d-%m-%Y")
            temp_dict["customer_name"] = voucher.findtext("PARTYLEDGERNAME")
            temp_dict["placeOfSupply"] = voucher.findtext("PLACEOFSUPPLY")

            items = []
            for item in voucher.findall(".//ALLINVENTORYENTRIES.LIST"):
                temp_item = {}
                temp_item["item_name"] = item.findtext("STOCKITEMNAME")
                temp_item["category"] = "Inventory"

                uml = item.findtext("BILLEDQTY")[-3:]
                uml = uml.lower()
                uml = measurement[uml]
                temp_item["uml"] = uml

                temp_item["qty"] = float(item.findtext("BILLEDQTY")[:-4] or 0)
                temp_item["rate"] = float(item.findtext("RATE")[:-4] or 0)
                temp_item["taxable_value"] = abs(float(item.findtext("AMOUNT") or 0))

                if float(item.findtext("DISCOUNT") or 0):
                    temp_item["discount_type"] = "%"
                    temp_item["discount"] = float(item.findtext("DISCOUNT") or 0)

                gst_rate = 0
                tax_type = ""
                for rate_item in item.findall("RATEDETAILS.LIST"):
                    tax_type = rate_item.findtext("GSTRATEDUTYHEAD")
                    if tax_type in ["CGST", "SGST/UTGST", "SGST"]:
                        gst_rate += float(rate_item.findtext("GSTRATE"))
                    elif tax_type == "IGST":
                        gst_rate = float(rate_item.findtext("GSTRATE"))

                temp_item["gst_rate"] = gst_rate
                if tax_type == "IGST":
                    temp_item["igst"] = round((temp_item["taxable_value"] * gst_rate) / 100, 2)
                else:
                    temp_item["cgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)
                    temp_item["sgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)

                temp_item["invoice_value"] = (temp_item["taxable_value"] or 0) + (temp_item.get("igst") or 0) + (temp_item.get("cgst") or 0) + (temp_item.get("sgst") or 0)

                items.append(temp_item)

            temp_dict["items"] = items
            invoices.append(temp_dict)

        # print("invoices", invoices)
        return invoices

    async def get_tally_creditNote(self, start_date, end_date):
        from_date = start_date.strftime("%d-%b-%Y")
        to_date   = end_date.strftime("%d-%b-%Y")

        xml_request  = creditNote_tdl.format(from_date=from_date, to_date=to_date)
        request = requests.post(self.url, data=xml_request)
        response = request.text

        # print(response)

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        # Sales
        invoices = []
        for voucher in root.findall(".//VOUCHER"):
            temp_dict = {}

            if not voucher.findtext("VOUCHERNUMBER"):
                continue

            temp_dict["invoice_no"] = voucher.findtext("VOUCHERNUMBER")
            invoice_date = voucher.findtext("DATE")
            temp_dict["invoice_date"] = datetime.strptime(invoice_date, "%Y%m%d").strftime("%d-%m-%Y")
            temp_dict["customer_name"] = voucher.findtext("PARTYLEDGERNAME")
            temp_dict["placeOfSupply"] = voucher.findtext("PLACEOFSUPPLY")

            items = []
            for item in voucher.findall(".//ALLINVENTORYENTRIES.LIST"):
                temp_item = {}
                temp_item["item_name"] = item.findtext("STOCKITEMNAME")
                temp_item["category"] = "Inventory"

                uml = item.findtext("BILLEDQTY")[-3:]
                uml = uml.lower()
                uml = measurement[uml]
                temp_item["uml"] = uml

                temp_item["qty"] = float(item.findtext("BILLEDQTY")[:-4] or 0)
                temp_item["rate"] = float(item.findtext("RATE")[:-4] or 0)
                temp_item["taxable_value"] = abs(float(item.findtext("AMOUNT") or 0))

                if float(item.findtext("DISCOUNT") or 0):
                    temp_item["discount_type"] = "%"
                    temp_item["discount"] = float(item.findtext("DISCOUNT") or 0)

                gst_rate, tax_type = self.get_gst_rate(voucher, False)
                temp_item["gst_rate"] = gst_rate

                if tax_type == "IGST":
                    temp_item["igst"] = round((temp_item["taxable_value"] * gst_rate) / 100, 2)
                else:
                    temp_item["cgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)
                    temp_item["sgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)

                temp_item["invoice_value"] = round((temp_item["taxable_value"] or 0) + (temp_item.get("igst") or 0) + (temp_item.get("cgst") or 0) + (temp_item.get("sgst") or 0), 2)

                items.append(temp_item)

            temp_dict["items"] = items
            invoices.append(temp_dict)

        # print("invoices", invoices)
        return invoices

    async def get_sales_order(self, start_date, end_date):
        from_date = start_date.strftime("%d-%b-%Y")
        to_date   = end_date.strftime("%d-%b-%Y")

        xml_request  = sale_order_tdl.format(from_date=from_date, to_date=to_date)
        request = requests.post(self.url, data=xml_request)
        response = request.text

        # print(response)

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        # Sales
        invoices = []
        for voucher in root.findall(".//VOUCHER"):
            temp_dict = {}

            if not voucher.findtext("VOUCHERNUMBER"):
                continue

            temp_dict["invoice_no"] = voucher.findtext("VOUCHERNUMBER")
            invoice_date = voucher.findtext("DATE")
            temp_dict["invoice_date"] = datetime.strptime(invoice_date, "%Y%m%d").strftime("%d-%m-%Y")
            temp_dict["customer_name"] = voucher.findtext("PARTYLEDGERNAME")
            temp_dict["placeOfSupply"] = voucher.findtext("PLACEOFSUPPLY")

            items = []
            for item in voucher.findall(".//ALLINVENTORYENTRIES.LIST"):
                temp_item = {}
                temp_item["item_name"] = item.findtext("STOCKITEMNAME")
                temp_item["category"] = "Inventory"

                uml = item.findtext("BILLEDQTY")[-3:]
                uml = uml.lower()
                uml = measurement[uml]
                temp_item["uml"] = uml

                temp_item["qty"] = float(item.findtext("BILLEDQTY")[:-4] or 0)
                temp_item["rate"] = float(item.findtext("RATE")[:-4] or 0)
                temp_item["taxable_value"] = abs(float(item.findtext("AMOUNT") or 0))

                if float(item.findtext("DISCOUNT") or 0):
                    temp_item["discount_type"] = "%"
                    temp_item["discount"] = float(item.findtext("DISCOUNT") or 0)

                gst_rate, tax_type = self.get_gst_rate(voucher, True)

                temp_item["gst_rate"] = gst_rate
                if tax_type == "IGST":
                    temp_item["igst"] = round((temp_item["taxable_value"] * gst_rate) / 100, 2)
                else:
                    temp_item["cgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)
                    temp_item["sgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)

                temp_item["invoice_value"] = round((temp_item["taxable_value"] or 0) + (temp_item.get("igst") or 0) + (temp_item.get("cgst") or 0) + (temp_item.get("sgst") or 0), 2)

                items.append(temp_item)

            temp_dict["items"] = items
            invoices.append(temp_dict)

        # print("invoices", invoices)
        return invoices
    
    async def get_purchase_order(self, start_date, end_date):
        from_date = start_date.strftime("%d-%b-%Y")
        to_date   = end_date.strftime("%d-%b-%Y")

        xml_request  = purchase_order_tdl.format(from_date=from_date, to_date=to_date)
        request = requests.post(self.url, data=xml_request)
        response = request.text

        # print(response)

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        # Sales
        invoices = []
        for voucher in root.findall(".//VOUCHER"):
            temp_dict = {}

            if not voucher.findtext("VOUCHERNUMBER"):
                continue

            temp_dict["invoice_no"] = voucher.findtext("VOUCHERNUMBER")
            invoice_date = voucher.findtext("DATE")
            temp_dict["invoice_date"] = datetime.strptime(invoice_date, "%Y%m%d").strftime("%d-%m-%Y")
            temp_dict["customer_name"] = voucher.findtext("PARTYLEDGERNAME")
            temp_dict["placeOfSupply"] = voucher.findtext("PLACEOFSUPPLY")

            items = []
            for item in voucher.findall(".//ALLINVENTORYENTRIES.LIST"):
                temp_item = {}
                temp_item["item_name"] = item.findtext("STOCKITEMNAME")
                temp_item["category"] = "Inventory"

                uml = item.findtext("BILLEDQTY")[-3:]
                uml = uml.lower()
                uml = measurement[uml]
                temp_item["uml"] = uml

                temp_item["qty"] = float(item.findtext("BILLEDQTY")[:-4] or 0)
                temp_item["rate"] = float(item.findtext("RATE")[:-4] or 0)
                temp_item["taxable_value"] = abs(float(item.findtext("AMOUNT") or 0))

                if float(item.findtext("DISCOUNT") or 0):
                    temp_item["discount_type"] = "%"
                    temp_item["discount"] = float(item.findtext("DISCOUNT") or 0)

                gst_rate = 0
                tax_type = ""
                for rate_item in item.findall("RATEDETAILS.LIST"):
                    tax_type = rate_item.findtext("GSTRATEDUTYHEAD")
                    if tax_type in ["CGST", "SGST/UTGST", "SGST"]:
                        gst_rate += float(rate_item.findtext("GSTRATE"))
                    elif tax_type == "IGST":
                        gst_rate = float(rate_item.findtext("GSTRATE"))

                temp_item["gst_rate"] = gst_rate
                if tax_type == "IGST":
                    temp_item["igst"] = round((temp_item["taxable_value"] * gst_rate) / 100, 2)
                else:
                    temp_item["cgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)
                    temp_item["sgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)

                temp_item["invoice_value"] = (temp_item["taxable_value"] or 0) + (temp_item.get("igst") or 0) + (temp_item.get("cgst") or 0) + (temp_item.get("sgst") or 0)

                items.append(temp_item)

            temp_dict["items"] = items
            invoices.append(temp_dict)

        # print("invoices", invoices)
        return invoices
    
    async def get_delivery_challan(self, start_date, end_date):
        from_date = start_date.strftime("%d-%b-%Y")
        to_date   = end_date.strftime("%d-%b-%Y")

        xml_request  = delivery_challan_tdl.format(from_date=from_date, to_date=to_date)
        request = requests.post(self.url, data=xml_request)
        response = request.text

        print(response)

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        # Sales
        invoices = []
        for voucher in root.findall(".//VOUCHER"):
            temp_dict = {}

            if not voucher.findtext("VOUCHERNUMBER"):
                continue

            temp_dict["invoice_no"] = voucher.findtext("VOUCHERNUMBER")
            invoice_date = voucher.findtext("DATE")
            temp_dict["invoice_date"] = datetime.strptime(invoice_date, "%Y%m%d").strftime("%d-%m-%Y")
            temp_dict["customer_name"] = voucher.findtext("PARTYLEDGERNAME")
            temp_dict["placeOfSupply"] = voucher.findtext("PLACEOFSUPPLY")

            items = []
            for item in voucher.findall(".//ALLINVENTORYENTRIES.LIST"):
                temp_item = {}
                temp_item["item_name"] = item.findtext("STOCKITEMNAME")
                temp_item["category"] = "Inventory"

                uml = item.findtext("BILLEDQTY")[-3:]
                uml = uml.lower()
                uml = measurement[uml]
                temp_item["uml"] = uml

                temp_item["qty"] = float(item.findtext("BILLEDQTY")[:-4] or 0)
                temp_item["rate"] = float(item.findtext("RATE")[:-4] or 0)
                temp_item["taxable_value"] = abs(float(item.findtext("AMOUNT") or 0))

                if float(item.findtext("DISCOUNT") or 0):
                    temp_item["discount_type"] = "%"
                    temp_item["discount"] = float(item.findtext("DISCOUNT") or 0)

                # gst_rate = 0
                # tax_type = ""
                # for rate_item in item.findall("RATEDETAILS.LIST"):
                #     tax_type = rate_item.findtext("GSTRATEDUTYHEAD")
                #     if tax_type in ["CGST", "SGST/UTGST", "SGST"]:
                #         gst_rate += float(rate_item.findtext("GSTRATE"))
                #     elif tax_type == "IGST":
                #         gst_rate = float(rate_item.findtext("GSTRATE"))

                gst_rate, tax_type = self.get_gst_rate(voucher, True)

                temp_item["gst_rate"] = gst_rate
                if tax_type == "IGST":
                    temp_item["igst"] = round((temp_item["taxable_value"] * gst_rate) / 100, 2)
                else:
                    temp_item["cgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)
                    temp_item["sgst"] = round((temp_item["taxable_value"] * gst_rate) / 200, 2)

                temp_item["invoice_value"] = round((temp_item["taxable_value"] or 0) + (temp_item.get("igst") or 0) + (temp_item.get("cgst") or 0) + (temp_item.get("sgst") or 0), 2)
                items.append(temp_item)

            temp_dict["items"] = items
            invoices.append(temp_dict)

        # print("invoices", invoices)
        return invoices

    async def get_tally_journal(self, start_date, end_date):
        from_date = start_date.strftime("%d-%b-%Y")
        to_date = end_date.strftime("%d-%b-%Y")

        xml_request  = journal_tdl.format(from_date=from_date, to_date=to_date)
        request = requests.post(self.url, data=xml_request)
        response = request.text

        # print("response", response)

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        # Sales
        invoices = []
        for voucher in root.findall(".//VOUCHER"):
            temp_dict = {}
            if not voucher.findtext("VOUCHERNUMBER"):
                continue

            temp_dict["invoice_no"] = voucher.findtext("VOUCHERNUMBER")
            invoice_date = voucher.findtext("DATE")
            temp_dict["invoice_date"] = datetime.strptime(invoice_date, "%Y%m%d").strftime("%d-%m-%Y")

            items = []
            party_name = ""
            nature_name = ""
            total_amount = 0
            for item in voucher.findall(".//ALLLEDGERENTRIES.LIST"):
                if item.findtext("ISDEEMEDPOSITIVE") == "Yes":
                    total_amount += abs(float(item.findtext("AMOUNT") or 0) )
                    party_name = item.findtext("LEDGERNAME")
                else:
                    temp_item = {}
                    if not nature_name:
                        nature_name = item.findtext("LEDGERNAME")
                    temp_item["nature_name"] = item.findtext("LEDGERNAME")
                    temp_item["amount"] = item.findtext("AMOUNT")

                    items.append(temp_item)

            temp_dict["party_name"] = party_name
            temp_dict["nature_name"] = nature_name
            temp_dict["amount"] = total_amount
            temp_dict["narration"] = voucher.findtext("NARRATION")

            temp_dict["items"] = items
            invoices.append(temp_dict)

        # print("invoices", invoices)
        return invoices

    async def get_stock_jurnal(self, start_date, end_date):
        from_date = start_date.strftime("%d-%b-%Y")
        to_date   = end_date.strftime("%d-%b-%Y")

        xml_request  = stockJournal_tdl.format(from_date=from_date, to_date=to_date)
        request = requests.post(self.url, data=xml_request)
        response = request.text

        # print("response", response)

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        # Sales
        invoices = []
        for voucher in root.findall(".//VOUCHER"):
            temp_dict = {}

            if not voucher.findtext("VOUCHERNUMBER"):
                continue

            temp_dict["invoice_no"] = voucher.findtext("VOUCHERNUMBER")
            invoice_date = voucher.findtext("DATE")
            temp_dict["invoice_date"] = datetime.strptime(invoice_date, "%Y%m%d").strftime("%d-%m-%Y")

            total_amount = 0
            source_items = []
            product_items = []
            for item in voucher.findall(".//ALLINVENTORYENTRIES.LIST"):
                temp_item = {}

                temp_item["item_name"] = item.findtext("STOCKITEMNAME")
                temp_item["qty"] = float(item.findtext("BILLEDQTY")[:-4] or 0)
                temp_item["rate"] = float(item.findtext("RATE")[:-4] or 0)
                temp_item["amount"] = abs(float(item.findtext("AMOUNT") or 0))

                if item.findtext("ISDEEMEDPOSITIVE") == "Yes":
                    product_items.append(temp_item)
                    total_amount += abs(float(item.findtext("AMOUNT") or 0))
                else:
                    source_items.append(temp_item)

            temp_dict["total_amount"] = total_amount
            temp_dict["narration"] = voucher.findtext("NARRATION")
            temp_dict["source_items"] = source_items
            temp_dict["product_items"] = product_items
            temp_dict["items"] = []
            invoices.append(temp_dict)

        print("invoices", invoices)
        return invoices


    # BUSY Connector Methods
    def connect_busy(self, dsn: str, username: str, password: str) -> bool:
        """Mock BUSY connection"""
        self.busy_status = ConnectorStatus.PENDING
        self.busy_status_changed.emit(self.busy_status)
        
        self._add_log(LogLevel.INFO, f"Attempting to connect to BUSY via DSN: {dsn}", "BUSY")
        
        QTimer.singleShot(1500, self._simulate_busy_connection)
        return True
    
    def _simulate_busy_connection(self):
        """Simulate BUSY connection result"""
        import random
        success = random.choice([True, True, False])
        
        if success:
            self.busy_status = ConnectorStatus.CONNECTED
            self._add_log(LogLevel.SUCCESS, "BUSY connection successful", "BUSY")
        else:
            self.busy_status = ConnectorStatus.ERROR
            self._add_log(LogLevel.ERROR, "BUSY connection failed", "BUSY")
        
        self.busy_status_changed.emit(self.busy_status)
    
    def disconnect_busy(self):
        """Disconnect BUSY"""
        self.busy_status = ConnectorStatus.DISCONNECTED
        self.busy_status_changed.emit(self.busy_status)
        self._add_log(LogLevel.INFO, "BUSY disconnected", "BUSY")
    
    def export_busy_data(self, config: BusyConfig) -> bool:
        """Mock BUSY data export"""
        self._add_log(LogLevel.INFO, "Starting BUSY data export...", "BUSY")
        
        # TODO: Implement actual BUSY ODBC export logic
        
        QTimer.singleShot(2000, lambda: self._complete_export("BUSY"))
        return True
    
    def _complete_export(self, source: str):
        """Complete export simulation"""
        self.last_sync_time = datetime.now()
        self._add_log(LogLevel.SUCCESS, f"{source} data export completed", source)
    
    # Sync Methods
    def serialize_dates(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return obj

    # def sync_tally_data(self, config: TallyConfig, data) -> bool:
    #     """Mock Tally data sync"""
    #     self._add_log(LogLevel.INFO, "Starting Tally data sync...", "Tally")
        
    #     access_token = {
    #         "Authorization": f"Bearer {self.access_token}",
    #         "Content-Type": "application/json"
    #     }
    #     url = "http://127.0.0.1:8000/tallyConnector"

    #     if "Ledgers" in config.selected_data_types:
    #         payload = {"ledgers": data.get('ledgers')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/importLedger", json=payload_json, headers=access_token)
    #         response = request.text

    #     if "Stocks" in config.selected_data_types:
    #         payload = {"stocks": data.get('stocks')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/importStocks", json=payload_json, headers=access_token)
    #         response = request.text

    #     if "Sales" in config.selected_data_types:
    #         payload = {"sales": data.get('sales')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/slaes", json=payload_json, headers=access_token)
    #         response = request.text

    #     if "Purchase" in config.selected_data_types:
    #         payload = {"purchase": data.get('purchase')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/purchase", json=payload_json, headers=access_token)
    #         response = request.text

    #     if "Credit Note" in config.selected_data_types:
    #         payload = {"credit_note": data.get('credit_note')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/creditNote", json=payload_json, headers=access_token)
    #         response = request.text
        
    #     if "Debit Note" in config.selected_data_types:
    #         payload = {"debit_note": data.get('debit_note')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/debitNote", json=payload_json, headers=access_token)
    #         response = request.text

    #     if "Sale Order" in config.selected_data_types:
    #         payload = {"sale_order": data.get('sale_order')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/saleOrder", json=payload_json, headers=access_token)
    #         response = request.text

    #     if "Purchase Order" in config.selected_data_types:
    #         payload = {"purchase_order": data.get('purchase_order')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/purchaseOrder", json=payload_json, headers=access_token)
    #         response = request.text

    #     if "Delivery Challan" in config.selected_data_types:
    #         payload = {"delivery_challan": data.get('delivery_challan')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/deliveryChallan", json=payload_json, headers=access_token)
    #         response = request.text

    #     if "Receipt" in config.selected_data_types:
    #         payload = {"receipt": data.get('receipt')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/receipt", json=payload_json, headers=access_token)
    #         response = request.text

    #     if "Payment" in config.selected_data_types:
    #         payload = {"payment": data.get('payment')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/payment", json=payload_json, headers=access_token)
    #         response = request.text

    #     if "Journal" in config.selected_data_types:
    #         payload = {"journal": data.get('journal')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/jurnal", json=payload_json, headers=access_token)
    #         response = request.text

    #     if "Stock Journal" in config.selected_data_types:
    #         payload = {"stock_journal": data.get('stock_journal')}
    #         payload_json = json.loads(
    #             json.dumps(payload, default=self.serialize_dates)
    #         )
    #         request = requests.post(f"{url}/stock_journal", json=payload_json, headers=access_token)
    #         response = request.text

    #         print("response", response)

    #     QTimer.singleShot(2500, lambda: self._complete_sync("Tally"))
    #     return True
    
    async def sync_tally_data(self, config: TallyConfig, data) -> bool:
        """Parallel Tally data sync to cloud"""

        self._add_log(LogLevel.INFO, "Starting Tally data sync...", "Tally")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        base_url = "http://127.0.0.1:8000/tallyConnector"

        tasks = []
        task_names = []

        async def send(endpoint, key):
            payload = {key: data.get(key)}

            payload_json = json.loads(
                json.dumps(payload, default=self.serialize_dates)
            )

            async with semaphore:
                async with httpx.AsyncClient(timeout=300) as client:
                    response = await client.post(
                        f"{base_url}/{endpoint}",
                        json=payload_json,
                        headers=headers,
                    )
                    response.raise_for_status()
                    return response.text

        # ✅ limit concurrency (VERY IMPORTANT)
        semaphore = asyncio.Semaphore(5)

        mapping = {
            "Ledgers": ("importLedger", "ledgers"),
            "Stocks": ("importStocks", "stocks"),
            "Sales": ("slaes", "sales"),
            "Purchase": ("purchase", "purchase"),
            "Credit Note": ("creditNote", "credit_note"),
            "Debit Note": ("debitNote", "debit_note"),
            "Sale Order": ("saleOrder", "sale_order"),
            "Purchase Order": ("purchaseOrder", "purchase_order"),
            "Delivery Challan": ("deliveryChallan", "delivery_challan"),
            "Receipt": ("receipt", "receipt"),
            "Payment": ("payment", "payment"),
            "Journal": ("jurnal", "journal"),
            "Stock Journal": ("stock_journal", "stock_journal"),
        }

        try:
            for dtype in config.selected_data_types:
                if dtype in mapping:
                    endpoint, key = mapping[dtype]
                    tasks.append(send(endpoint, key))
                    task_names.append(dtype)

            # 🚀 PARALLEL CLOUD UPLOAD
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for name, result in zip(task_names, results):
                if isinstance(result, Exception):
                    logging.exception(result)
                    raise Exception(f"{name} sync failed")

            QTimer.singleShot(2500, lambda: self._complete_sync("Tally"))
            return True

        except Exception as e:
            logging.exception(e)
            raise Exception(e)

    def sync_busy_data(self, config: BusyConfig) -> bool:
        """Mock BUSY data sync"""
        self._add_log(LogLevel.INFO, "Starting BUSY data sync...", "BUSY")
        
        # TODO: Implement actual BUSY sync logic
        
        QTimer.singleShot(2500, lambda: self._complete_sync("BUSY"))
        return True
    
    def _complete_sync(self, source: str):
        """Complete sync simulation"""
        self.last_sync_time = datetime.now()
        self._add_log(LogLevel.SUCCESS, f"{source} data sync completed", source)
    
    # Utility Methods
    def get_logs(self) -> List[LogEntry]:
        """Get all logs"""
        return self.logs.copy()
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs.clear()
        self._add_log(LogLevel.INFO, "Logs cleared", "System")
    
    def get_last_sync_time(self) -> datetime:
        """Get last sync time"""
        return self.last_sync_time
    
    def get_status_color(self, status: ConnectorStatus) -> str:
        """Get CSS color for status"""
        colors = {
            ConnectorStatus.CONNECTED: "#4CAF50",
            ConnectorStatus.DISCONNECTED: "#F44336",
            ConnectorStatus.PENDING: "#FF9800",
            ConnectorStatus.ERROR: "#9C27B0"
        }
        return colors.get(status, "#757575")