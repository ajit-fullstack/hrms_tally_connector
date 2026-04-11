company_details_xml = """
  <ENVELOPE>
  <HEADER>
      <VERSION>1</VERSION>
      <TALLYREQUEST>EXPORT</TALLYREQUEST>
      <TYPE>COLLECTION</TYPE>
      <ID>CompanyDetails</ID>
  </HEADER>

  <BODY>
      <DESC>
      <STATICVARIABLES>
          <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>

      <TDL>
          <TDLMESSAGE>

          <COLLECTION NAME="CompanyDetails">
              <TYPE>COMPANY</TYPE>
              <FETCH>
              NAME,
              GUID,
              ADDRESS,
              STATENAME,
              COUNTRYNAME,
              PINCODE,
              GSTIN
              </FETCH>
          </COLLECTION>

          </TDLMESSAGE>
      </TDL>

      </DESC>
  </BODY>
  </ENVELOPE>
"""

stocks_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>StockItemDetails</ID>
  </HEADER>

  <BODY>
    <DESC>

      <STATICVARIABLES>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>
  
      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="StockItemDetails">
            <TYPE>STOCKITEM</TYPE>

            <FETCH>
              NAME,
              PARENT,
              BASEUNITS,

              GSTCLASSIFICATIONS,
              GSTAPPLICABLE,
              GSTDETAILS,
              GSTRATE,

              OPENINGBALANCE,
              OPENINGRATE,
              OPENINGVALUE,

              IsServiceItem,
              IsInventoriable,
              GSTTypeOfSupply
            </FETCH>

          </COLLECTION>

        </TDLMESSAGE> 
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

ledger_tdl = """
  <ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>LedgerDetails</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="LedgerDetails">
            <TYPE>LEDGER</TYPE>
            <FETCH>
              NAME,
              PARENT,
              ADDRESS,
              COUNTRYNAME,
              PRIORSTATENAME,
              PINCODE,
              ACCOUNTNUMBER,
              BANKNAME,
              TAXTYPE,
              OPENINGBALANCE,
              CLOSINGBALANCE,
              ISDEEMEDPOSITIVE,
              LEDGSTREGDETAILS.GSTIN,
            </FETCH>
            
            <SUBCOLLECTION NAME="GSTDetails">
              <TYPE>LEDGSTREGDETAILS</TYPE>
              <FETCH>
                GSTIN
              </FETCH>
            </SUBCOLLECTION>

            </COLLECTION>
        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

sales_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>SalesVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>

      <STATICVARIABLES>
        <SVFROMDATE TYPE="Date">{from_date}</SVFROMDATE>
        <SVTODATE TYPE="Date">{to_date}</SVTODATE>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="SalesVouchers">
            <TYPE>Voucher</TYPE>
            <FILTER>IsSales</FILTER>

            <FETCH>
              DATE,
              VOUCHERNUMBER,
              VOUCHERTYPENAME,
              PARTYLEDGERNAME,
              PLACEOFSUPPLY,

              INVENTORYENTRIES.STOCKITEMNAME,
              INVENTORYENTRIES.BILLEDQTY,
              INVENTORYENTRIES.RATE,
              INVENTORYENTRIES.DISCOUNT,
              INVENTORYENTRIES.AMOUNT,

              ALLLEDGERENTRIES.LEDGERNAME,
              ALLLEDGERENTRIES.AMOUNT,
              ALLLEDGERENTRIES.ISDEEMEDPOSITIVE,
              ALLLEDGERENTRIES.LEDGERNAME.PARENT,
              ALLLEDGERENTRIES.GROUPNAME
            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formula" NAME="IsSales">
            $$IsSales:$VoucherTypeName
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

purchase_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>PurchaseVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>

      <STATICVARIABLES>
        <SVFROMDATE TYPE="Date">{from_date}</SVFROMDATE>
        <SVTODATE TYPE="Date">{to_date}</SVTODATE>

        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="PurchaseVouchers">
            <TYPE>Voucher</TYPE>
            <FILTER>IsPurchase</FILTER>

            <FETCH>
              DATE,
              VOUCHERNUMBER,
              PARTYLEDGERNAME,

              REFERENCE,
              REFERENCEDATE,
              PLACEOFSUPPLY,

              INVENTORYENTRIES.STOCKITEMNAME,
              INVENTORYENTRIES.BILLEDQTY,
              INVENTORYENTRIES.RATE,
              INVENTORYENTRIES.DISCOUNT,
              INVENTORYENTRIES.AMOUNT,
              INVENTORYENTRIES.RATEDETAILS

            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formula" NAME="IsPurchase">
            $$IsPurchase:$VoucherTypeName
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY> 
</ENVELOPE>
"""

