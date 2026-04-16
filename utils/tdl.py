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

ledger_group_tdl = ""

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

combined_fetch_tdl = """
  <ENVELOPE>
    <HEADER>
      <VERSION>1</VERSION>
      <TALLYREQUEST>EXPORT</TALLYREQUEST>
      <TYPE>COLLECTION</TYPE>
      <ID>CombinedData</ID>
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

            <!-- 🔹 GROUPS -->
            <COLLECTION NAME="GroupCollection">
              <TYPE>GROUP</TYPE>
              <FETCH>NAME, PARENT</FETCH>
            </COLLECTION>

            <!-- 🔹 LEDGERS -->
            <COLLECTION NAME="LedgerCollection">
              <TYPE>LEDGER</TYPE>
              <FETCH>NAME, PARENT</FETCH>
            </COLLECTION>

            <!-- 🔹 JOURNALS -->
            <COLLECTION NAME="JournalCollection">
              <TYPE>VOUCHER</TYPE>
              <CHILDOF>Journal</CHILDOF>
              <FILTER>IsJournalVoucher</FILTER>
              <FETCH>
                DATE,
                VOUCHERNUMBER,
                VOUCHERTYPENAME,
                NARRATION,
                ALLLEDGERENTRIES.LIST
              </FETCH>
            </COLLECTION>
            <SYSTEM TYPE="Formula" NAME="IsJournalVoucher">
              $$IsEqual:$VOUCHERTYPENAME:"Journal"
            </SYSTEM>

            <!-- ✅ FINAL COMBINED COLLECTION -->
            <COLLECTION NAME="CombinedData">
              <COLLECTION>GroupCollection</COLLECTION>
              <COLLECTION>LedgerCollection</COLLECTION>
              <COLLECTION>JournalCollection</COLLECTION>
            </COLLECTION>

          </TDLMESSAGE>
        </TDL>

      </DESC>
    </BODY>
  </ENVELOPE>
"""
