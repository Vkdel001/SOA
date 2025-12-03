# ZwennPay Statement of Account Generator - Web App

## Setup Instructions

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Header Image
Place `ZwennPay_header.png` in the `static` folder

### 3. Run the Web Application
```bash
python app.py
```

### 4. Access the Web App
Open your browser and go to: `http://localhost:5000`

### 5. Using the Application
1. Upload Merchant Master file (Email_master.xlsx)
2. Upload Summary file (summary.xlsx)
3. Enter start date (e.g., "01 November 2025")
4. Enter end date (e.g., "30 November 2025")
5. Click "Generate Statements"
6. Download the ZIP file containing all PDFs

## File Requirements

### Merchant Master File (Email_master.xlsx)
Columns: Merchant_Name, Email, Address, Contact

### Summary File (summary.xlsx)
Columns: TradeName, Merchant, MerchantBankAccountNo, Total TransactionAmount, Total TransactionCharges, Total TransactionTax, Total SettledAmount

## Output
- ZIP file containing individual PDF statements for each merchant
- Filename format: `SOA_MerchantName_StartDate_EndDate.pdf`
- Professional formatting with ZwennPay branding

## Notes
- Date format: DD Month YYYY (e.g., 03 December 2025)
- All amounts shown in MUR (Mauritian Rupees)
- VAT calculated at 15% as per Mauritius tax regulations
- Maximum file size: 16MB