creditNote_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>CreditNoteVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="CreditNoteVouchers">
            <TYPE>VOUCHER</TYPE>

            <!-- FILTER ONLY CREDIT NOTES -->
            <FILTER>IsCreditNote</FILTER>

            <!-- FETCH EVERYTHING IMPORTANT -->
            <FETCH>
              DATE,
              VOUCHERNUMBER,
              VOUCHERTYPENAME,
              PARTYLEDGERNAME,
              PLACEOFSUPPLY,
              INVENTORYENTRIES.STOCKITEMNAME,
              INVENTORYENTRIES.BILLEDQTY,
              INVENTORYENTRIES.RATE,
              INVENTORYENTRIES.DISCOUNT,
              INVENTORYENTRIES.AMOUNT,
            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formulae" NAME="IsCreditNote">
            $$IsEqual:$VOUCHERTYPENAME:"Credit Note"
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

debitNote_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>DebitNoteVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>

        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="DebitNoteVouchers">
            <TYPE>VOUCHER</TYPE>

            <!-- FILTER ONLY DEBIT NOTES -->
            <FILTER>IsDebitNote</FILTER>

            <!-- IMPORTANT FIELDS -->
            <FETCH>
              DATE,
              VOUCHERNUMBER,
              VOUCHERTYPENAME,
              PARTYLEDGERNAME,
              PLACEOFSUPPLY,
              ALLINVENTORYENTRIES,
              LEDGERENTRIES,
              GSTDETAILS
            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formulae" NAME="IsDebitNote">
            $$IsEqual:$VOUCHERTYPENAME:"Debit Note"
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

sale_order_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>SalesOrderVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="SalesOrderVouchers">
            <TYPE>VOUCHER</TYPE>

            <!-- FILTER ONLY SALES ORDERS -->
            <FILTER>IsSalesOrder</FILTER>

            <!-- FETCH ALL REQUIRED FIELDS -->
            <FETCH>
              DATE,
              VOUCHERNUMBER,
              VOUCHERTYPENAME,
              PARTYLEDGERNAME,
              PLACEOFSUPPLY,
              REFERENCE,
              NARRATION,
              INVENTORYENTRIES.STOCKITEMNAME,
              INVENTORYENTRIES.BILLEDQTY,
              INVENTORYENTRIES.RATE,
              INVENTORYENTRIES.DISCOUNT,
              INVENTORYENTRIES.AMOUNT,
            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formulae" NAME="IsSalesOrder">
            $$IsEqual:$VOUCHERTYPENAME:"Sales Order"
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

purchase_order_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>PurchaseOrderVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="PurchaseOrderVouchers">
            <TYPE>VOUCHER</TYPE>

            <!-- FILTER ONLY PURCHASE ORDERS -->
            <FILTER>IsPurchaseOrder</FILTER>

            <!-- FETCH REQUIRED FIELDS -->
            <FETCH>
              DATE,
              VOUCHERNUMBER,
              VOUCHERTYPENAME,
              PARTYLEDGERNAME,
              PLACEOFSUPPLY,
              REFERENCE,
              NARRATION,
              ALLINVENTORYENTRIES,
              LEDGERENTRIES,
              GSTDETAILS
            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formulae" NAME="IsPurchaseOrder">
            $$IsEqual:$VOUCHERTYPENAME:"Purchase Order"
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

