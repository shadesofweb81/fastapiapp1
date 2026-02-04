"""
Invoice PDF Generator A5 - Generate professional invoice PDFs for A5 paper using ReportLab
This implementation matches the exact design from 1-1.html template
"""
import os
import re
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5, A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepInFrame, KeepTogether, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.pdfgen import canvas


class InvoicePDFA5Generator:
    """Generate professional invoice PDFs for A5 paper size - matching 1-1.html design"""
    
    def __init__(self):
        self.page_size = A4
        self.page_width, self.page_height = self.page_size
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.currency_symbol = '₹'  # Default currency symbol (Rupee)
        # Currency symbol mappings for better display
        self.currency_map = {
            'INR': '₹',
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'AUD': 'A$',
            'CAD': 'C$'
        }
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for A5 paper size matching 1-1.html"""
        # Company name style - Bold, larger
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=0,
            spaceBefore=0,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        # Bold text style
        self.styles.add(ParagraphStyle(
            name='BoldText',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0,
            fontName='Helvetica-Bold'
        ))
        
        # Document title style - TAX INVOICE - centered bold
        self.styles.add(ParagraphStyle(
            name='DocumentTitle',
            parent=self.styles['Heading1'],
            fontSize=9,
            textColor=colors.black,
            spaceAfter=0,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Copy type style (Original Copy) - italic right aligned
        self.styles.add(ParagraphStyle(
            name='CopyType',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.black,
            alignment=TA_RIGHT,
            fontName='Helvetica-Oblique'
        ))
        
        # GSTIN style - left aligned
        self.styles.add(ParagraphStyle(
            name='GSTINStyle',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        # Table header style - small
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=5,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Table cell style
        self.styles.add(ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=5,
            textColor=colors.black,
            alignment=TA_LEFT
        ))
        
        # Table cell right aligned
        self.styles.add(ParagraphStyle(
            name='TableCellRight',
            parent=self.styles['Normal'],
            fontSize=5,
            textColor=colors.black,
            alignment=TA_RIGHT
        ))
        
        # Italic style for Add rows
        self.styles.add(ParagraphStyle(
            name='ItalicText',
            parent=self.styles['Normal'],
            fontSize=5,
            textColor=colors.black,
            alignment=TA_RIGHT,
            fontName='Helvetica-Oblique'
        ))
        
        # Grand Total style
        self.styles.add(ParagraphStyle(
            name='GrandTotal',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.black,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
        
        # Footer signature style - italic
        self.styles.add(ParagraphStyle(
            name='FooterSignature',
            parent=self.styles['Normal'],
            fontSize=6,
            textColor=colors.black,
            alignment=TA_LEFT,
            fontName='Helvetica-Oblique'
        ))
    
    def generate_invoice_pdf(self, data, options, preview=False):
        """
        Generate invoice PDF for A5 paper
        
        Args:
            data: Dictionary containing invoice data
            options: Dictionary containing print options
            preview: If True, generate single copy for preview
            
        Returns:
            Path to generated PDF file
        """
        try:
            # Get invoice number from either location
            transaction_header = data.get('transactionHeader', {})
            invoice_num = transaction_header.get('invoiceNumber') or data.get('invoiceNumber', 'invoice')

            # Sanitize invoice number for use in filename (remove invalid characters)
            safe_invoice_num = re.sub(r'[\\/:*?"<>|]', '_', str(invoice_num))

            # Determine output path
            if preview:
                output_dir = Path(os.environ.get('TEMP', '/tmp'))
                filename = f"preview_a5_{safe_invoice_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            elif options.get('save_file'):
                output_dir = Path(options.get('save_location'))
                filename = options.get('filename')
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
            else:
                output_dir = Path(os.environ.get('TEMP', '/tmp'))
                filename = f"{safe_invoice_num}_a5_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            output_path = output_dir / filename
            
            # Set currency symbol from company data
            company = data.get('company', {})
            currency_symbol = company.get('currencySymbol') or company.get('currency_symbol')
            currency_code = company.get('currencyCode') or company.get('currency')
            
            # Try to get symbol, then map currency code, then default
            if currency_symbol:
                self.currency_symbol = currency_symbol
            elif currency_code and currency_code in self.currency_map:
                self.currency_symbol = self.currency_map[currency_code]
            else:
                self.currency_symbol = '₹'  # Default fallback
            
            # A4 margins - force content to top half (A5 Landscape area on A4)
            # A4 Height = 297mm. Half = ~148.5mm. Using 150mm bottom margin allows roughly 145mm height.
            margins = {'right': 2*mm, 'left': 2*mm, 'top': 4*mm, 'bottom': 155*mm}

            # Create PDF title for metadata
            company_name = company.get('name') or company.get('companyName', 'Company')
            pdf_title = f"Invoice {invoice_num} - {company_name}"

            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=self.page_size,
                rightMargin=margins['right'],
                leftMargin=margins['left'],
                topMargin=margins['top'],
                bottomMargin=margins['bottom'],
                title=pdf_title,
                author=company_name,
                subject=f"Invoice {invoice_num}"
            )
            
            # Determine which copy types to generate
            if preview:
                copy_types = ["ORIGINAL"]
                num_copies = 1
            else:
                copy_types = options.get('copy_types', ["ORIGINAL"])
                num_copies = options.get('num_copies', 1)

            # Build PDF content
            story = []

            # Store data for footer drawing
            self.footer_data = data

            # Generate copies: repeat the copy_types pattern num_copies times
            page_count = 0
            for _ in range(num_copies):
                for copy_type in copy_types:
                    if page_count > 0:
                        # Add page break between all pages except the first
                        story.append(PageBreak())

                    # Build content for this copy
                    story.extend(self._build_invoice_content(data, copy_type))
                    page_count += 1
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_page_elements, onLaterPages=self._add_page_elements)
            
            return str(output_path)
        
        except Exception as e:
            print(f"Error generating A5 invoice PDF: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _build_invoice_content(self, data, copy_type):
        """Build invoice content for one copy - matching 1-1.html layout"""
        content = []
        content_width = self.page_width - 4*mm  # Account for 2mm margins on each side
        
        # Map copy type to display text
        copy_type_map = {
            "ORIGINAL": "Original Copy",
            "DUPLICATE": "Duplicate Copy",
            "TRIPLICATE": "Triplicate Copy"
        }
        copy_display = copy_type_map.get(copy_type, f"{copy_type} Copy")
        
        # Get company data
        company = data.get('company', {})
        company_gstin = company.get('gstin') or company.get('taxId', '')
        
        # Row 1: GSTIN | TAX INVOICE | Copy Type
        row1_data = [[
            Paragraph(f"GSTIN : {company_gstin}", self.styles['GSTINStyle']),
            Paragraph("TAX INVOICE", self.styles['DocumentTitle']),
            Paragraph(copy_display, self.styles['CopyType'])
        ]]
        row1_table = Table(row1_data, colWidths=[content_width*0.35, content_width*0.30, content_width*0.35])
        row1_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            # Horizontal line below the TAX INVOICE header
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ]))
        content.append(row1_table)
        content.append(Spacer(1, 0.5*mm))
        
        # Row 2: Company details (left) | Billed to (right)
        content.extend(self._build_company_and_party_section(data))
        content.append(Spacer(1, 1*mm))

        # Row 3: Invoice No | Dated | Place of Supply
        content.extend(self._build_invoice_details_row(data))
        content.append(Spacer(1, 1*mm))
        
        # Items table with tax columns
        content.extend(self._build_items_table(data))
        content.append(Spacer(1, 0.5*mm))

        # Tax addition rows (Add: SGST, Add: CGST, Add: Rounded Off)
        content.extend(self._build_tax_addition_rows(data))
        content.append(Spacer(1, 0.5*mm))

        # Grand Total row
        content.extend(self._build_grand_total_row(data))
        content.append(Spacer(1, 1*mm))
        
        # Tax Summary table
        content.extend(self._build_tax_summary_table(data))
        return content
    
    def _build_company_and_party_section(self, data):
        """Build company and party details side by side"""
        content = []
        content_width = self.page_width - 4*mm
        
        company = data.get('company', {})
        party_data = data.get('party', {})
        
        # Left side - Company details
        company_name = company.get('name') or company.get('companyName', 'Company Name')
        phone = company.get('phone') or company.get('phoneNumber', '')
        email = company.get('email', '')
        
        left_content = []
        left_content.append(Paragraph(f"<b>{company_name}</b>", self.styles['CompanyName']))
        if phone or email:
            tel_email = f"Tel./Email : {phone} / {email}" if phone and email else f"Tel./Email : {phone}{email}"
            left_content.append(Paragraph(tel_email, self.styles['NormalText']))
        
        # Right side - Billed to details
        party_name = party_data.get('name') or data.get('partyName', 'N/A')
        billing_address = party_data.get('billingAddress', party_data)
        address = billing_address.get('address', '')
        city = billing_address.get('city', '')
        state = billing_address.get('state', '')
        party_gstin = party_data.get('taxId') or party_data.get('gstin', '')
        
        # Build address string
        address_parts = []
        if address:
            address_parts.append(address)
        if city:
            address_parts.append(city)
        address_str = ', '.join(address_parts) if address_parts else ''
        
        right_content = []
        right_content.append(Paragraph(f"<b>Billed to :</b>  {party_name}", self.styles['BoldText']))
        if address_str:
            right_content.append(Paragraph(f"<b>Address :</b>  {address_str}", self.styles['NormalText']))
        if party_gstin:
            right_content.append(Paragraph(f"<b>GSTIN :</b>  {party_gstin}", self.styles['NormalText']))
        
        # Create two column layout
        left_table = Table([[cell] for cell in left_content], colWidths=[content_width*0.45])
        left_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        right_table = Table([[cell] for cell in right_content], colWidths=[content_width*0.50])
        right_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        main_table = Table([[left_table, right_table]], colWidths=[content_width*0.45, content_width*0.55])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            # Vertical line separating company and billed-to sections
            ('LINEAFTER', (0, 0), (0, -1), 0.5, colors.black),
        ]))
        content.append(main_table)
        
        return content
    
    def _build_invoice_details_row(self, data):
        """Build Invoice No | Dated | Place of Supply row"""
        content = []
        content_width = self.page_width - 4*mm
        
        transaction_header = data.get('transactionHeader', data)
        
        invoice_no = transaction_header.get('invoiceNumber') or data.get('invoiceNumber', 'N/A')
        trans_date = transaction_header.get('transactionDate') or data.get('transactionDate', '')
        place_of_supply = transaction_header.get('placeOfSupply') or data.get('placeOfSupply', '')
        state_code = transaction_header.get('stateCode') or data.get('stateCode', '')
        
        formatted_date = self._format_date_time(trans_date)
        
        # Place of supply with state code
        pos_display = place_of_supply
        if state_code:
            pos_display = f"{place_of_supply} ({state_code})" if place_of_supply else f"({state_code})"
        
        row_data = [[
            Paragraph(f"<b>Invoice No.</b>  : {invoice_no}", self.styles['BoldText']),
            Paragraph(f"<b>Dated</b>  : {formatted_date}", self.styles['BoldText']),
            Paragraph(f"<b>Place of Supply</b>  : {pos_display}", self.styles['BoldText'])
        ]]
        
        row_table = Table(row_data, colWidths=[content_width*0.30, content_width*0.35, content_width*0.35])
        row_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        content.append(row_table)
        
        return content
    
    def _build_items_table(self, data):
        """Build items table with tax columns matching 1-1.html"""
        content = []
        content_width = self.page_width - 4*mm
        
        # Table header matching 1-1.html:
        # S.N. | Goods/Services supplied | HSN/SAC | Qty. | Unit | List Price | CGST (%) | CGST Amt. | SGST (%) | SGST Amt. | Amount(₹)
        header_row = [
            Paragraph('S.N.', self.styles['TableHeader']),
            Paragraph('Goods / Services supplied', self.styles['TableHeader']),
            Paragraph('HSN/SAC', self.styles['TableHeader']),
            Paragraph('Qty.', self.styles['TableHeader']),
            Paragraph('Unit', self.styles['TableHeader']),
            Paragraph('List Price', self.styles['TableHeader']),
            Paragraph('CGST (%)', self.styles['TableHeader']),
            Paragraph('CGST Amt.', self.styles['TableHeader']),
            Paragraph('SGST (%)', self.styles['TableHeader']),
            Paragraph('SGST Amt.', self.styles['TableHeader']),
            Paragraph(f'Amount({self.currency_symbol})', self.styles['TableHeader'])
        ]
        
        table_data = [header_row]
        
        # Items rows
        items = data.get('items', [])
        for idx, item in enumerate(items, 1):
            serial_no = item.get('serialNumber') if item.get('serialNumber') else idx
            description = item.get('description') or item.get('productName', '')
            hsn_code = item.get('hsnCode', '')
            quantity = float(item.get('quantity', 0) or 0)
            unit = item.get('unit') or item.get('unitName', '')
            unit_price = float(item.get('unitPrice', 0) or 0)
            line_total = float(item.get('lineTotal', 0) or 0)
            
            # Tax details from item
            cgst_rate = float(item.get('cgstRate', 0) or item.get('cgst', 0) or 0)
            cgst_amount = float(item.get('cgstAmount', 0) or 0)
            sgst_rate = float(item.get('sgstRate', 0) or item.get('sgst', 0) or 0)
            sgst_amount = float(item.get('sgstAmount', 0) or 0)
            
            # If no separate tax amounts, calculate from rates if available
            if cgst_amount == 0 and cgst_rate > 0:
                taxable_value = float(item.get('taxableValue', 0) or line_total or 0)
                cgst_amount = taxable_value * cgst_rate / 100
            if sgst_amount == 0 and sgst_rate > 0:
                taxable_value = float(item.get('taxableValue', 0) or line_total or 0)
                sgst_amount = taxable_value * sgst_rate / 100

            qty_display = f"{quantity:.2f}" if quantity != int(quantity) else f"{int(quantity)}.00"
            
            table_data.append([
                Paragraph(str(serial_no), self.styles['TableCell']),
                Paragraph(description, self.styles['TableCell']),
                Paragraph(str(hsn_code), self.styles['TableCell']),
                Paragraph(qty_display, self.styles['TableCellRight']),
                Paragraph(str(unit), self.styles['TableCell']),
                Paragraph(f"{unit_price:,.2f}", self.styles['TableCellRight']),
                Paragraph(f"{cgst_rate:.2f} %", self.styles['TableCellRight']),
                Paragraph(f"{cgst_amount:,.2f}", self.styles['TableCellRight']),
                Paragraph(f"{sgst_rate:.2f} %", self.styles['TableCellRight']),
                Paragraph(f"{sgst_amount:,.2f}", self.styles['TableCellRight']),
                Paragraph(f"{line_total:,.2f}", self.styles['TableCellRight'])
            ])
        
        # Pad with empty rows to ensure fixed height (minimum 12 item rows)
        min_rows = 12
        empty_row = ['', '', '', '', '', '', '', '', '', '', '']
        while len(table_data) - 1 < min_rows:  # -1 for header row
            table_data.append(empty_row)

        # Column widths proportional to content
        col_widths = [
            content_width * 0.04,   # S.N.
            content_width * 0.22,   # Goods/Services
            content_width * 0.08,   # HSN/SAC
            content_width * 0.08,   # Qty
            content_width * 0.05,   # Unit
            content_width * 0.10,   # List Price
            content_width * 0.08,   # CGST %
            content_width * 0.09,   # CGST Amt
            content_width * 0.08,   # SGST %
            content_width * 0.08,   # SGST Amt
            content_width * 0.10    # Amount
        ]

        # Fixed row heights: header + data rows
        item_row_height = 3.5*mm
        row_heights = [4*mm] + [item_row_height] * (len(table_data) - 1)

        items_table = Table(table_data, colWidths=col_widths, rowHeights=row_heights)
        
        items_table.setStyle(TableStyle([
            # Header row styling
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 5),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            
            # Data rows styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 5),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # S.N. center
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Numbers right aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Borders
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEAFTER', (0, 0), (-2, -1), 0.25, colors.grey),
            ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.grey),
            
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        content.append(items_table)
        
        return content
    
    def _build_tax_addition_rows(self, data):
        """Build Add: SGST, Add: CGST, Add: Rounded Off rows"""
        content = []
        content_width = self.page_width - 4*mm
        
        summary = data.get('summary', data)
        
        # Get tax totals
        total_sgst = 0
        total_cgst = 0
        sgst_rate = 0
        cgst_rate = 0
        
        # Try to get from taxComponentsSummary
        tax_components_summary = summary.get('taxComponentsSummary', [])
        for comp in tax_components_summary:
            tax_type = comp.get('taxType', '').upper()
            amount = float(comp.get('amount', 0) or 0)
            rate = float(comp.get('rate', 0) or 0)
            if 'SGST' in tax_type:
                total_sgst += amount
                sgst_rate = rate
            elif 'CGST' in tax_type:
                total_cgst += amount
                cgst_rate = rate
        
        # If not found, try from taxes array
        if total_sgst == 0 and total_cgst == 0:
            taxes = data.get('taxes', [])
            for tax in taxes:
                tax_type = tax.get('taxType', '').upper()
                amount = float(tax.get('taxAmount') or tax.get('amount', 0) or 0)
                rate = float(tax.get('rate', 0) or 0)
                if 'SGST' in tax_type:
                    total_sgst += amount
                    sgst_rate = rate
                elif 'CGST' in tax_type:
                    total_cgst += amount
                    cgst_rate = rate
        
        # Calculate from items if still not found
        if total_sgst == 0 and total_cgst == 0:
            items = data.get('items', [])
            for item in items:
                cgst_amount = float(item.get('cgstAmount', 0) or 0)
                sgst_amount = float(item.get('sgstAmount', 0) or 0)
                total_cgst += cgst_amount
                total_sgst += sgst_amount
                if cgst_rate == 0:
                    cgst_rate = float(item.get('cgstRate', 0) or item.get('cgst', 0) or 0)
                if sgst_rate == 0:
                    sgst_rate = float(item.get('sgstRate', 0) or item.get('sgst', 0) or 0)
        
        # Round off amount
        round_off = float(summary.get('roundOff', 0) or 0)
        round_off_sign = "(+)" if round_off >= 0 else "(-)"
        
        # Build addition rows - spacer + label + amount
        add_rows_data = [
            ['', Paragraph(f"<i>Add : SGST @ {sgst_rate:.2f} %</i>", self.styles['ItalicText']),
             Paragraph(f"{total_sgst:,.2f}", self.styles['TableCellRight'])],
            ['', Paragraph(f"<i>Add : CGST @ {cgst_rate:.2f} %</i>", self.styles['ItalicText']),
             Paragraph(f"{total_cgst:,.2f}", self.styles['TableCellRight'])],
            ['', Paragraph(f"<i>Add : Rounded Off {round_off_sign}</i>", self.styles['ItalicText']),
             Paragraph(f"{abs(round_off):,.2f}", self.styles['TableCellRight'])]
        ]

        # Three columns: spacer, label and amount, with more horizontal space
        col_widths = [content_width * 0.50, content_width * 0.30, content_width * 0.20]

        # Row heights with some breathing room
        row_heights = [2.5*mm, 2.5*mm, 2.5*mm]

        add_table = Table(add_rows_data, colWidths=col_widths, rowHeights=row_heights)
        add_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Oblique'),
            ('FONTSIZE', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 0.5*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5*mm),
        ]))
        
        content.append(add_table)
        
        return content
    
    def _build_grand_total_row(self, data):
        """Build Grand Total row"""
        content = []
        content_width = self.page_width - 4*mm
        
        summary = data.get('summary', data)
        total = float(summary.get('total', 0) or 0)
        
        row_data = [[
            '', '', '', '', '', '',
            Paragraph("<b>Grand Total</b>", self.styles['GrandTotal']),
            '', '', '',
            Paragraph(f"<b>{self.currency_symbol} {total:,.2f}</b>", self.styles['GrandTotal'])
        ]]
        
        col_widths = [
            content_width * 0.04,
            content_width * 0.22,
            content_width * 0.08,
            content_width * 0.08,
            content_width * 0.05,
            content_width * 0.10,
            content_width * 0.08,
            content_width * 0.09,
            content_width * 0.08,
            content_width * 0.08,
            content_width * 0.10  # 10: Total
        ]
        
        total_table = Table(row_data, colWidths=col_widths)
        total_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (6, 0), (9, 0)),
            ('ALIGN', (6, 0), (9, 0), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        
        content.append(total_table)
        
        return content
    
    def _build_tax_summary_table(self, data):
        """Build Tax Summary table: Tax Rate | Taxable Amt. | CGST | SGST | Total Tax"""
        content = []
        content_width = self.page_width - 4*mm
        
        # Header row
        header_row = [
            Paragraph('<b>Tax Rate</b>', self.styles['BoldText']),
            Paragraph('<b>Taxable Amt.</b>', self.styles['BoldText']),
            Paragraph('<b>CGST</b>', self.styles['BoldText']),
            Paragraph('<b>SGST</b>', self.styles['BoldText']),
            Paragraph('<b>Total Tax</b>', self.styles['BoldText'])
        ]
        
        table_data = [header_row]
        
        # Group items by tax rate
        tax_groups = {}
        items = data.get('items', [])
        for item in items:
            cgst_rate = float(item.get('cgstRate', 0) or item.get('cgst', 0) or 0)
            sgst_rate = float(item.get('sgstRate', 0) or item.get('sgst', 0) or 0)
            total_rate = cgst_rate + sgst_rate
            
            taxable_value = float(item.get('taxableValue', 0) or item.get('lineTotal', 0) or 0)
            cgst_amount = float(item.get('cgstAmount', 0) or 0)
            sgst_amount = float(item.get('sgstAmount', 0) or 0)
            
            if cgst_amount == 0 and cgst_rate > 0:
                cgst_amount = taxable_value * cgst_rate / 100
            if sgst_amount == 0 and sgst_rate > 0:
                sgst_amount = taxable_value * sgst_rate / 100
            
            rate_key = f"{total_rate:.2f}%"
            if rate_key not in tax_groups:
                tax_groups[rate_key] = {
                    'taxable': 0,
                    'cgst': 0,
                    'sgst': 0,
                    'total_tax': 0
                }
            
            tax_groups[rate_key]['taxable'] += taxable_value
            tax_groups[rate_key]['cgst'] += cgst_amount
            tax_groups[rate_key]['sgst'] += sgst_amount
            tax_groups[rate_key]['total_tax'] += cgst_amount + sgst_amount
        
        # Add data rows
        for rate_key, values in tax_groups.items():
            table_data.append([
                Paragraph(rate_key, self.styles['TableCell']),
                Paragraph(f"{values['taxable']:,.2f}", self.styles['TableCellRight']),
                Paragraph(f"{values['cgst']:,.2f}", self.styles['TableCellRight']),
                Paragraph(f"{values['sgst']:,.2f}", self.styles['TableCellRight']),
                Paragraph(f"{values['total_tax']:,.2f}", self.styles['TableCellRight'])
            ])
        
        col_widths = [
            content_width * 0.15,
            content_width * 0.25,
            content_width * 0.20,
            content_width * 0.20,
            content_width * 0.20
        ]
        
        summary_table = Table(table_data, colWidths=col_widths)
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEAFTER', (0, 0), (-2, -1), 0.25, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        content.append(summary_table)
        
        return content
    
    def _format_date_time(self, date_str):
        """Format date string with time - matching 1-1.html format (DD-MM-YYYY HH:MM AM/PM)"""
        if not date_str:
            return 'N/A'
        
        try:
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%Y %I:%M %p')
        except:
            return date_str
    
    def _format_date(self, date_str):
        """Format date string - compact for A5"""
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
    
    def _add_page_elements(self, canvas_obj, doc):
        """Add page border to each page - A5 is half of A4 (top half used)"""
        # Draw border around the page content area (top half of A4)
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setLineWidth(0.5)
        margin = 2*mm

        # A5 area with extra margin so two copies on one A4 have spacing
        # Border inset: 5mm extra at bottom and 2mm extra at top vs pure half-page
        border_bottom = self.page_height / 2 + 5*mm
        border_top = self.page_height - 4*mm
        border_height = border_top - border_bottom

        # Rect(x, y, width, height)
        canvas_obj.rect(
            margin,
            border_bottom,
            self.page_width - 2*margin,
            border_height
        )

        # Draw signatures at the bottom of the page border (text only, matching HTML)
        sig_y_position = border_bottom + 3*mm
        canvas_obj.setFont('Helvetica-Oblique', 6)
        canvas_obj.setFillColor(colors.black)

        # Left: Receiver's Signature
        canvas_obj.drawString(margin + 3*mm, sig_y_position, "Receiver's Signature")

        # Right: Authorised Signatory
        canvas_obj.drawRightString(self.page_width - margin - 3*mm, sig_y_position, "Authorised Signatory")


def generate_invoice_pdf_a5(data, options, preview=False):
    """
    Wrapper function to generate invoice PDF for A5 paper
    
    Args:
        data: Invoice data dictionary
        options: Print options dictionary
        preview: Boolean indicating preview mode
        
    Returns:
        Path to generated PDF file
    """
    generator = InvoicePDFA5Generator()
    return generator.generate_invoice_pdf(data, options, preview)
