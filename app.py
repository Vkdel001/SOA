from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os
import io
import zipfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Create folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_statement_pdf(merchant_info, summary_info, start_date, end_date, output_path):
    """Generate a single PDF statement"""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Add logo at top
    logo_path = os.path.join('static', 'zwennPay.jpg')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=3*inch, height=0.6*inch)
        story.append(img)
        story.append(Spacer(1, 0.3*inch))
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#8b2f8b'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph("STATEMENT OF ACCOUNT", title_style))
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    story.append(Paragraph("Monthly Transaction Summary", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Statement Info (left aligned)
    info_data = [
        ["Statement Period:", f"{start_date} - {end_date}"],
        ["Statement Date:", datetime.now().strftime("%d %B %Y")],
        ["Account No.:", str(summary_info.get('MerchantBankAccountNo', 'N/A'))]
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 5*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#8b2f8b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Customer Details Box (without Customer ID)
    customer_data = [
        ["Customer Name:", merchant_info.get('Merchant_Name', 'N/A')],
        ["Address:", merchant_info.get('Address', 'N/A')],
        ["Contact:", f"{merchant_info.get('Contact', 'N/A')} | {merchant_info.get('Email', 'N/A')}"]
    ]
    
    customer_table = Table(customer_data, colWidths=[1.5*inch, 5*inch])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5e6f0')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#8b2f8b')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#8b2f8b')),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Transaction Summary Table
    total_transactions = float(summary_info.get('Total TransactionAmount', 0))
    total_charges = float(summary_info.get('Total TransactionCharges', 0))
    total_tax = float(summary_info.get('Total TransactionTax', 0))
    total_settled = float(summary_info.get('Total SettledAmount', 0))
    
    # Use Paragraphs for wrapping text in headers
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.whitesmoke,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=11
    )
    
    summary_data = [
        [Paragraph("Total<br/>Transactions", header_style), 
         Paragraph("Total Transaction<br/>Charges", header_style), 
         Paragraph("VAT on Transaction<br/>Charges", header_style), 
         Paragraph("Amount<br/>Credited", header_style)],
        [f"MUR {total_transactions:,.2f}", f"MUR {total_charges:,.2f}", 
         f"MUR {total_tax:,.2f}", f"MUR {total_settled:,.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[1.625*inch, 1.625*inch, 1.625*inch, 1.625*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b2f8b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, 1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#8b2f8b')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#8b2f8b')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#8b2f8b')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Statement Summary Text
    summary_text = f"""<b>Statement Summary:</b><br/>
    This statement shows the transaction activity for the period from {start_date} to {end_date}. 
    The amount credited represents the net settlement after deducting all transaction charges and 
    applicable VAT at 15% as per Mauritius tax regulations."""
    
    summary_style = ParagraphStyle(
        'SummaryText',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        spaceAfter=20
    )
    story.append(Paragraph(summary_text, summary_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Footer text
    footer_text = """This statement is issued by ZwennPay Ltd, a Payment Service Provider licensed by the 
    Bank of Mauritius (License: PSP/2023/001). For inquiries or disputes, contact us at +230 123 4567 or 
    info@zwennpay.mu. This document is confidential and intended only for the account holder."""
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
        leading=11
    )
    story.append(Paragraph(footer_text, footer_style))
    
    doc.build(story)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_statements():
    try:
        # Check if files are uploaded
        if 'master_file' not in request.files or 'summary_file' not in request.files:
            return jsonify({'error': 'Please upload both files'}), 400
        
        master_file = request.files['master_file']
        summary_file = request.files['summary_file']
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Please provide start and end dates'}), 400
        
        if master_file.filename == '' or summary_file.filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        if not (allowed_file(master_file.filename) and allowed_file(summary_file.filename)):
            return jsonify({'error': 'Only Excel files (.xlsx, .xls) are allowed'}), 400
        
        # Read Excel files using openpyxl engine for .xlsx files
        merchant_df = pd.read_excel(master_file, engine='openpyxl')
        summary_df = pd.read_excel(summary_file, engine='openpyxl')
        
        print("Master columns:", merchant_df.columns.tolist())
        print("Summary columns:", summary_df.columns.tolist())
        print("Number of merchants in summary:", len(summary_df))
        
        # Clean output folder
        for file in os.listdir(app.config['OUTPUT_FOLDER']):
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # Generate PDFs for each row in summary
        generated_files = []
        errors = []
        
        print(f"Processing {len(summary_df)} records from summary file")
        
        for idx, row in summary_df.iterrows():
            try:
                trade_name = str(row['TradeName']).strip()
                merchant = str(row['Merchant']).strip()
                
                print(f"Processing: {trade_name}")
                
                # Match TradeName from summary with Merchant_Name from master
                merchant_info = merchant_df[merchant_df['Merchant_Name'].str.strip() == trade_name]
                
                if merchant_info.empty:
                    errors.append(f"TradeName '{trade_name}' not found in master file")
                    print(f"Warning: {trade_name} not in master file")
                    continue
                
                merchant_info = merchant_info.iloc[0].to_dict()
                summary_info = row.to_dict()
                
                filename = f"SOA_{trade_name.replace(' ', '_').replace('/', '_')}_{start_date.replace(' ', '_')}_{end_date.replace(' ', '_')}.pdf"
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                
                print(f"Generating PDF: {filename}")
                generate_statement_pdf(merchant_info, summary_info, start_date, end_date, output_path)
                
                if os.path.exists(output_path):
                    generated_files.append(filename)
                    print(f"Successfully created: {filename}")
                else:
                    errors.append(f"Failed to create PDF for {trade_name}")
                    
            except Exception as e:
                error_msg = f"Error processing {trade_name}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
        
        print(f"Generated {len(generated_files)} PDFs")
        
        if not generated_files:
            error_detail = "\n".join(errors) if errors else "No PDFs were generated"
            return jsonify({'error': f'No statements generated. {error_detail}'}), 400
        
        # Create ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename in generated_files:
                file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                if os.path.exists(file_path):
                    zip_file.write(file_path, filename)
                    print(f"Added to ZIP: {filename}")
        
        zip_buffer.seek(0)
        
        print(f"ZIP file size: {len(zip_buffer.getvalue())} bytes")
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'Statements_{start_date.replace(" ", "_")}_{end_date.replace(" ", "_")}.zip'
        )
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error: {error_detail}")
        return jsonify({'error': str(e), 'detail': error_detail}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