delivery_challan_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>DeliveryChallanVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="DeliveryChallanVouchers">
            <TYPE>VOUCHER</TYPE>

            <!-- FILTER ONLY DELIVERY CHALLAN -->
            <FILTER>IsDeliveryChallan</FILTER>

            <!-- FETCH REQUIRED FIELDS -->
            <FETCH>
              DATE,
              VOUCHERNUMBER,
              VOUCHERTYPENAME,
              PARTYLEDGERNAME,
              PLACEOFSUPPLY,
              REFERENCE,
              NARRATION,
              ALLINVENTORYENTRIES,
              LEDGERENTRIES,
              GSTDETAILS
            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formulae" NAME="IsDeliveryChallan">
            $$IsEqual:$VOUCHERTYPENAME:"Delivery Note"
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

receipt_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>ReceiptVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="ReceiptVouchers">
            <TYPE>VOUCHER</TYPE>
            <FILTER>IsReceipt</FILTER>
            <FETCH>
              DATE,
              VOUCHERNUMBER,
              VOUCHERTYPENAME,
              PARTYLEDGERNAME,
              ALLLEDGERENTRIES,
              LEDGERENTRIES,
              NARRATION
            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formulae" NAME="IsReceipt">
            $$IsEqual:$VOUCHERTYPENAME:"Receipt"
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

payment_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>PaymentVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="PaymentVouchers">
            <TYPE>VOUCHER</TYPE>
            <FILTER>IsPayment</FILTER>
            <FETCH>
              DATE,
              VOUCHERNUMBER,
              VOUCHERTYPENAME,
              PARTYLEDGERNAME,
              LEDGERENTRIES,
              ALLLEDGERENTRIES,
              NARRATION
            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formulae" NAME="IsPayment">
            $$IsEqual:$VOUCHERTYPENAME:"Payment"
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

contra_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>ContraVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="ContraVouchers">
            <TYPE>VOUCHER</TYPE>
            <FILTER>IsContra</FILTER>
            <FETCH>
              DATE,
              VOUCHERNUMBER,
              VOUCHERTYPENAME,
              LEDGERENTRIES,
              ALLLEDGERENTRIES,
              NARRATION
            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formulae" NAME="IsContra">
            $$IsEqual:$VOUCHERTYPENAME:"Contra"
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

stockJournal_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>StockJournalVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
        <EXPLODEFLAG>Yes</EXPLODEFLAG>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="StockJournalVouchers">
            <TYPE>VOUCHER</TYPE>

            <!-- FILTER ONLY STOCK JOURNAL -->
            <FILTER>IsStockJournal</FILTER>

            <!-- FETCH REQUIRED FIELDS -->
            <FETCH>
              DATE,
              VOUCHERNUMBER,
              VOUCHERTYPENAME,
              REFERENCE,
              NARRATION,
              INVENTORYENTRIESIN,
              INVENTORYENTRIESOUT
            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formulae" NAME="IsStockJournal">
            $$IsEqual:$VOUCHERTYPENAME:"Stock Journal"
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

journal_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>JournalVouchers</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>

          <COLLECTION NAME="JournalVouchers">
            <TYPE>VOUCHER</TYPE>

            <!-- FILTER ONLY JOURNAL VOUCHERS -->
            <FILTER>IsJournalVoucher</FILTER>

            <!-- FETCH REQUIRED FIELDS -->
            <FETCH>
              DATE,
              VOUCHERNUMBER,
              VOUCHERTYPENAME,
              REFERENCE,
              ISDEEMEDPOSITIVE,
              NARRATION,
              LEDGERENTRIES,
              GSTDETAILS
            </FETCH>
          </COLLECTION>

          <SYSTEM TYPE="Formulae" NAME="IsJournalVoucher">
            $$IsEqual:$VOUCHERTYPENAME:"Journal"
          </SYSTEM>

        </TDLMESSAGE>
      </TDL>

    </DESC>
  </BODY>
</ENVELOPE>
"""

opening_balance_tdl = """
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>EXPORT</TALLYREQUEST>
    <TYPE>COLLECTION</TYPE>
    <ID>LedgerDetails</ID>
  </HEADER>

  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
        <SVTODATE>{from_date}</SVTODATE>
      </STATICVARIABLES>

      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="LedgerDetails">
            <TYPE>LEDGER</TYPE>
            <FETCH>
              NAME,
              PARENT,
              OPENINGBALANCE,
              CLOSINGBALANCE
            </FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>
