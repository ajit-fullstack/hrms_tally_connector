"""
Application controller for Accounting Connector
"""

import requests, json, asyncio, httpx, logging, re
from utils.tdl import *
from utils.drop_down import *
from utils.utils import Utils
from datetime import datetime
import xml.etree.ElementTree as ET
from datetime import date, datetime
from typing import List
from PySide6.QtCore import QObject, Signal, QTimer

from src.models import (
    ConnectorStatus, LogLevel, LogEntry,
    TallyConfig, BusyConfig
)

logging.basicConfig(filename="error.txt", format="%(asctime)s - %(message)s", level=logging.DEBUG)

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
        self.dublicate_invoice = dict()
        self.ledger_category_map = dict()
    
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
        login_url = "https://api-hr.startupkhata.com/api/auth/login"


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
    
    def get_month_year_range(self, start_date: datetime, end_date: datetime):
        result = []        
        current = start_date.replace(day=1)

        while current <= end_date:
            result.append({
                "month": current.month,
                "year": current.year
            })

            # move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return result
    
    async def fetch_data(self, client, month, year, headers):
        params = { "month": month, "year": year }
        url = "https://api-hr.startupkhata.com/import/salary"

        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        return response.json()

    async def export_tally_data(self, config: TallyConfig) -> dict:
        """Parallel Tally data export"""

        self._add_log(LogLevel.INFO, "Starting Tally data export...", "Tally")
        self.url = f"http://{config.host}:{config.port}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        try:
            final_data = {}
            month_year_list = self.get_month_year_range(config.date_from, config.date_to)

            result_data = []
            async with httpx.AsyncClient(timeout=30.0) as client:
                tasks = [
                    self.fetch_data(client, item["month"], item["year"], headers)
                    for item in month_year_list
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)
                if results:
                    for result in results:
                        result_data.extend(result)

            final_data['journal'] = result_data
        
            response = requests.get('https://api-hr.startupkhata.com/import/employees', headers=headers)
            if response.text:
                final_data['ledgers'] = response.json()

            QTimer.singleShot(7000, lambda: self._complete_export("Tally"))
            return final_data

        except Exception as e:
            logging.exception(e)
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
    

    # BUSY Connector Methods
    def connect_busy(self, dsn: str, username: str, password: str) -> bool:
        """Mock BUSY connection"""
        self.busy_status = ConnectorStatus.PENDING
        self.busy_status_changed.emit(self.busy_status)
        
        self.url = f"http://localhost:981/busyapi"

        self._add_log(LogLevel.INFO, f"Attempting to connect to BUSY via DSN: {dsn}", "BUSY")
        
        QTimer.singleShot(1000, self._busy_connection)
        return True
    
    def _busy_connection(self):
        """Simulate BUSY connection result"""
        success = self.get_busy_companies()
        
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
    
    def generate_xml(voucher_type, from_date, to_date):
        return f"""
            <REQUEST>
                <HEADER>
                    <REQUESTTYPE>Get</REQUESTTYPE>
                    <OBJECT>Voucher</OBJECT>
                </HEADER>
                <BODY>
                    <FILTERS>
                        <FILTER>
                            <NAME>VoucherType</NAME>
                            <VALUE>{voucher_type}</VALUE>
                        </FILTER>
                        <FILTER>
                            <NAME>DateRange</NAME>
                            <FROM>{from_date}</FROM>
                            <TO>{to_date}</TO>
                        </FILTER>
                    </FILTERS>

                    <FIELDS>
                        <FIELD>Date</FIELD>
                        <FIELD>VoucherNo</FIELD>
                        <FIELD>PartyName</FIELD>
                        <FIELD>Amount</FIELD>
                        <FIELD>Discount</FIELD>
                        <FIELD>PlaceOfSupply</FIELD>
                    </FIELDS>

                    <CHILDFIELDS>
                        <CHILDFIELD>
                            <NAME>InventoryEntries</NAME>
                            <FIELDS>
                                <FIELD>ItemName</FIELD>
                                <FIELD>Qty</FIELD>
                                <FIELD>Unit</FIELD>
                                <FIELD>Rate</FIELD>
                                <FIELD>Amount</FIELD>
                                <FIELD>Discount</FIELD>
                            </FIELDS>
                        </CHILDFIELD>
                    </CHILDFIELDS>
                </BODY>
            </REQUEST>
        """

    # Export Data Form Busy
    def get_busy_companies(self):
        headers = {
            "Content-Type": "text/xml"
        }

        xml_request = """
        <REQUEST>
            <HEADER>
                <REQUESTTYPE>GetCompanyList</REQUESTTYPE>
            </HEADER>
        </REQUEST>
        """

        response = requests.post(self.url, data=xml_request, headers=headers)

        # print("response:", response.text)

        root = ET.fromstring(response.text)

        companies = []

        for company in root.findall(".//COMPANY"):
            name = company.findtext("NAME")
            if name:
                companies.append(name)

        return companies
    

    # Sync Methods
    def serialize_dates(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return obj

    def fetch_data_from_tally(self, config):
        url = "http://localhost:9000"

        # <SVFROMDATE>{from_date}</SVFROMDATE>
        # <SVTODATE>{to_date}</SVTODATE>

        headers = {"Content-Type": "application/xml"}

        response = requests.post(url, data=combined_fetch_tdl, headers=headers)
        response = response.text

        logging.debug(response)

        response = Utils.clean_tally_xml(response)
        root = ET.fromstring(response)

        ledger_categories = []
        for group in root.findall(".//GROUP"):
            name = ""
            for lang in group.findall(".//LANGUAGENAME.LIST"):
                for child in lang.findall(".//NAME.LIST/NAME"):
                    name = child.text

            if name:
                ledger_categories.append(name)

        ledgers = []
        for ledger in root.findall(".//LEDGER"):
            name = ""
            for lang in ledger.findall(".//LANGUAGENAME.LIST"):
                for child in lang.findall(".//NAME.LIST/NAME"):
                    name = child.text

            if name:
                if name.lower() not in ledgers:
                    ledgers.append(name.lower())

        journals = []
        for voucher in root.findall(".//VOUCHER"):
            if not voucher.findtext('VOUCHERNUMBER'):
                continue

            amount = 0
            temp_dict = {}
            need_to_continue = False
            for item in voucher.findall('.//ALLLEDGERENTRIES.LIST'):
                if item.findtext('ISDEEMEDPOSITIVE') == 'Yes':
                    amount += abs(float(item.findtext('AMOUNT') or 0))
                    temp_dict['party_name'] = item.findtext('LEDGERNAME')
                else:
                    nature = item.findtext('LEDGERNAME')

                    if nature.lower() != 'salary':
                        need_to_continue = True
                        continue
                    
                    temp_dict["nature"] = nature

            if need_to_continue:
                continue

            temp_dict["amount"] = amount
            journals.append(temp_dict)

        return {
            'ledgers': ledgers,
            'journals': journals,
            'ledger_categories': ledger_categories
        }

    # sync tally group function    
    def sync_group(self, tally_groups):
        groups_need_to_create = []
        if 'salary payable' not in tally_groups:
            groups_need_to_create.append({'name': 'Salary Payable', 'parent': 'Current Liabilities'})

        return groups_need_to_create

    def create_groups(self, groups):
        xml_payload = """
            <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Import</TALLYREQUEST>
                <TYPE>Data</TYPE>
                <ID>All Masters</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <REPORTNAME>All Masters</REPORTNAME>
                </DESC>
                <DATA>
                    <TALLYMESSAGE xmlns:UDF="TallyUDF">
        """

        for group in groups:
            xml_payload += f"""
                <GROUP NAME="{group.get('name')}" ACTION="Create">
                    <NAME>{group.get('name')}</NAME>
                    <PARENT>{group.get('parent')}</PARENT>
                    <ISSUBLEDGER>No</ISSUBLEDGER>
                    <ISBILLWISEON>No</ISBILLWISEON>
                    <ISREVENUE>No</ISREVENUE>
                </GROUP>
            """

        xml_payload += """
                    </TALLYMESSAGE>
                </DATA>
            </BODY>
        </ENVELOPE>
        """

        headers = {"Content-Type": "application/xml"}
        response = requests.post(self.url, data=xml_payload, headers=headers)
        response.raise_for_status()  # handles 4xx/5xx
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(response.text)

    # sync tally ledger function
    def create_salary_ledger(self):
        xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
            <ENVELOPE>
            <HEADER>
                <TALLYREQUEST>Import Data</TALLYREQUEST>
            </HEADER>
            <BODY>
                <IMPORTDATA>
                    <REQUESTDESC>
                        <REPORTNAME>All Masters</REPORTNAME>
                    </REQUESTDESC>
                    <REQUESTDATA>
                        <TALLYMESSAGE>
                            <LEDGER NAME="Salary" ACTION="Create">
                                <NAME>Salary</NAME>
                                <PARENT>Expenses (Indirect)</PARENT>
                            </LEDGER>
                        </TALLYMESSAGE>
                    </REQUESTDATA>
                </IMPORTDATA>
            </BODY>
        </ENVELOPE>
        """

        headers = {"Content-Type": "application/xml"}
        response = requests.post(self.url, data=xml_data, headers=headers)
        response.raise_for_status()  # handles 4xx/5xx
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(response.text)
        
    def sync_ledger(self, tally_ledgers, data):
        ledger_need_to_create = []
        for item in data:
            if item.get('ledger_name').lower() not in tally_ledgers:
                ledger_need_to_create.append(item)
        
        if "salary" not in tally_ledgers:
            self.create_salary_ledger()
        
        return ledger_need_to_create

    def create_ledger(self, ledgers):
        xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
            <ENVELOPE>
            <HEADER>
                <TALLYREQUEST>Import Data</TALLYREQUEST>
            </HEADER>
            <BODY>
                <IMPORTDATA>
                <REQUESTDESC>
                    <REPORTNAME>All Masters</REPORTNAME>
                </REQUESTDESC>
                <REQUESTDATA>
            """

        for ledger in ledgers:
            xml_data += f"""
                <TALLYMESSAGE>
                    <LEDGER NAME="{ledger['ledger_name']}" ACTION="Create">
                        <NAME>{ledger['ledger_name']}</NAME>
                        <PARENT>{ledger['parent']}</PARENT>

                        <ADDRESS.LIST TYPE="String">
                            <ADDRESS>{ledger.get('ledgerAddress','')}</ADDRESS>
                        </ADDRESS.LIST>

                        <STATE>{ledger.get('ledgerState','')}</STATE>
                        <COUNTRY>{ledger.get('ledgerCountry','India')}</COUNTRY>
                        <PINCODE>{ledger.get('ledgerPincode','')}</PINCODE>

                        <LEDGERPHONE>{ledger.get('ledgerMobile','')}</LEDGERPHONE>
                        <EMAIL>{ledger.get('ledgerEmail','')}</EMAIL>

                    </LEDGER>
                </TALLYMESSAGE>
                """     
            
        xml_data += """
                    </REQUESTDATA>
                </IMPORTDATA>
            </BODY>
        </ENVELOPE>
        """

        headers = {"Content-Type": "application/xml"}
        response = requests.post(self.url, data=xml_data, headers=headers)
        response.raise_for_status()  # handles 4xx/5xx
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(response.text)

    # sync tally journal function
    def sync_journal(self, tally_jounals, data):
        def make_key(j):
            return (
                j["party_name"].lower(),
                j["nature"].lower(),
                float(j["amount"])
            )
        
        tally_set = {make_key(t) for t in tally_jounals}

        new_journals = []
        for h in data:
            r = make_key(h)
            if r not in tally_set:
                new_journals.append(h)

        return new_journals

    def create_journal(self, journals):
        xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
            <ENVELOPE>
                <HEADER>
                    <TALLYREQUEST>Import Data</TALLYREQUEST>
                </HEADER>
                <BODY>
                    <IMPORTDATA>
                        <REQUESTDESC>
                            <REPORTNAME>Vouchers</REPORTNAME>
                        </REQUESTDESC>
                        <REQUESTDATA>
            """

        for journal in journals:
            date = datetime.strptime(journal["voucher_date"], '%d-%m-%Y').strftime("%Y%m%d")

            xml_data += f"""
                <TALLYMESSAGE>
                    <VOUCHER VCHTYPE="Journal" ACTION="Create">
                        <VOUCHERTYPENAME>Journal</VOUCHERTYPENAME>
                        <DATE>{date}</DATE>
                        <VOUCHERNUMBER>{journal["voucher_no"]}</VOUCHERNUMBER>
                        <NARRATION>Imported from HR-Payroll through tally connector.</NARRATION>
                
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{journal["party_name"]}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>{-journal["amount"]}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{journal["nature"]}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                            <AMOUNT>{journal["amount"]}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                
                    </VOUCHER>
                </TALLYMESSAGE>
            """

        xml_data += """
                    </REQUESTDATA>
                </IMPORTDATA>
            </BODY>
        </ENVELOPE>
        """

        headers = {"Content-Type": "application/xml"}
        response = requests.post(self.url, data=xml_data, headers=headers)
        response.raise_for_status()  # handles 4xx/5xx
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(response.text)

    async def sync_tally_data(self, config: TallyConfig, data) -> bool:
        """Parallel Tally data sync to cloud"""
        try:
            self._add_log(LogLevel.INFO, "Starting Tally data sync...", "Tally")
            tally_data = self.fetch_data_from_tally(config)

            # sync tally groups
            groups_need_to_create = self.sync_group(tally_data.get('ledger_categories'))
            self.create_groups(groups_need_to_create)

            # sync ledger
            ledger_need_to_create = self.sync_ledger(tally_data.get('ledgers'), data.get('ledgers'))
            self.create_ledger(ledger_need_to_create)

            # sync journl
            journal_need_to_create = self.sync_journal(tally_data.get('journals'), data.get('journal'))
            self.create_journal(journal_need_to_create)

            return {"message": "Data has been sucessfully synced.."}
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
    