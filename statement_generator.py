import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
from tkinter import Tk, Label, Entry, Button, messagebox, StringVar
from tkinter import ttk
import traceback


class StatementGenerator:
    def __init__(self):
        self.merchant_master_file = "Email_master.xlsx"
        self.summary_file = "summary.xlsx"
        self.header_image = "ZwennPay_header.png"
        self.output_folder = "Statements"
        
        # Create output folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    
    def load_data(self):
        """Load merchant master and summary data"""
        try:
            self.merchant_df = pd.read_excel(self.merchant_master_file)
            self.summary_df = pd.read_excel(self.summary_file)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data files:\n{str(e)}")
            return False
    
    def generate_statement(self, merchant_name, start_date, end_date):
        """Generate PDF statement for a merchant"""
        try:
            # Get merchant details
            merchant_info = self.merchant_df[
                self.merchant_df['Merchant_Name'].str.strip() == merchant_name.strip()
            ]
            
            if merchant_info.empty:
                return False, f"Merchant '{merchant_name}' not found in master file"
            
            merchant_info = merchant_info.iloc[0]
            
            # Get transaction summary
            summary_info = self.summary_df[
                self.summary_df['Merchant'].str.strip() == merchant_name.strip()
            ]
            
            if summary_info.empty:
                return False, f"No transactions found for '{merchant_name}'"
            
            # Create PDF
            filename = f"{self.output_folder}/SOA_{merchant_name.replace(' ', '_')}_{start_date}_{end_date}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch,
                                   leftMargin=0.75*inch, rightMargin=0.75*inch)
            
            story = []
            styles = getSampleStyleSheet()
            
            # Add header image if exists
            if os.path.exists(self.header_image):
                img = Image(self.header_image, width=7*inch, height=1.5*inch)
                story.append(img)
                story.append(Spacer(1, 0.3*inch))
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a4d7a'),
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
            
            # Company and Statement Info
            info_data = [
                ["ZwennPay Ltd", "Statement Period:", f"{start_date} - {end_date}"],
                ["Port Louis, Mauritius", "Statement Date:", datetime.now().strftime("%d %B %Y")],
                ["PSP License: Bank of Mauritius", "Account No.:", summary_info.iloc[0]['MerchantBankAccountNo']]
            ]
            
            info_table = Table(info_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a4d7a')),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Customer Details Box
            customer_data = [
                ["Customer Name:", merchant_info['Merchant_Name']],
                ["Customer ID:", summary_info.iloc[0]['TradeName']],
                ["Address:", merchant_info.get('Address', 'N/A')],
                ["Contact:", f"{merchant_info.get('Contact', 'N/A')} | {merchant_info.get('Email', 'N/A')}"]
            ]
            
            customer_table = Table(customer_data, colWidths=[1.5*inch, 5*inch])
            customer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f0f7')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a4d7a')),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1a4d7a')),
            ]))
            story.append(customer_table)
            story.append(Spacer(1, 0.3*inch))

            # Transaction Summary Table
            total_transactions = summary_info['Total TransactionAmount'].sum()
            total_charges = summary_info['Total TransactionCharges'].sum()
            total_tax = summary_info['Total TransactionTax'].sum()
            total_settled = summary_info['Total SettledAmount'].sum()
            
            summary_data = [
                ["Total Transactions", "Total Transaction Charges", "VAT on Transaction Charges", "Amount Credited"],
                [f"MUR {total_transactions:,.2f}", f"MUR {total_charges:,.2f}", 
                 f"MUR {total_tax:,.2f}", f"MUR {total_settled:,.2f}"]
            ]
            
            summary_table = Table(summary_data, colWidths=[1.625*inch, 1.625*inch, 1.625*inch, 1.625*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a4d7a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 1), (-1, 1), colors.white),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, 1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1a4d7a')),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1a4d7a')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1a4d7a')),
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
            story.append(Spacer(1, 0.2*inch))
            
            # Footer
            footer_text = """This statement is issued by ZwennPay Ltd, a Payment Service Provider licensed by the 
            Bank of Mauritius (License: PSP/2023/001). For inquiries or disputes, contact us at +230 123 4567 or 
            info@zwennpay.mu. This document is confidential and intended only for the account holder."""
            
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=7,
                textColor=colors.grey,
                alignment=TA_CENTER,
                leading=10
            )
            story.append(Paragraph(footer_text, footer_style))
            
            # Build PDF
            doc.build(story)
            
            return True, filename
            
        except Exception as e:
            return False, f"Error generating statement: {str(e)}\n{traceback.format_exc()}"
    
    def generate_all_statements(self, start_date, end_date):
        """Generate statements for all merchants"""
        if not self.load_data():
            return
        
        success_count = 0
        failed_merchants = []
        
        unique_merchants = self.summary_df['Merchant'].unique()
        
        for merchant in unique_merchants:
            success, result = self.generate_statement(merchant, start_date, end_date)
            if success:
                success_count += 1
            else:
                failed_merchants.append(f"{merchant}: {result}")
        
        # Show results
        message = f"Successfully generated {success_count} statement(s)\n"
        message += f"Saved in folder: {self.output_folder}\n\n"
        
        if failed_merchants:
            message += "Failed merchants:\n" + "\n".join(failed_merchants)
        
        messagebox.showinfo("Generation Complete", message)


class StatementGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ZwennPay - Statement of Account Generator")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        self.generator = StatementGenerator()
        
        # Title
        title_label = Label(root, text="Statement of Account Generator", 
                           font=("Arial", 16, "bold"), fg="#1a4d7a")
        title_label.pack(pady=20)
        
        # Frame for inputs
        input_frame = ttk.Frame(root, padding="20")
        input_frame.pack(fill="both", expand=True)
        
        # Start Date
        Label(input_frame, text="Start Date:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=10)
        self.start_date_var = StringVar()
        self.start_date_entry = Entry(input_frame, textvariable=self.start_date_var, 
                                      font=("Arial", 11), width=25)
        self.start_date_entry.grid(row=0, column=1, pady=10, padx=10)
        self.start_date_entry.insert(0, "01 November 2025")
        
        # End Date
        Label(input_frame, text="End Date:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=10)
        self.end_date_var = StringVar()
        self.end_date_entry = Entry(input_frame, textvariable=self.end_date_var, 
                                    font=("Arial", 11), width=25)
        self.end_date_entry.grid(row=1, column=1, pady=10, padx=10)
        self.end_date_entry.insert(0, "30 November 2025")
        
        # Info label
        info_label = Label(input_frame, text="Format: DD Month YYYY (e.g., 01 November 2025)", 
                          font=("Arial", 9), fg="gray")
        info_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Generate Button
        generate_btn = Button(root, text="Generate All Statements", 
                             command=self.generate_statements,
                             font=("Arial", 12, "bold"), 
                             bg="#8b2f8b", fg="white",
                             padx=20, pady=10,
                             cursor="hand2")
        generate_btn.pack(pady=20)
        
        # Status label
        self.status_label = Label(root, text="", font=("Arial", 9), fg="green")
        self.status_label.pack()
    
    def generate_statements(self):
        start_date = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()
        
        if not start_date or not end_date:
            messagebox.showerror("Error", "Please enter both start and end dates")
            return
        
        self.status_label.config(text="Generating statements...", fg="blue")
        self.root.update()
        
        try:
            self.generator.generate_all_statements(start_date, end_date)
            self.status_label.config(text="Generation complete!", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate statements:\n{str(e)}")
            self.status_label.config(text="Generation failed", fg="red")


def main():
    root = Tk()
    app = StatementGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