"""


# 01144444121
# 121@airtel.com
# acc no.:- 20027487151
# dsl no:- 01123655542_wifi
# leadline no.;- 01140586731



# Busy xml requests
company_details_bussy_xml = """
<REQUEST>
    <HEADER>
        <REQUESTTYPE>Get</REQUESTTYPE>
        <OBJECT>Company</OBJECT>
    </HEADER>
    <BODY>
        <FIELDS>
            <FIELD>Name</FIELD>
            <FIELD>Address1</FIELD>
            <FIELD>Address2</FIELD>
            <FIELD>Address3</FIELD>
            <FIELD>City</FIELD>
            <FIELD>State</FIELD>
            <FIELD>Country</FIELD>
            <FIELD>Pincode</FIELD>
            <FIELD>GSTIN</FIELD>
            <FIELD>PAN</FIELD>
            <FIELD>Email</FIELD>
            <FIELD>Phone</FIELD>
        </FIELDS>
    </BODY>
</REQUEST>"""

ledger_busy_xml = """
<REQUEST>
    <HEADER>
        <REQUESTTYPE>Get</REQUESTTYPE>
        <OBJECT>Account</OBJECT>
    </HEADER>
    <BODY>
        <FIELDS>
            <FIELD>Name</FIELD>
            <FIELD>Group</FIELD>
            <FIELD>Address1</FIELD>
            <FIELD>Address2</FIELD>
            <FIELD>City</FIELD>
            <FIELD>State</FIELD>
            <FIELD>Country</FIELD>
            <FIELD>Pincode</FIELD>
            <FIELD>GSTIN</FIELD>
            <FIELD>PAN</FIELD>
            <FIELD>Email</FIELD>
            <FIELD>Phone</FIELD>
            <FIELD>OpeningBalance</FIELD>
            <FIELD>DebitBalance</FIELD>
            <FIELD>CreditBalance</FIELD>
        </FIELDS>
    </BODY>
</REQUEST>"""

stocks_busy_xml = """
<REQUEST>
    <HEADER>
        <REQUESTTYPE>Get</REQUESTTYPE>
        <OBJECT>Item</OBJECT>
    </HEADER>
    <BODY>
        <FIELDS>
            <FIELD>Name</FIELD>
            <FIELD>Group</FIELD>
            <FIELD>Category</FIELD>
            <FIELD>Unit</FIELD>
            <FIELD>HSNCode</FIELD>
            <FIELD>GSTTaxRate</FIELD>
            <FIELD>OpeningQty</FIELD>
            <FIELD>OpeningValue</FIELD>
            <FIELD>ClosingQty</FIELD>
            <FIELD>ClosingValue</FIELD>
            <FIELD>PurchaseRate</FIELD>
            <FIELD>SaleRate</FIELD>
        </FIELDS>
    </BODY>
</REQUEST>"""

receipt_busy_xml = """
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
            <FIELD>Narration</FIELD>
        </FIELDS>
    </BODY>
</REQUEST>"""

stock_journal_busy_xml = """
<REQUEST>
    <HEADER>
        <REQUESTTYPE>Get</REQUESTTYPE>
        <OBJECT>Voucher</OBJECT>
    </HEADER>
    <BODY>
        <FILTERS>
            <FILTER>
                <NAME>VoucherType</NAME>
                <VALUE>Stock Journal</VALUE>
            </FILTER>
            <FILTER>
                <NAME>DateRange</NAME>
                <FROM>{from_date}</FROM>
                <TO>{to_date}</TO>
            </FILTER>
        </FILTERS>

        <!-- Voucher Level -->
        <FIELDS>
            <FIELD>Date</FIELD>
            <FIELD>VoucherNo</FIELD>
            <FIELD>Narration</FIELD>
        </FIELDS>

        <!-- Inventory Details -->
        <CHILDFIELDS>
            <CHILDFIELD>
                <NAME>InventoryEntries</NAME>
                <FIELDS>
                    <FIELD>ItemName</FIELD>
                    <FIELD>Qty</FIELD>
                    <FIELD>Unit</FIELD>
                    <FIELD>Rate</FIELD>
                    <FIELD>Amount</FIELD>
                </FIELDS>
            </CHILDFIELD>
        </CHILDFIELDS>

    </BODY>
</REQUEST>"""

