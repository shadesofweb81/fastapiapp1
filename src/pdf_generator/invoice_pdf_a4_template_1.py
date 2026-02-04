"""
Invoice PDF Generator - Template 1 (Busy Style)
A4 paper size with classic Busy software layout - Fixed positions matching Sales-44.html
"""
import os
import re
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfgen import canvas


class InvoicePDFTemplate1Generator:
    """Generate professional invoice PDFs with Busy-style template for A4 paper - Fixed positions"""
    
    def __init__(self):
        self.page_size = A4
        self.page_width, self.page_height = self.page_size
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.currency_symbol = '₹'
        self.currency_map = {
            'INR': '₹',
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'AUD': 'A$',
            'CAD': 'C$'
        }
        # Fixed margin for outer border (8mm from page edge)
        self.outer_margin = 8*mm
        self.content_width = self.page_width - (2 * self.outer_margin)
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for Busy-style template"""
        # GSTIN style (top left - bold)
        self.styles.add(ParagraphStyle(
            name='GSTINStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Copy type style (top right - regular)
        self.styles.add(ParagraphStyle(
            name='CopyType',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))
        
        # Document type style (TAX INVOICE - bold centered)
        self.styles.add(ParagraphStyle(
            name='DocType',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Company name style (large, centered, bold)
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=0,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Company address style (centered)
        self.styles.add(ParagraphStyle(
            name='CompanyAddress',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section header style (e.g., "Party Details :")
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica-BoldOblique'
        ))
        
        # Label style
        self.styles.add(ParagraphStyle(
            name='Label',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica'
        ))
        
        # Value style
        self.styles.add(ParagraphStyle(
            name='Value',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica'
        ))
        
        # Bold value style
        self.styles.add(ParagraphStyle(
            name='ValueBold',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Table header style
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        # Table cell style
        self.styles.add(ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica'
        ))
        
        # Italic style for tax labels
        self.styles.add(ParagraphStyle(
            name='ItalicLabel',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica-Oblique'
        ))
        
        # Small style for footer/tax summary
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=6,
            textColor=colors.black,
            fontName='Helvetica'
        ))
        
        # Small bold style
        self.styles.add(ParagraphStyle(
            name='SmallTextBold',
            parent=self.styles['Normal'],
            fontSize=6,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Signature style
        self.styles.add(ParagraphStyle(
            name='Signature',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT
        ))
        
        # Bank details style
        self.styles.add(ParagraphStyle(
            name='BankDetails',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica'
        ))
        
        # Terms header
        self.styles.add(ParagraphStyle(
            name='TermsHeader',
            parent=self.styles['Normal'],
            fontSize=6,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Terms text
        self.styles.add(ParagraphStyle(
            name='TermsText',
            parent=self.styles['Normal'],
            fontSize=6,
            textColor=colors.black,
            fontName='Helvetica'
        ))
        
        # Table cell center
        self.styles.add(ParagraphStyle(
            name='TableCellCenter',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=TA_CENTER
        ))
        
        # Table cell right
        self.styles.add(ParagraphStyle(
            name='TableCellRight',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=TA_RIGHT
        ))
    
    def generate_invoice_pdf(self, data, options, preview=False):
        """
        Generate invoice PDF with Busy-style template
        
        Args:
            data: Dictionary containing invoice data
            options: Dictionary containing print options
            preview: If True, generate single copy for preview
            
        Returns:
            Path to generated PDF file
        """
        try:
            transaction_header = data.get('transactionHeader', {})
            invoice_num = transaction_header.get('invoiceNumber') or data.get('invoiceNumber', 'invoice')
            # Sanitize invoice number - replace invalid chars and spaces with underscores
            safe_invoice_num = re.sub(r'[\\/:*?"<>|\s]+', '_', str(invoice_num)).strip('_')

            if preview:
                output_dir = Path(os.environ.get('TEMP', '/tmp'))
                filename = f"preview_{safe_invoice_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            elif options.get('save_file'):
                output_dir = Path(options.get('save_location'))
                filename = options.get('filename', f"{safe_invoice_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                # Sanitize the provided filename as well
                filename = re.sub(r'[\\/:*?"<>|\s]+', '_', str(filename)).strip('_')
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
            else:
                output_dir = Path(os.environ.get('TEMP', '/tmp'))
                filename = f"{safe_invoice_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / filename
            
            # Set currency symbol
            company = data.get('company', {})
            currency_symbol = company.get('currencySymbol') or company.get('currency_symbol')
            currency_code = company.get('currencyCode') or company.get('currency')
            
            if currency_symbol:
                self.currency_symbol = currency_symbol
            elif currency_code and currency_code in self.currency_map:
                self.currency_symbol = self.currency_map[currency_code]
            else:
                self.currency_symbol = '₹'
            
            # Fixed footer heights (drawn on canvas)
            self.terms_footer_height = 22*mm
            self.bank_details_height = 14*mm
            # Bottom margin must clear the fixed footer area
            bottom_margin = self.outer_margin + self.terms_footer_height + self.bank_details_height + 2*mm

            # Margins for A4
            margins = {'right': self.outer_margin, 'left': self.outer_margin,
                      'top': self.outer_margin + 2*mm, 'bottom': bottom_margin}

            company_name = company.get('name') or company.get('companyName', 'Company')
            pdf_title = f"Invoice {invoice_num} - {company_name}"

            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=margins['right'],
                leftMargin=margins['left'],
                topMargin=margins['top'],
                bottomMargin=margins['bottom'],
                title=pdf_title,
                author=company_name,
                subject=f"Invoice {invoice_num}"
            )
            
            if preview:
                copy_types = ["Original Copy"]
                num_copies = 1
            else:
                copy_types = options.get('copy_types', ["Original Copy"])
                num_copies = options.get('num_copies', 1)

            story = []
            self.footer_data = data

            page_count = 0
            for _ in range(num_copies):
                for copy_type in copy_types:
                    if page_count > 0:
                        story.append(PageBreak())
                    story.extend(self._build_invoice_content(data, copy_type))
                    page_count += 1
            
            doc.build(story, onFirstPage=self._add_page_border, onLaterPages=self._add_page_border)
            
            return str(output_path)
        
        except Exception as e:
            print(f"Error generating invoice PDF: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _build_invoice_content(self, data, copy_type):
        """Build invoice content for one copy"""
        content = []
        
        # Row 1: GSTIN left | Copy type right
        content.extend(self._build_header_row(data, copy_type))
        content.append(Spacer(1, 2*mm))
        
        # Row 2: TAX INVOICE centered
        content.extend(self._build_doc_type_row(data))
        content.append(Spacer(1, 1*mm))
        
        # Row 3: Company name and address centered
        content.extend(self._build_company_row(data))
        content.append(Spacer(1, 3*mm))
        
        # Row 4: Party Details (left) | Invoice Details (right) - with border
        content.extend(self._build_party_invoice_row(data))
        
        # Row 5: GSTIN/UIN - with border
        content.extend(self._build_party_gstin_row(data))
        
        # Row 6: Items table with header - with border
        content.extend(self._build_items_table(data))
        
        # Row 7: Subtotal row
        content.extend(self._build_subtotal_row(data))
        
        # Row 8: Tax additions (SGST, CGST)
        content.extend(self._build_tax_additions(data))
        
        # Row 9: Grand Total row
        content.extend(self._build_grand_total_row(data))
        
        # Row 10: Tax summary table
        content.extend(self._build_tax_summary_table(data))
        
        # Row 11: Amount in words
        content.extend(self._build_amount_in_words(data))
        # Footer (Terms, Receiver's Signature, Authorised Signatory) is drawn
        # at fixed page bottom position by _add_page_border
        
        return content
    
    def _build_header_row(self, data, copy_type):
        """Build header row with GSTIN left and copy type right"""
        content = []
        company = data.get('company', {})
        gstin = company.get('gstin') or company.get('taxId', '')
        
        gstin_text = f"GSTIN : {gstin}" if gstin else ""
        
        header_data = [[
            Paragraph(gstin_text, self.styles['GSTINStyle']),
            Paragraph(copy_type, self.styles['CopyType'])
        ]]
        
        header_table = Table(header_data, colWidths=[self.content_width * 0.6, self.content_width * 0.4])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        content.append(header_table)
        return content
    
    def _build_doc_type_row(self, data):
        """Build document type row (TAX INVOICE)"""
        content = []
        transaction_header = data.get('transactionHeader', {})
        trans_type = transaction_header.get('type', '')
        
        if data.get('documentTitle'):
            doc_title = data.get('documentTitle')
        elif 'sale' in trans_type.lower() or 'invoice' in trans_type.lower():
            doc_title = 'TAX INVOICE'
        elif 'purchase' in trans_type.lower():
            doc_title = 'PURCHASE BILL'
        else:
            doc_title = 'TAX INVOICE'
        
        content.append(Paragraph(doc_title, self.styles['DocType']))
        return content
    
    def _build_company_row(self, data):
        """Build company name and address row"""
        content = []
        company = data.get('company', {})
        company_name = company.get('name') or company.get('companyName', 'Company Name')
        
        # Company name
        content.append(Paragraph(company_name.upper(), self.styles['CompanyName']))
        
        # Company address
        address_parts = []
        address = company.get('address', '')
        if address:
            address_parts.append(address)
        
        city = company.get('city', '')
        state = company.get('state', '')
        pincode = company.get('pincode') or company.get('zipCode', '')
        
        location = ' '.join(filter(None, [city, state, pincode]))
        if location:
            address_parts.append(location)
        
        if address_parts:
            content.append(Paragraph(', '.join(address_parts), self.styles['CompanyAddress']))
        
        return content
    
    def _build_party_invoice_row(self, data):
        """Build party details (left) and invoice details (right) with border"""
        content = []
        
        transaction_header = data.get('transactionHeader', data)
        party_data = data.get('party', {})
        
        left_width = self.content_width * 0.50
        right_width = self.content_width * 0.50
        
        # Left side - Party Details
        party_name = party_data.get('name') or data.get('partyName', 'N/A')
        billing_address = party_data.get('billingAddress', party_data)
        
        party_lines = [party_name]
        
        address = billing_address.get('address', '')
        if address:
            party_lines.append(address)
        
        city = billing_address.get('city', '')
        state = billing_address.get('state', '')
        if city:
            party_lines.append(city)
        if state:
            party_lines.append(state)
        
        left_content = [[Paragraph("<i>Party Details :</i>", self.styles['SectionHeader'])]]
        for line in party_lines:
            left_content.append([Paragraph(line, self.styles['Value'])])
        
        # Pad to minimum rows
        while len(left_content) < 5:
            left_content.append([Paragraph("", self.styles['Value'])])
        
        left_table = Table(left_content, colWidths=[left_width - 6])
        left_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        
        # Right side - Invoice Details
        invoice_no = transaction_header.get('invoiceNumber') or data.get('invoiceNumber', 'N/A')
        trans_date = transaction_header.get('transactionDate') or data.get('transactionDate', '')
        place_of_supply = transaction_header.get('placeOfSupply') or data.get('placeOfSupply', '')
        state_code = party_data.get('stateCode') or billing_address.get('stateCode', '')
        reverse_charge = transaction_header.get('reverseCharge', 'N')
        
        if place_of_supply and state_code:
            place_of_supply = f"{place_of_supply} ({state_code})"
        
        label_width = 28*mm
        value_width = right_width - label_width - 6
        
        right_content = [
            [Paragraph("Invoice No.", self.styles['Label']), 
             Paragraph(f": {invoice_no}", self.styles['Value'])],
            [Paragraph("Dated", self.styles['Label']), 
             Paragraph(f": {self._format_date_short(trans_date)}", self.styles['Value'])],
            [Paragraph("Place of Supply", self.styles['Label']), 
             Paragraph(f": {place_of_supply}" if place_of_supply else ": ", self.styles['Value'])],
            [Paragraph("Reverse Charge", self.styles['Label']), 
             Paragraph(f": {reverse_charge}", self.styles['Value'])]
        ]
        
        right_table = Table(right_content, colWidths=[label_width, value_width])
        right_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        
        # Combine with border
        main_table = Table([[left_table, right_table]], colWidths=[left_width, right_width])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBEFORE', (1, 0), (1, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        content.append(main_table)
        return content
    
    def _build_party_gstin_row(self, data):
        """Build party GSTIN/UIN row with border"""
        content = []
        party_data = data.get('party', {})
        party_gstin = party_data.get('taxId') or party_data.get('gstin', '')
        
        gstin_data = [[
            Paragraph("GSTIN / UIN", self.styles['Label']),
            Paragraph(f": {party_gstin}" if party_gstin else ": ", self.styles['Value'])
        ]]
        
        gstin_table = Table(gstin_data, colWidths=[25*mm, self.content_width - 25*mm])
        gstin_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        content.append(gstin_table)
        return content
    
    def _build_items_table(self, data):
        """Build items table with fixed column widths"""
        content = []
        
        # Column widths: S.N, Description, HSN/SAC Code, Qty, Unit, Price, Amount(₹)
        col_widths = [
            self.content_width * 0.06,   # S.N
            self.content_width * 0.34,   # Description
            self.content_width * 0.10,   # HSN/SAC Code
            self.content_width * 0.10,   # Qty
            self.content_width * 0.08,   # Unit
            self.content_width * 0.12,   # Price
            self.content_width * 0.20,   # Amount
        ]
        
        # Table header (two rows for HSN/SAC Code)
        header_row = [
            Paragraph('<b>S.N.</b>', self.styles['TableHeader']),
            Paragraph('<b>Description of Goods</b>', self.styles['TableHeader']),
            Paragraph('<b>HSN/SAC<br/>Code</b>', self.styles['TableHeader']),
            Paragraph('<b>Qty.</b>', self.styles['TableHeader']),
            Paragraph('<b>Unit</b>', self.styles['TableHeader']),
            Paragraph('<b>Price</b>', self.styles['TableHeader']),
            Paragraph(f'<b>Amount({self.currency_symbol})</b>', self.styles['TableHeader'])
        ]
        
        table_data = [header_row]
        
        # Items rows
        items = data.get('items', [])
        total_qty = 0
        default_unit = 'Pcs'
        
        for idx, item in enumerate(items, 1):
            serial_no = item.get('serialNumber') if item.get('serialNumber') else idx
            description = item.get('description') or item.get('productName', '')
            hsn_code = item.get('hsnCode', '')
            quantity = float(item.get('quantity', 0) or 0)
            unit = item.get('unit') or item.get('unitName', default_unit)
            unit_price = float(item.get('unitPrice', 0) or 0)
            line_total = float(item.get('lineTotal', 0) or 0)
            
            total_qty += quantity
            if unit:
                default_unit = unit
            
            table_data.append([
                Paragraph(f"{serial_no}.", self.styles['TableCellCenter']),
                Paragraph(description, self.styles['TableCell']),
                Paragraph(hsn_code, self.styles['TableCellCenter']),
                Paragraph(f"{quantity:.2f}", self.styles['TableCellRight']),
                Paragraph(unit, self.styles['TableCellCenter']),
                Paragraph(f"{unit_price:,.2f}", self.styles['TableCellRight']),
                Paragraph(f"{line_total:,.2f}", self.styles['TableCellRight'])
            ])
        
        # Add empty rows to fill minimum space (for fixed layout)
        min_rows = 12
        while len(table_data) < min_rows:
            table_data.append(['', '', '', '', '', '', ''])
        
        items_table = Table(table_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            # Header styling
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            
            # Data rows styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            
            # Borders
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEBEFORE', (1, 0), (1, -1), 0.5, colors.black),
            ('LINEBEFORE', (2, 0), (2, -1), 0.5, colors.black),
            ('LINEBEFORE', (3, 0), (3, -1), 0.5, colors.black),
            ('LINEBEFORE', (4, 0), (4, -1), 0.5, colors.black),
            ('LINEBEFORE', (5, 0), (5, -1), 0.5, colors.black),
            ('LINEBEFORE', (6, 0), (6, -1), 0.5, colors.black),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 1), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
        ]))
        
        content.append(items_table)
        
        # Store values for later use
        self._total_qty = total_qty
        self._default_unit = default_unit
        
        return content
    
    def _build_subtotal_row(self, data):
        """Build subtotal row"""
        content = []
        summary = data.get('summary', data)
        subtotal = float(summary.get('subTotal', 0) or 0)
        
        col_widths = [
            self.content_width * 0.80,
            self.content_width * 0.20,
        ]
        
        subtotal_data = [[
            Paragraph('', self.styles['TableCell']),
            Paragraph(f"<b>{subtotal:,.2f}</b>", self.styles['TableCellRight'])
        ]]
        
        subtotal_table = Table(subtotal_data, colWidths=col_widths)
        subtotal_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBEFORE', (1, 0), (1, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        content.append(subtotal_table)
        return content
    
    def _build_tax_additions(self, data):
        """Build tax additions section (SGST, CGST with @ rate)"""
        content = []
        summary = data.get('summary', data)
        
        tax_rows = []
        
        # Get tax components
        tax_components_summary = summary.get('taxComponentsSummary', [])
        
        if tax_components_summary:
            for comp in tax_components_summary:
                comp_name = comp.get('componentName', '')
                rate = float(comp.get('rate', 0) or 0)
                amount = float(comp.get('amount', 0) or 0)
                
                if amount > 0:
                    rate_str = f"@ {rate:.2f}%" if rate > 0 else ""
                    tax_rows.append([
                        Paragraph(f"Add", self.styles['ItalicLabel']),
                        Paragraph(f": {comp_name} {rate_str}", self.styles['ItalicLabel']),
                        Paragraph("", self.styles['TableCell']),
                        Paragraph(f"{amount:,.2f}", self.styles['TableCellRight'])
                    ])
        else:
            # Fall back to taxes array
            taxes = data.get('taxes', [])
            for tax in taxes:
                components = tax.get('components', [])
                for comp in components:
                    comp_name = comp.get('componentName', '')
                    rate = float(comp.get('rate', 0) or 0)
                    amount = float(comp.get('amount', 0) or 0)
                    
                    if amount > 0:
                        rate_str = f"@ {rate:.2f}%" if rate > 0 else ""
                        tax_rows.append([
                            Paragraph(f"Add", self.styles['ItalicLabel']),
                            Paragraph(f": {comp_name} {rate_str}", self.styles['ItalicLabel']),
                            Paragraph("", self.styles['TableCell']),
                            Paragraph(f"{amount:,.2f}", self.styles['TableCellRight'])
                        ])
        
        # Round off
        roundoff = float(summary.get('roundOff', 0) or 0)
        if roundoff != 0:
            sign = "(+)" if roundoff > 0 else "(-)"
            tax_rows.append([
                Paragraph(f"Add", self.styles['ItalicLabel']),
                Paragraph(f": Rounded Off {sign}", self.styles['ItalicLabel']),
                Paragraph("", self.styles['TableCell']),
                Paragraph(f"{abs(roundoff):,.2f}", self.styles['TableCellRight'])
            ])
        
        if tax_rows:
            col_widths = [
                self.content_width * 0.10,
                self.content_width * 0.50,
                self.content_width * 0.20,
                self.content_width * 0.20,
            ]
            
            tax_table = Table(tax_rows, colWidths=col_widths)
            tax_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
                ('LINEBEFORE', (3, 0), (3, -1), 0.5, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            
            content.append(tax_table)
        
        return content
    
    def _build_grand_total_row(self, data):
        """Build grand total row with qty and unit"""
        content = []
        
        summary = data.get('summary', data)
        total = float(summary.get('total', 0) or 0)
        total_qty = getattr(self, '_total_qty', 0)
        default_unit = getattr(self, '_default_unit', 'Pcs')
        
        col_widths = [
            self.content_width * 0.40,
            self.content_width * 0.20,
            self.content_width * 0.20,
            self.content_width * 0.20,
        ]
        
        grand_total_data = [[
            Paragraph('<b>Grand Total</b>', self.styles['ValueBold']),
            Paragraph(f"<b>{total_qty:,.2f} {default_unit}</b>", self.styles['TableCellCenter']),
            Paragraph(f"<b>{self.currency_symbol}</b>", self.styles['TableCellCenter']),
            Paragraph(f"<b>{total:,.2f}</b>", self.styles['TableCellRight'])
        ]]
        
        total_table = Table(grand_total_data, colWidths=col_widths)
        total_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBEFORE', (3, 0), (3, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ]))
        
        content.append(total_table)
        return content
    
    def _build_tax_summary_table(self, data):
        """Build tax summary table (HSN/SAC, Tax Rate, Taxable Amt., CGST, SGST, Total Tax)"""
        content = []
        
        summary = data.get('summary', data)
        subtotal = float(summary.get('subTotal', 0) or 0)
        
        # Header row
        header_row = [
            Paragraph('<b>HSN/SAC</b>', self.styles['SmallTextBold']),
            Paragraph('<b>Tax Rate</b>', self.styles['SmallTextBold']),
            Paragraph('<b>Taxable Amt.</b>', self.styles['SmallTextBold']),
            Paragraph('<b>CGST</b>', self.styles['SmallTextBold']),
            Paragraph('<b>SGST</b>', self.styles['SmallTextBold']),
            Paragraph('<b>Total Tax</b>', self.styles['SmallTextBold'])
        ]
        
        table_data = [header_row]
        
        # Get HSN codes from items
        items = data.get('items', [])
        hsn_codes = set()
        for item in items:
            hsn = item.get('hsnCode', '')
            if hsn:
                hsn_codes.add(hsn)
        
        hsn_str = ', '.join(hsn_codes) if hsn_codes else ''
        
        # Build tax summary from components
        tax_components_summary = summary.get('taxComponentsSummary', [])
        
        # Group by rate
        cgst_total = 0
        sgst_total = 0
        igst_total = 0
        total_rate = 0
        
        for comp in tax_components_summary:
            comp_type = comp.get('componentType', '').upper()
            comp_name = comp.get('componentName', '').upper()
            rate = float(comp.get('rate', 0) or 0)
            amount = float(comp.get('amount', 0) or 0)
            
            if 'CGST' in comp_type or 'CGST' in comp_name:
                cgst_total += amount
                total_rate += rate
            elif 'SGST' in comp_type or 'SGST' in comp_name:
                sgst_total += amount
                total_rate += rate
            elif 'IGST' in comp_type or 'IGST' in comp_name:
                igst_total += amount
                total_rate += rate
        
        total_tax = cgst_total + sgst_total + igst_total
        
        # Data row
        rate_str = f"{total_rate:.0f}%" if total_rate > 0 else "0%"
        
        table_data.append([
            Paragraph(hsn_str, self.styles['SmallText']),
            Paragraph(rate_str, self.styles['SmallText']),
            Paragraph(f"{subtotal:,.2f}", self.styles['SmallText']),
            Paragraph(f"{cgst_total:,.2f}" if cgst_total else "0.00", self.styles['SmallText']),
            Paragraph(f"{sgst_total:,.2f}" if sgst_total else "0.00", self.styles['SmallText']),
            Paragraph(f"{total_tax:,.2f}", self.styles['SmallText'])
        ])
        
        col_widths = [self.content_width * 0.15, self.content_width * 0.12, self.content_width * 0.18, 
                      self.content_width * 0.18, self.content_width * 0.18, self.content_width * 0.19]
        
        tax_summary_table = Table(table_data, colWidths=col_widths)
        tax_summary_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEBEFORE', (1, 0), (1, -1), 0.5, colors.black),
            ('LINEBEFORE', (2, 0), (2, -1), 0.5, colors.black),
            ('LINEBEFORE', (3, 0), (3, -1), 0.5, colors.black),
            ('LINEBEFORE', (4, 0), (4, -1), 0.5, colors.black),
            ('LINEBEFORE', (5, 0), (5, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        content.append(tax_summary_table)
        return content
    
    def _build_amount_in_words(self, data):
        """Build amount in words row"""
        content = []
        
        summary = data.get('summary', data)
        total = float(summary.get('total', 0) or 0)
        amount_in_words = self._number_to_words(total)
        
        words_para = Paragraph(f"<b>Rupees {amount_in_words} Only</b>", self.styles['ValueBold'])
        content.append(words_para)
        
        return content
    
    def _build_footer_section(self, data):
        """Build footer at bottom with terms (left), receiver's signature (center), authorised signatory (right)"""
        content = []
        
        company = data.get('company', {})
        company_name = company.get('name') or company.get('companyName', 'Company Name')
        
        # Get terms from data
        terms_list = data.get('termsAndConditions', [])
        if not terms_list:
            terms_text = data.get('terms', '')
            if terms_text:
                terms_list = [terms_text]
        
        # Default terms if none provided - exact format as specified
        if not terms_list:
            terms_list = [
                "E.& O.E.",
                "1. Goods once sold will not be taken back.",
                "2. Interest @ 18% p.a. will be charged if the payment",
                "    is not made with in the stipulated time.",
                "3. Subject to local Jurisdiction only."
            ]
        
        left_width = self.content_width * 0.40
        center_width = self.content_width * 0.30
        right_width = self.content_width * 0.30
        
        # Left - Terms & Conditions
        left_content = [[Paragraph('<b>Terms &amp; Conditions</b>', self.styles['TermsHeader'])]]
        for term in terms_list[:6]:  # Allow up to 6 terms
            left_content.append([Paragraph(term, self.styles['TermsText'])])
        
        left_table = Table(left_content, colWidths=[left_width - 6])
        left_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        
        # Center - Receiver's Signature
        center_content = [
            [Paragraph("<b>Receiver's Signature :</b>", self.styles['SmallTextBold'])],
            [Spacer(1, 18*mm)]
        ]
        center_table = Table(center_content, colWidths=[center_width - 6])
        center_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        # Right - for Company Name / Authorised Signatory
        right_content = [
            [Paragraph(f"<b>for {company_name.upper()}</b>", self.styles['Signature'])],
            [Spacer(1, 15*mm)],
            [Paragraph("<b>Authorised Signatory</b>", self.styles['Signature'])]
        ]
        right_table = Table(right_content, colWidths=[right_width - 6])
        right_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        # Combine all three columns with borders
        footer_table = Table([[left_table, center_table, right_table]], 
                            colWidths=[left_width, center_width, right_width])
        footer_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBEFORE', (1, 0), (1, -1), 0.5, colors.black),
            ('LINEBEFORE', (2, 0), (2, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        content.append(footer_table)
        return content
    
    def _format_date_short(self, date_str):
        """Format date string in DD-MM-YYYY format"""
        if not date_str:
            return 'N/A'
        
        try:
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%Y')
        except:
            return date_str
    
    def _number_to_words(self, num):
        """Convert a number to words (Indian numbering system)"""
        if num == 0:
            return "Zero"
        
        num = round(num, 2)
        int_part = int(num)
        dec_part = int(round((num - int_part) * 100))
        
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
                'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
                'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        def two_digits(n):
            if n < 20:
                return ones[n]
            else:
                return tens[n // 10] + ('' if n % 10 == 0 else ' ' + ones[n % 10])
        
        def three_digits(n):
            if n < 100:
                return two_digits(n)
            else:
                return ones[n // 100] + ' Hundred' + ('' if n % 100 == 0 else ' ' + two_digits(n % 100))
        
        result = ''
        
        if int_part >= 10000000:
            crore = int_part // 10000000
            result += three_digits(crore) + ' Crore '
            int_part %= 10000000
        
        if int_part >= 100000:
            lakh = int_part // 100000
            result += two_digits(lakh) + ' Lakh '
            int_part %= 100000
        
        if int_part >= 1000:
            thousand = int_part // 1000
            result += two_digits(thousand) + ' Thousand '
            int_part %= 1000
        
        if int_part > 0:
            result += three_digits(int_part)
        
        result = result.strip()
        
        if dec_part > 0:
            result += ' and ' + two_digits(dec_part) + ' Paise'
        
        return result if result else 'Zero'
    
    def _add_page_border(self, canvas_obj, doc):
        """Add outer page border, bank details row, footer signatures, and page number"""
        page_num = canvas_obj.getPageNumber()

        # Get company data for footer
        company_name = "Company Name"
        company = {}
        if hasattr(self, 'footer_data') and self.footer_data:
            company = self.footer_data.get('company', {})
            company_name = company.get('name') or company.get('companyName', 'Company Name')

        terms_height = getattr(self, 'terms_footer_height', 22*mm)
        bank_height = getattr(self, 'bank_details_height', 14*mm)

        # Terms/Signature footer - bottom aligned with page border
        footer_y = self.outer_margin
        # Bank details row - sits directly above terms footer
        bank_y = footer_y + terms_height

        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setLineWidth(0.5)

        # --- Bank Details Row (horizontal layout across full width) ---
        canvas_obj.rect(self.outer_margin, bank_y, self.content_width, bank_height)

        left_x = self.outer_margin + 3

        bank_name = company.get('bankName', '')
        account_number = company.get('accountNumber', '')
        ifsc_code = company.get('ifscCode', '')
        account_holder = company.get('accountHolderName', '')
        branch_name = company.get('branchName', '')

        canvas_obj.setFillColor(colors.black)

        # Row 1: "Bank Details :" header label + Bank Name + Branch
        row1_y = bank_y + bank_height - 5*mm
        canvas_obj.setFont('Helvetica-Bold', 7)
        canvas_obj.drawString(left_x, row1_y, "Bank Details :")

        col2_x = self.outer_margin + self.content_width * 0.18
        col3_x = self.outer_margin + self.content_width * 0.52
        col4_x = self.outer_margin + self.content_width * 0.75

        canvas_obj.setFont('Helvetica', 7)
        canvas_obj.drawString(col2_x, row1_y, f"Bank : {bank_name}")
        canvas_obj.drawString(col3_x, row1_y, f"Branch : {branch_name}")
        canvas_obj.drawString(col4_x, row1_y, f"A/c Holder : {account_holder}")

        # Row 2: A/c No + IFSC Code
        row2_y = bank_y + bank_height - 10*mm
        canvas_obj.drawString(col2_x, row2_y, f"A/c No. : {account_number}")
        canvas_obj.drawString(col3_x, row2_y, f"IFSC Code : {ifsc_code}")

        # --- Terms & Signature Footer Row ---
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.rect(self.outer_margin, footer_y, self.content_width, terms_height)

        # Column positions
        left_width = self.content_width * 0.40
        center_x = self.outer_margin + left_width
        center_width = self.content_width * 0.30
        right_x = self.outer_margin + left_width + center_width

        # Vertical dividers
        canvas_obj.line(center_x, footer_y, center_x, footer_y + terms_height)
        canvas_obj.line(right_x, footer_y, right_x, footer_y + terms_height)

        # Left section - Terms & Conditions
        canvas_obj.setFont('Helvetica-Bold', 7)
        canvas_obj.setFillColor(colors.black)
        canvas_obj.drawString(left_x, footer_y + 19*mm, "Terms & Conditions")

        # Use company terms if provided, otherwise defaults
        company_terms = company.get('termsAndConditions', '')
        if company_terms:
            # Split long terms text into lines
            terms = [line.strip() for line in company_terms.split('\n') if line.strip()]
        else:
            # Check data-level terms
            data_terms = self.footer_data.get('termsAndConditions', []) if hasattr(self, 'footer_data') and self.footer_data else []
            if data_terms:
                terms = data_terms if isinstance(data_terms, list) else [data_terms]
            else:
                terms = [
                    "E.& O.E.",
                    "1. Goods once sold will not be taken back.",
                    "2. Interest @ 18% p.a. will be charged if the",
                    "    payment is not made with in the stipulated time.",
                    "3. Subject to local Jurisdiction only."
                ]

        canvas_obj.setFont('Helvetica', 6)
        y_offset = 15*mm
        for term in terms[:6]:
            canvas_obj.drawString(left_x, footer_y + y_offset, term)
            y_offset -= 3*mm

        # Center section - Receiver's Signature
        canvas_obj.setFont('Helvetica-Bold', 7)
        canvas_obj.setFillColor(colors.black)
        text_width = canvas_obj.stringWidth("Receiver's Signature :", 'Helvetica-Bold', 7)
        center_text_x = center_x + (center_width - text_width) / 2
        canvas_obj.drawString(center_text_x, footer_y + 19*mm, "Receiver's Signature :")

        # Right section - Authorised Signatory
        canvas_obj.setFont('Helvetica-Bold', 7)
        for_company_text = f"for {company_name.upper()}"
        canvas_obj.drawRightString(self.outer_margin + self.content_width - 3, footer_y + 19*mm, for_company_text)

        auth_sig_text = "Authorised Signatory"
        canvas_obj.drawRightString(self.outer_margin + self.content_width - 3, footer_y + 3*mm, auth_sig_text)

        # Page number at bottom right (below footer)
        text = f"Page {page_num}"
        canvas_obj.setFont('Helvetica', 7)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawRightString(self.page_width - 10*mm, 4*mm, text)

        # Draw outer border at 8mm margin from page edges
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.rect(
            self.outer_margin,
            self.outer_margin,
            self.page_width - 2*self.outer_margin,
            self.page_height - 2*self.outer_margin
        )


def generate_invoice_pdf_template_1(data, options, preview=False):
    """
    Wrapper function to generate invoice PDF with Template 1 (Busy style)
    
    Args:
        data: Invoice data dictionary
        options: Print options dictionary
        preview: Boolean indicating preview mode
        
    Returns:
        Path to generated PDF file
    """
    generator = InvoicePDFTemplate1Generator()
    return generator.generate_invoice_pdf(data, options, preview)
