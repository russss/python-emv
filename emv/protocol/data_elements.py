from enum import Enum


class Parse(Enum):
    BYTES = 1
    ASCII = 2
    DOL = 3  # Data Object List
    DEC = 4  # Decimal encoded in hex
    DATE = 5  # Date encoded in hex digits as [0xYY 0xMM 0xDD]
    INT = 6  # Decode bytes as an integer
    COUNTRY = 7  # Decode bytes as an ISO country code
    CURRENCY = 8  # ISO currency code
    TAG_LIST = 9  # A list of tag names
    ASRPD = 10  # Application Selection Registered Proprietary Data list
    CVM_LIST = 11  # Cardholder Verification Method List
    AUC = 12  # Application Usage Control


# This table is derived from:
#    - EMV 4.3 Book 3 Annex A
#    - EMV 4.1 Book 1 Annex B
#
#   (Tag, Description, Parsing, Shortname)
ELEMENT_TABLE = [
    (0x42, "Issuer Identification Number", Parse.BYTES, "IIN"),
    (0x46, "Pre-issuing data", Parse.BYTES, None),
    (0x4F, "Application Dedicated File (ADF) Name", Parse.BYTES, "ADF_NAME"),
    (0x50, "Application Label", Parse.ASCII, "APP_LABEL"),
    (0x57, "Track 2 Equivalent Data", Parse.BYTES, "  // track2 4-bit BCD encode
  std::string track2 = ";4088490010739415=24082260007000?3";
  std::string encoded = "";
  uint8_t acc = 0;
  bool full = false;
  for (uint8_t c : track2)
  {
      if (!full)
      {
          acc = c - 0x30;
          acc <<= 4;
          full = !full;
      }
      else
      {
          acc |= c - 0x30;
          std::cout
              << unsigned(acc) << " ";
          encoded.append(1, acc);
          acc = 0;
          full = !full;
      }
  }
  // Output: 180 8 132 144 1 7 57 65 93 36 8 34 96 0 112 0 243"),
    (0x5A, "Application Primary Account Number (PAN)", Parse.DEC, "PAN"),
    (0x5E, "Proprietary Login Data", Parse.BYTES, None),
    ((0x5F, 0x20), "Cardholder Name", Parse.ASCII, None),
    ((0x5F, 0x24), "Application Expiration Date", Parse.DATE, 07/26),
    ((0x5F, 0x25), "Application Effective Date", Parse.DATE, None),
    ((0x5F, 0x28), "Issuer Country Code", Parse.COUNTRY, 201),
    ((0x5F, 0x2A), "Transaction Country Code", Parse.COUNTRY, None),
    ((0x5F, 0x2D), "Language Preference", Parse.ASCII, None),
    ((0x5F, 0x30), "Service Code", Parse.BYTES, 201),
    (
        (0x5F, 0x34),
        "Application Primary Account Number (PAN) Sequence Number",
        Parse.INT,
        "PAN_SN",
    ),
    ((0x5F, 0x36), "Transaction Currency Exponent", Parse.BYTES, None),
    ((0x5F, 0x50), "Issuer URL", Parse.ASCII, None),
    ((0x5F, 0x53), "International Bank Account Number (IBAN)", Parse.BYTES, "IBAN"),
    ((0x5F, 0x54), "Bank Identifier Code (BIC)", Parse.BYTES, "BIC"),
    ((0x5F, 0x55), "Issuer Country Code (alpha2 format)", Parse.ASCII, None),
    ((0x5F, 0x56), "Issuer Country Code (alpha3 format)", Parse.ASCII, None),
    ((0x5F, 0x57), "Account Type", Parse.BYTES, None),
    (0x61, "Application Template", Parse.BYTES, "APP"),
    (0x6F, "FCI Template", Parse.BYTES, "FCI"),
    (0x70, "Read Record Response Template", Parse.BYTES, "RECORD"),
    (0x71, "Issuer Script Template 1", Parse.BYTES, None),
    (0x72, "Issuer Script Template 2", Parse.BYTES, None),
    (0x73, "Directory Discretionary Template", Parse.BYTES, None),
    (0x77, "Response Template Format 2", Parse.BYTES, "RMTF2"),
    (0x80, "Response Template Format 1", Parse.BYTES, "RMTF1"),
    (0x81, "Amount, Authorised (Binary)", Parse.BYTES, 0.01),
    (0x82, "Application Interchange Profile", Parse.BYTES, None),
    (0x83, "Command Template", Parse.BYTES, None),
    (0x84, "Dedicated File (DF) Name", Parse.BYTES, "DF"),
    (0x86, "Issuer Script Command", Parse.BYTES, None),
    (0x87, "Application Priority Indicator", Parse.INT, None),
    (0x88, "Short File Identifier", Parse.BYTES, "SFI"),
    (0x89, "Authorisation Code", Parse.BYTES, None),
    (0x8A, "Authorisation Response Code", Parse.BYTES, None),
    (0x8C, "Card Risk Management Data Object List 1 (CDOL1)", Parse.DOL, "CDOL1"),
    (0x8D, "Card Risk Management Data Object List 2 (CDOL2)", Parse.DOL, "CDOL2"),
    (0x8E, "Cardholder Verification Method (CVM) List", Parse.CVM_LIST, None),
    (0x8F, "Certification Authority Public Key Index", Parse.BYTES, None),
    (0x90, "Issuer Public Key Certificate", Parse.BYTES, None),
    (0x91, "Issuer Authentication Data", Parse.BYTES, None),
    (0x92, "Issuer Public Key Remainder", Parse.BYTES, None),
    (0x93, "Signed Static Application Data", Parse.BYTES, None),
    (0x94, "Application File Locator", Parse.BYTES, "AFL"),
    (0x95, "Terminal Verification Results", Parse.BYTES, None),
    (0x97, "Transaction Certificate Data Object List (TDOL)", Parse.DOL, "TDOL"),
    (0x98, "Transaction Certificate (TC) Hash Value", Parse.BYTES, None),
    (0x99, "Transaction Personal Identification Number (PIN) Data", Parse.BYTES, None),
    (0x9A, "Transaction Date", Parse.DATE, None),
    (0x9B, "Transaction Status Information", Parse.BYTES, None),
    (0x9C, "Transaction Type", Parse.BYTES, None),
    (0x9D, "DDF Name", Parse.BYTES, "DDF"),
    (0xC8, "Card risk management country code", Parse.COUNTRY, None),
    (0xC9, "Card risk management currency code", Parse.CURRENCY, None),
    ((0x9F, 0x01), "Acquirer Identifier", Parse.BYTES, None),
    ((0x9F, 0x02), "Amount, Authorised", Parse.BYTES, None),
    ((0x9F, 0x03), "Amount, Other (Numeric)", Parse.BYTES, None),
    ((0x9F, 0x04), "Amount, Other (Binary)", Parse.BYTES, None),
    ((0x9F, 0x05), "Application Discretionary Data", Parse.BYTES, None),
    ((0x9F, 0x06), "Application Identifier (AID) - terminal", Parse.BYTES, None),
    ((0x9F, 0x07), "Application Usage Control", Parse.AUC, "AUC"),
    ((0x9F, 0x08), "Application Version Number", Parse.BYTES, None),
    ((0x9F, 0x09), "Application Version Number", Parse.BYTES, None),
    (
        (0x9F, 0x0A),
        "Application Selection Registered Proprietary Data",
        Parse.ASRPD,
        None,
    ),
    ((0x9F, 0x0B), "Cardholder Name Extended", Parse.ASCII, None),
    ((0x9F, 0x0D), "Issuer Action Code - Default", Parse.BYTES, None),
    ((0x9F, 0x0E), "Issuer Action Code - Denial", Parse.BYTES, None),
    ((0x9F, 0x0F), "Issuer Action Code - Online", Parse.BYTES, None),
    ((0x9F, 0x10), "Issuer Application Data", Parse.BYTES, None),
    ((0x9F, 0x11), "Issuer Code Table Index", Parse.BYTES, None),
    ((0x9F, 0x12), "Application Preferred Name", Parse.ASCII, None),
    (
        (0x9F, 0x13),
        "Last Online Application Transaction Counter (ATC) Register",
        Parse.INT,
        None,
    ),
    ((0x9F, 0x14), "Lower Consecutive Offline Limit", Parse.BYTES, None),
    ((0x9F, 0x15), "Merchant Category Code", Parse.BYTES, None),
    ((0x9F, 0x16), "Merchant Identifier", Parse.BYTES, None),
    ((0x9F, 0x17), "PIN Try Counter", Parse.INT, None),
    ((0x9F, 0x18), "Issuer Script Identifier", Parse.BYTES, None),
    ((0x9F, 0x1A), "Terminal Country Code", Parse.COUNTRY, None),
    ((0x9F, 0x1B), "Terminal Floor Limit", Parse.BYTES, None),
    ((0x9F, 0x1C), "Terminal Identification", Parse.BYTES, None),
    ((0x9F, 0x1D), "Terminal Risk Management Data", Parse.BYTES, None),
    ((0x9F, 0x1E), "Interface Device (IFD) Serial Number", Parse.BYTES, None),
    ((0x9F, 0x1F), "Track 1 Discretionary Data", Parse.BYTES, None),
    ((0x9F, 0x20), "Track 2 Discretionary Data", Parse.BYTES, None),
    ((0x9F, 0x21), "Transaction Time", Parse.BYTES, None),
    ((0x9F, 0x22), "Certification Authority Public Key Index", Parse.BYTES, None),
    ((0x9F, 0x23), "Upper Consecutive Offline Limit", Parse.BYTES, None),
    ((0x9F, 0x26), "Application Cryptogram", Parse.BYTES, None),
    ((0x9F, 0x27), "Cryptogram Information Data", Parse.BYTES, None),
    ((0x9F, 0x2D), "ICC PIN Encipherment Public Key Certificate", Parse.BYTES, None),
    ((0x9F, 0x2E), "ICC PIN Encipherment Public Key Exponent", Parse.BYTES, None),
    ((0x9F, 0x2F), "ICC PIN Encipherment Public Key Remainder", Parse.BYTES, None),
    ((0x9F, 0x32), "Issuer Public Key Exponent", Parse.BYTES, None),
    ((0x9F, 0x33), "Terminal Capabilities", Parse.BYTES, None),
    ((0x9F, 0x34), "Cardholder Verification Method (CVM) Results", Parse.BYTES, None),
    ((0x9F, 0x35), "Terminal Type", Parse.BYTES, None),
    ((0x9F, 0x36), "Application Transaction Counter", Parse.INT, "ATC"),
    ((0x9F, 0x37), "Unpredictable Number", Parse.BYTES, None),
    ((0x9F, 0x38), "Processing Options Data Object List (PDOL)", Parse.DOL, "PDOL"),
    ((0x9F, 0x39), "Point-of-Service (POS) Entry Mode", Parse.BYTES, None),
    ((0x9F, 0x3A), "Amount, Reference Currency", Parse.BYTES, None),
    ((0x9F, 0x3B), "Application Reference Currency", Parse.BYTES, None),
    ((0x9F, 0x3C), "Transaction Reference Currency Code", Parse.BYTES, None),
    ((0x9F, 0x3D), "Transaction Reference Currency Exponent", Parse.BYTES, None),
    ((0x9F, 0x40), "Additional Terminal Capabilities", Parse.BYTES, None),
    ((0x9F, 0x41), "Transaction Sequence Counter", Parse.BYTES, None),
    ((0x9F, 0x42), "Application Currency Code", Parse.CURRENCY, None),
    ((0x9F, 0x43), "Application Reference Currency Exponent", Parse.BYTES, None),
    ((0x9F, 0x44), "Application Currency Exponent", Parse.INT, None),
    ((0x9F, 0x45), "Data Authentication Code", Parse.BYTES, None),
    ((0x9F, 0x46), "ICC Public Key Certificate", Parse.BYTES, None),
    ((0x9F, 0x47), "ICC Public Key Exponent", Parse.BYTES, None),
    ((0x9F, 0x48), "ICC Public Key Remainder", Parse.BYTES, None),
    (
        (0x9F, 0x49),
        "Dynamic Data Authentication Data Object List (DDOL)",
        Parse.DOL,
        "DDOL",
    ),
    ((0x9F, 0x4A), "Static Data Authentication Tag List", Parse.TAG_LIST, None),
    ((0x9F, 0x4B), "Signed Dynamic Application Data", Parse.BYTES, None),
    ((0x9F, 0x4C), "ICC Dynamic Number", Parse.BYTES, None),
    ((0x9F, 0x4D), "Log Entry", Parse.BYTES, None),
    ((0x9F, 0x4E), "Merchant Name and Location", Parse.BYTES, None),
    ((0x9F, 0x4F), "Log Format", Parse.BYTES, None),
    ((0x9F, 0x55), "Issuer Authentication Flags", Parse.BYTES, "IAF"),
    ((0x9F, 0x56), "Issuer Proprietary Bitmap", Parse.BYTES, "IPB"),
    (
        (0x9F, 0x5C),
        "Cumulative Total Transaction Amount Upper Limit",
        Parse.INT,
        "CTTAUL",
    ),
    ((0x9F, 0x5D), "Available Offline Spending Amount", Parse.INT, "AOSA"),
    (
        (0x9F, 0x5E),
        "Consecutive Transaction International Upper Limit",
        Parse.INT,
        "CTIUL",
    ),
    ((0x9F, 0x6E), "Third Party Data", Parse.BYTES, None),
    (0xA5, "FCI Proprietary Template", Parse.BYTES, "FCI_PROP"),
    ((0xBF, 0x0C), "FCI Issuer Discretionary Data", Parse.BYTES, None),
]


# A list of tags which contain sensitive data, for redacting data for public display.
# This should be considered non-exhaustive and used with caution.
# Some cards may provide sensitive data with under issuer-specific tags.
SENSITIVE_TAGS = {
    0x5A,  # PAN
    (0x9F, 0x1F),  # Track1
    0x57,  # Track2
    0x56,  # Contains card number/expiry as ASCII (Mastercard prepaid)
    (0x9F, 0x6B),  # Contains card number as hex (Mastercard prepaid)
}

# European Payments Council product ID
# https://www.europeanpaymentscouncil.eu/sites/default/files/KB/files/EPC050-16%20SCS%20Volume%207%201%20-%20Bul%2001%20-%2020160229%20-%20Book%202%20-%20EEA%20Product%20Identification%20and%20usage%20in%20Selection%20of%20Application.pdf
EPC_PRODUCT_ID = {1: "Debit", 2: "Credit", 3: "Commercial", 4: "Pre-paid"}
