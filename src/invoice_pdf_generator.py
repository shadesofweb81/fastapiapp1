"""
Invoice PDF Generator - Generate professional invoice PDFs using ReportLab
"""
import os
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepInFrame, KeepTogether, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.pdfgen import canvas


class InvoicePDFGenerator:
    """Generate professional invoice PDFs"""
    
    def __init__(self, paper_size="A4"):
        # Set page size based on parameter
        if paper_size == "A5":
            self.page_size = A5
            self.scale = 0.7  # Scale factor for A5 (roughly half of A4)
        else:
            self.page_size = A4
            self.scale = 1.0  # No scaling for A4
        self.page_width, self.page_height = self.page_size
        self.paper_size_name = paper_size
        self.styles = getSampleStyleSheet()
        self._create_custom_styles(paper_size)
        self.currency_symbol = 'Rs.'  # Default currency symbol
        # Currency symbol mappings for better display
        self.currency_map = {
            'INR': 'Rs.',
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'AUD': 'A$',
            'CAD': 'C$'
        }
    
    def _create_custom_styles(self, paper_size="A4"):
        """Create custom paragraph styles based on paper size"""
        # Adjust font sizes for A5 (scale to ~70%)
        is_a5 = paper_size == "A5"
        size_factor = 0.7 if is_a5 else 1.0
        
        # Company name style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=int(18 * size_factor),
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=0,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Company details style
        self.styles.add(ParagraphStyle(
            name='CompanyDetails',
            parent=self.styles['Normal'],
            fontSize=int(9 * size_factor),
            textColor=colors.HexColor('#444444'),
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        # Document title style
        self.styles.add(ParagraphStyle(
            name='DocumentTitle',
            parent=self.styles['Heading1'],
            fontSize=int(16 * size_factor),
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=0,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Normal'],
            fontSize=int(10 * size_factor),
            textColor=colors.white,
            # backColor removed for no background color
            spaceAfter=int(6 * size_factor),
            fontName='Helvetica-Bold'
        ))
        
        # Label style
        self.styles.add(ParagraphStyle(
            name='Label',
            parent=self.styles['Normal'],
            fontSize=int(9 * size_factor),
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Bold'
        ))
        
        # Value style
        self.styles.add(ParagraphStyle(
            name='Value',
            parent=self.styles['Normal'],
            fontSize=int(9 * size_factor),
            textColor=colors.HexColor('#000000')
        ))
        
        # Copy type style (ORIGINAL/DUPLICATE/TRIPLICATE)
        self.styles.add(ParagraphStyle(
            name='CopyType',
            parent=self.styles['Normal'],
            fontSize=int(9 * size_factor),
            textColor=colors.HexColor('#d32f2f'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
    
    def generate_invoice_pdf(self, data, options, preview=False):
        """
        Generate invoice PDF
        
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
            invoice_num = (
                transaction_header.get('invoiceNumber') or 
                transaction_header.get('transactionNumber') or 
                data.get('invoiceNumber', 'invoice')
            )
            # Remove empty strings
            if not invoice_num or invoice_num.strip() == '':
                invoice_num = transaction_header.get('transactionNumber', 'invoice')
            
            # Determine output path
            if preview:
                output_dir = Path(os.environ.get('TEMP', '/tmp'))
                filename = f"preview_{invoice_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            elif options.get('save_file'):
                output_dir = Path(options.get('save_location'))
                filename = options.get('filename')
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
            else:
                output_dir = Path(os.environ.get('TEMP', '/tmp'))
                filename = f"{invoice_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
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
                self.currency_symbol = 'Rs.'  # Default fallback
            
            # Get paper size from options
            paper_size = options.get('paper_size', 'A4')
            if paper_size == "A5":
                page_size = A5
                self.scale = 0.7
                # Minimal margins - larger bottom for footer with bank details
                margins = {'right': 1*mm, 'left': 1*mm, 'top': 1*mm, 'bottom': 60*mm}
            else:
                page_size = A4
                self.scale = 1.0
                # Minimal margins - larger bottom for footer with bank details
                margins = {'right': 1*mm, 'left': 1*mm, 'top': 1*mm, 'bottom': 65*mm}
            
            # Update instance page dimensions
            self.page_width, self.page_height = page_size
            self.paper_size_name = paper_size
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=page_size,
                rightMargin=margins['right'],
                leftMargin=margins['left'],
                topMargin=margins['top'],
                bottomMargin=margins['bottom']
            )
            
            # Determine which copy types to generate
            if preview:
                copy_types = ["ORIGINAL"]
            else:
                copy_types = options.get('copy_types', ["ORIGINAL"])
            
            # Build PDF content
            story = []
            
            # Store data for footer drawing
            self.footer_data = data
            
            for copy_type in copy_types:
                if copy_types.index(copy_type) > 0:
                    # Add page break between copies
                    story.append(Spacer(1, 0))  # Will be handled by page break
                
                # Build content for this copy
                story.extend(self._build_invoice_content(data, copy_type))
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            
            return str(output_path)
        
        except Exception as e:
            print(f"Error generating invoice PDF: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _build_invoice_content(self, data, copy_type):
        """Build invoice content for one copy"""
        content = []
        
        # Document title at the very top with copy type
        transaction_header = data.get('transactionHeader', {})
        trans_type = transaction_header.get('type', '')
        
        # Determine document title based on transaction type
        if data.get('documentTitle'):
            doc_title = data.get('documentTitle')
        elif 'sale' in trans_type.lower() or 'invoice' in trans_type.lower():
            doc_title = 'TAX INVOICE'
        elif 'purchase' in trans_type.lower():
            doc_title = 'PURCHASE BILL'
        else:
            doc_title = 'TAX INVOICE'
        
        # Title centered with copy type on far right only
        # Use 3 columns: empty left spacer, centered title, right-aligned copy type
        # Content width = page_width - left_margin - right_margin (margins aligned with page border)
        content_width = self.page_width - (8*mm if self.paper_size_name == "A5" else 12*mm)
        side_width = 20*mm * self.scale
        center_width = content_width - 2*side_width
        
        title_table_data = [[
            Paragraph('', self.styles['Value']),  # Empty left spacer for balance
            Paragraph(doc_title, self.styles['DocumentTitle']),
            Paragraph(copy_type, self.styles['CopyType'])  # Copy type only on right
        ]]
        title_table = Table(title_table_data, colWidths=[side_width, center_width, side_width])
        title_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))
        content.append(title_table)
        
        # Company header - no spacing between title and company
        content.extend(self._build_company_header(data))
        content.append(Spacer(1, 2*mm * self.scale))
        
        # Invoice details (left) and Party details (right)
        content.extend(self._build_details_section(data))
        content.append(Spacer(1, 2*mm * self.scale))
        
        # Items table
        content.extend(self._build_items_table(data))
        content.append(Spacer(1, 2*mm * self.scale))
        
        # Totals section with amount in words
        content.extend(self._build_totals_section(data))
        content.append(Spacer(1, 2*mm * self.scale))
        
        # Combined section: Bank Details row + Terms & Conditions (left) | Authorized Signature (right)
        content.extend(self._build_signature_section(data))
        
        # Add page break for next copy
        content.append(Spacer(1, 10*mm * self.scale))
        
        return content
    
    def _build_company_header(self, data):
        """Build company header section"""
        content = []
        
        company = data.get('company', {})
        # Support both old and new API format
        company_name = company.get('name') or company.get('companyName', 'Company Name')
        address = company.get('address', '')
        city = company.get('city', '')
        state = company.get('state', '')
        country = company.get('country', '')
        zipcode = company.get('zipCode', '')
        phone = company.get('phone') or company.get('phoneNumber', '')
        email = company.get('email', '')
        gstin = company.get('gstin') or company.get('taxId', '')
        website = company.get('website', '')
        
        # Company name
        content.append(Paragraph(company_name, self.styles['CompanyName']))
        
        # Address line 1 - Address
        if address:
            content.append(Paragraph(address, self.styles['CompanyDetails']))
        
        # Address line 2 - City, State, Zip, Country
        location_parts = []
        if city:
            location_parts.append(city)
        if state:
            location_parts.append(state)
        if zipcode:
            location_parts.append(zipcode)
        if country:
            location_parts.append(country)
        
        if location_parts:
            address_line = ', '.join(location_parts)
            content.append(Paragraph(address_line, self.styles['CompanyDetails']))
        
        # Contact details line
        contact_parts = []
        if phone:
            contact_parts.append(f"Phone: {phone}")
        if email:
            contact_parts.append(f"Email: {email}")
        if website:
            contact_parts.append(f"Web: {website}")
        
        if contact_parts:
            content.append(Paragraph(' | '.join(contact_parts), self.styles['CompanyDetails']))
        
        # Tax/GSTIN line
        if gstin:
            content.append(Paragraph(f"GSTIN: {gstin}", self.styles['CompanyDetails']))
        
        # Add horizontal border line after company header
        content.append(Spacer(1, 2*mm * self.scale))
        content_width = self.page_width - (8*mm if self.paper_size_name == "A5" else 12*mm)
        line_table = Table([['']],  colWidths=[content_width])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor('#1a5490')),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        content.append(line_table)
        
        return content
    
    def _build_details_section(self, data):
        """Build invoice details, transport details, billing and shipping address section"""
        content = []
        
        # Get transaction header (new API format) or fall back to root level (old format)
        transaction_header = data.get('transactionHeader', data)
        party_data = data.get('party', {})
        transport_data = data.get('transport', {})
        
        # Calculate column width - use full available content width
        # Document margins are aligned with page border
        # Content width = page_width - left_margin - right_margin
        content_width = self.page_width - (8*mm if self.paper_size_name == "A5" else 12*mm)
        col_width = content_width / 2
        
        # === ROW 1: Invoice Details and Transport Details ===
        # Helper function to create label-value table
        def create_details_table(details_list, title, label_width=None):
            """Create a formatted table with label: value pairs"""
            if label_width is None:
                label_width = 22*mm * self.scale
            table_data = []
            table_data.append([Paragraph(f"<b>{title}</b>", self.styles['Label']), ''])
            for label, value in details_list:
                table_data.append([
                    Paragraph(f"{label}:", self.styles['Label']),
                    Paragraph(str(value), self.styles['Value'])
                ])
            
            value_width = col_width - label_width - 4*mm * self.scale  # padding
            tbl = Table(table_data, colWidths=[label_width, value_width])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 1),
                ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ('SPAN', (0, 0), (1, 0)),  # Span title across both columns
            ]))
            return tbl
        
        # Left column - Invoice details
        invoice_details = []
        invoice_no = (
            transaction_header.get('invoiceNumber') or 
            transaction_header.get('transactionNumber') or 
            data.get('invoiceNumber', 'N/A')
        )
        if not invoice_no or invoice_no.strip() == '':
            invoice_no = transaction_header.get('transactionNumber', 'N/A')
        invoice_details.append(('Invoice No', f"<b>{invoice_no}</b>"))
        
        trans_date = transaction_header.get('transactionDate') or data.get('transactionDate', '')
        invoice_details.append(('Date', self._format_date(trans_date)))
        
        due_date = transaction_header.get('dueDate') or data.get('dueDate', '')
        if due_date:
            invoice_details.append(('Due Date', self._format_date(due_date)))
        
        place_of_supply = transaction_header.get('placeOfSupply') or data.get('placeOfSupply', '')
        if place_of_supply:
            invoice_details.append(('Place of Supply', place_of_supply))
        
        trans_no = transaction_header.get('transactionNumber') or data.get('transactionNumber', '')
        if trans_no:
            invoice_details.append(('Transaction No', trans_no))
        
        # Make Invoice Details value column wider for long names
        # Make invoice label column wider so labels fit on one line
        invoice_label_width = 28*mm * self.scale  # wider label column for long labels
        invoice_table = create_details_table(invoice_details, 'Invoice Details', label_width=invoice_label_width)
        
        # Right column - Transport details
        transport_details = []
        gr_number = transport_data.get('grNumber') or data.get('grNumber', '')
        transport_details.append(('GR/LR No', gr_number))
        
        transporter_name = transport_data.get('transporterName') or data.get('transporterName', '')
        transport_details.append(('Transporter', transporter_name))
        
        eway_bill = transport_data.get('ewayBillNo') or data.get('ewayBillNo', '')
        transport_details.append(('E-Way Bill No', eway_bill))
        
        vehicle_no = transport_data.get('vehicleNumber') or data.get('vehicleNumber', '')
        transport_details.append(('Vehicle No', vehicle_no))
        
        loading_station = transport_data.get('loadingStation') or data.get('loadingStation', '')
        if loading_station:
            transport_details.append(('Loading Station', loading_station))
        
        # Make transport label column wider so labels fit on one line
        transport_label_width = 32*mm * self.scale  # wider label column for long labels
        transport_table = create_details_table(transport_details, 'Transport Details', label_width=transport_label_width)
        
        # Create table for Invoice and Transport details
        row1_table = Table([[invoice_table, transport_table]], colWidths=[col_width, col_width])
        row1_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ]))
        content.append(row1_table)
        content.append(Spacer(1, 2*mm * self.scale))
        
        # === ROW 2: Billing Address and Shipping Address ===
        party_name = party_data.get('name') or data.get('partyName', 'N/A')
        
        # Helper function to create address table
        def create_address_table(title, name, address_data, gstin='', phone=''):
            """Create a formatted address table"""
            table_data = []
            table_data.append([Paragraph(f"<b>{title}</b>", self.styles['Label']), ''])
            table_data.append([Paragraph('Name:', self.styles['Label']), Paragraph(f"<b>{name}</b>", self.styles['Value'])])
            
            if address_data.get('address'):
                table_data.append([Paragraph('Address:', self.styles['Label']), Paragraph(address_data.get('address', ''), self.styles['Value'])])
            
            location_parts = []
            if address_data.get('city'):
                location_parts.append(address_data.get('city'))
            if address_data.get('state'):
                location_parts.append(address_data.get('state'))
            if address_data.get('zipCode'):
                location_parts.append(address_data.get('zipCode'))
            if location_parts:
                table_data.append([Paragraph('Location:', self.styles['Label']), Paragraph(', '.join(location_parts), self.styles['Value'])])
            
            if gstin:
                table_data.append([Paragraph('GSTIN:', self.styles['Label']), Paragraph(gstin, self.styles['Value'])])
            
            if phone:
                table_data.append([Paragraph('Phone:', self.styles['Label']), Paragraph(phone, self.styles['Value'])])
            
            label_width = 18*mm * self.scale
            value_width = col_width - label_width - 4*mm * self.scale
            tbl = Table(table_data, colWidths=[label_width, value_width])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 1),
                ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ('SPAN', (0, 0), (1, 0)),  # Span title across both columns
            ]))
            return tbl
        
        # Left column - Billing Address
        billing_address = party_data.get('billingAddress', party_data)
        party_gstin = party_data.get('taxId') or party_data.get('gstin', '')
        party_phone = party_data.get('phone') or party_data.get('phoneNumber', '')
        billing_table = create_address_table('Billing Address', party_name, billing_address, party_gstin, party_phone)
        
        # Right column - Shipping Address
        shipping_address = party_data.get('shippingAddress', billing_address)
        shipping_name = shipping_address.get('name') or party_name
        shipping_gstin = shipping_address.get('taxId') or shipping_address.get('gstin', '')
        shipping_phone = shipping_address.get('phone') or shipping_address.get('phoneNumber', '')
        shipping_table = create_address_table('Shipping Address', shipping_name, shipping_address, shipping_gstin, shipping_phone)
        
        # Create table for Billing and Shipping Address
        row2_table = Table([[billing_table, shipping_table]], colWidths=[col_width, col_width])
        row2_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ]))
        content.append(row2_table)
        
        return content
    
    def _build_items_table(self, data):
        """Build items table"""
        content = []
        
        # Table header
        table_data = [[
            Paragraph('<b>S.No</b>', self.styles['Label']),
            Paragraph('<b>Description</b>', self.styles['Label']),
            Paragraph('<b>HSN/SAC</b>', self.styles['Label']),
            Paragraph('<b>Qty</b>', self.styles['Label']),
            Paragraph('<b>Unit Price</b>', self.styles['Label']),
            Paragraph('<b>Discount</b>', self.styles['Label']),
            Paragraph('<b>Amount</b>', self.styles['Label'])
        ]]
        
        # Items rows
        items = data.get('items', [])
        for idx, item in enumerate(items, 1):
            # Use serialNumber from item if available, otherwise use 1-based index
            serial_no = item.get('serialNumber') if item.get('serialNumber') else idx
            description = item.get('description') or item.get('productName', '')
            hsn_code = item.get('hsnCode', '')
            quantity = item.get('quantity', 0)
            unit = item.get('unit') or item.get('unitName', '')
            unit_price = item.get('unitPrice', 0)
            discount_amount = item.get('discountAmount', 0)
            line_total = item.get('lineTotal', 0)
            
            # Format quantity with unit
            qty_display = f"{quantity:.2f} {unit}" if unit else f"{quantity:.2f}"
            
            table_data.append([
                Paragraph(str(serial_no), self.styles['Value']),
                Paragraph(description, self.styles['Value']),
                Paragraph(hsn_code, self.styles['Value']),
                Paragraph(qty_display, self.styles['Value']),
                Paragraph(f"{unit_price:,.2f}", self.styles['Value']),
                Paragraph(f"{discount_amount:,.2f}", self.styles['Value']),
                Paragraph(f"{line_total:,.2f}", self.styles['Value'])
            ])
        
        # Create table with dynamic column widths based on paper size
        # Use full content width - margins are now aligned with page border
        content_width = self.page_width - (8*mm if self.paper_size_name == "A5" else 12*mm)
        
        # Column proportions: S.No(5%), Description(37%), HSN(10%), Qty(12%), UnitPrice(13%), Discount(10%), Amount(13%)
        col_widths = [
            content_width * 0.05,  # S.No
            content_width * 0.37,  # Description
            content_width * 0.10,  # HSN
            content_width * 0.12,  # Qty
            content_width * 0.13,  # Unit Price
            content_width * 0.10,  # Discount
            content_width * 0.13   # Amount
        ]
        
        items_table = Table(table_data, colWidths=col_widths)
        
        # Scale font sizes and padding for A5
        header_font_size = int(9 * self.scale) if self.scale < 1 else 9
        data_font_size = int(8 * self.scale) if self.scale < 1 else 8
        cell_padding = int(4 * self.scale) if self.scale < 1 else 4
        
        items_table.setStyle(TableStyle([
            # Header row (no background)
            # ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            # ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), header_font_size),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), cell_padding + 2),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), data_font_size),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # S.No center
            ('ALIGN', (3, 1), (6, -1), 'RIGHT'),  # Numbers right-aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Outer border
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a5490')),
            # Internal grid lines
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.grey),  # Horizontal lines between rows
            ('LINEAFTER', (0, 0), (-2, -1), 0.5, colors.grey),  # Vertical lines between columns
            # ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            
            # Padding - default for middle columns
            ('LEFTPADDING', (0, 0), (-1, -1), cell_padding),
            ('RIGHTPADDING', (0, 0), (-1, -1), cell_padding),
            ('TOPPADDING', (0, 0), (-1, -1), cell_padding - 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), cell_padding - 1),
            
            # Small left padding for first column (S.No)
            ('LEFTPADDING', (0, 0), (0, -1), 2),
            # Small right padding for last column (Amount)
            ('RIGHTPADDING', (-1, 0), (-1, -1), 2),
        ]))
        
        content.append(items_table)
        
        return content
    
    def _build_totals_section(self, data):
        """Build totals section"""
        content = []
        
        # Get summary (new API format) or fall back to root level (old format)
        summary = data.get('summary', data)
        
        # Create totals table (right-aligned)
        totals_data = []
        
        # Subtotal
        subtotal = summary.get('subTotal', 0)
        totals_data.append([
            Paragraph('<b>Subtotal:</b>', self.styles['Label']),
            Paragraph(f"{self.currency_symbol}{subtotal:,.2f}", self.styles['Value'])
        ])
        
        # Discount
        discount = summary.get('totalDiscountAmount') or summary.get('discount', 0)
        if discount > 0:
            totals_data.append([
                Paragraph('Discount:', self.styles['Value']),
                Paragraph(f"{self.currency_symbol}{discount:,.2f}", self.styles['Value'])
            ])
        
        # Freight
        freight = summary.get('freight', 0)
        if freight > 0:
            totals_data.append([
                Paragraph('Freight:', self.styles['Value']),
                Paragraph(f"{self.currency_symbol}{freight:,.2f}", self.styles['Value'])
            ])
        
        # Taxes - use tax components summary if available
        tax_components_summary = summary.get('taxComponentsSummary', [])
        if tax_components_summary:
            totals_data.append([
                Paragraph('<b>Taxes:</b>', self.styles['Label']),
                Paragraph('', self.styles['Value'])
            ])
            
            for comp in tax_components_summary:
                comp_name = comp.get('componentName', '')
                comp_type = comp.get('componentType', '')
                rate = comp.get('rate', 0)
                amount = comp.get('amount', 0)
                
                label = f"{comp_name} ({comp_type})" if comp_type else comp_name
                if rate > 0:
                        label += f" @ {rate}%"
                
                totals_data.append([
                    Paragraph(f"  {label}:", self.styles['Value']),
                    Paragraph(f"{self.currency_symbol}{amount:,.2f}", self.styles['Value'])
                ])
        else:
            # Fall back to old format taxes
            taxes = data.get('taxes', [])
            if taxes:
                totals_data.append([
                    Paragraph('<b>Taxes:</b>', self.styles['Label']),
                    Paragraph('', self.styles['Value'])
                ])
                
                for tax in taxes:
                    tax_name = tax.get('taxName', '')
                    # Check if tax has components
                    components = tax.get('components', [])
                    if components:
                        for comp in components:
                            comp_name = comp.get('componentName', '')
                            rate = comp.get('rate', 0)
                            amount = comp.get('amount', 0)
                            label = f"{comp_name} @ {rate}%"
                            totals_data.append([
                                Paragraph(f"  {label}:", self.styles['Value']),
                                Paragraph(f"{self.currency_symbol}{amount:,.2f}", self.styles['Value'])
                            ])
                    else:
                        # Single tax without components
                        tax_amount = tax.get('taxAmount') or tax.get('amount', 0)
                        totals_data.append([
                            Paragraph(f"  {tax_name}:", self.styles['Value']),
                            Paragraph(f"{self.currency_symbol}{tax_amount:,.2f}", self.styles['Value'])
                        ])
        
        # Round off
        roundoff = summary.get('roundOff', 0)
        if roundoff != 0:
            totals_data.append([
                Paragraph('Round Off:', self.styles['Value']),
                Paragraph(f"{self.currency_symbol}{roundoff:,.2f}", self.styles['Value'])
            ])
        
        # Grand total
        total = summary.get('total', 0)
        totals_data.append([
            Paragraph('<b>Grand Total:</b>', self.styles['Label']),
            Paragraph(f"{self.currency_symbol}{total:,.2f}", self.styles['Value'])
        ])
        
        # Create table with wider columns
        totals_table = Table(totals_data, colWidths=[45*mm * self.scale, 35*mm * self.scale])
        totals_font_size = int(9 * self.scale) if self.scale < 1 else 9
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), totals_font_size),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            # Outer border for totals section
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a5490')),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#000000')),
        ]))
        
        # Create container to right-align the totals table
        content_width = self.page_width - (8*mm if self.paper_size_name == "A5" else 12*mm)
        totals_container = Table([[totals_table]], colWidths=[content_width])
        totals_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        content.append(totals_container)
        
        # Amount in words - with left margin to stay inside border
        amount_in_words = self._number_to_words(total)
        content.append(Spacer(1, 2*mm * self.scale))
        margin_offset = 6*mm if self.paper_size_name == "A5" else 8*mm
        content.append(Paragraph(f"&nbsp;&nbsp;&nbsp;<b>Amount in Words:</b> {self.currency_symbol} {amount_in_words} Only", self.styles['Value']))
        
        return content
    
    def _number_to_words(self, num):
        """Convert a number to words (Indian numbering system)"""
        if num == 0:
            return "Zero"
        
        # Round to 2 decimal places
        num = round(num, 2)
        
        # Split into integer and decimal parts
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
        
        # Crore (10,000,000)
        if int_part >= 10000000:
            crore = int_part // 10000000
            result += three_digits(crore) + ' Crore '
            int_part %= 10000000
        
        # Lakh (100,000)
        if int_part >= 100000:
            lakh = int_part // 100000
            result += two_digits(lakh) + ' Lakh '
            int_part %= 100000
        
        # Thousand
        if int_part >= 1000:
            thousand = int_part // 1000
            result += two_digits(thousand) + ' Thousand '
            int_part %= 1000
        
        # Hundred and below
        if int_part > 0:
            result += three_digits(int_part)
        
        result = result.strip()
        
        # Add decimal part (paise)
        if dec_part > 0:
            result += ' and ' + two_digits(dec_part) + ' Paise'
        
        return result if result else 'Zero'
    
    def _build_signature_section(self, data):
        """Build section - Bank Details and Terms/Auth are drawn in footer"""
        content = []
        # Bank Details, Terms & Conditions and Authorized Signature will be drawn in footer area
        return content
    
    def _format_date(self, date_str):
        """Format date string"""
        if not date_str:
            return 'N/A'
        
        try:
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d-%b-%Y')
        except:
            return date_str
    
    def _add_page_number(self, canvas_obj, doc):
        """Add page number, border, and footer to each page"""
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        font_size = 6 if self.paper_size_name == "A5" else 8
        canvas_obj.setFont('Helvetica', font_size)
        canvas_obj.setFillColor(colors.grey)
        margin_offset = 10*mm if self.paper_size_name == "A5" else 15*mm
        canvas_obj.drawRightString(self.page_width - margin_offset, 4*mm, text)
        
        # Draw border around the page
        canvas_obj.setStrokeColor(colors.HexColor('#1a5490'))
        canvas_obj.setLineWidth(1)
        margin = 3*mm if self.paper_size_name == "A5" else 5*mm
        canvas_obj.rect(
            margin, 
            margin, 
            self.page_width - 2*margin, 
            self.page_height - 2*margin
        )
        
        # Draw footer section (Terms & Conditions | Authorized Signature)
        self._draw_footer(canvas_obj)
    
    def _draw_footer(self, canvas_obj):
        """Draw footer with Bank Details (left), Terms & Conditions (left) and Authorized Signature (right)"""
        # Get data
        data = getattr(self, 'footer_data', {})
        company = data.get('company', {})
        company_name = company.get('name') or company.get('companyName', 'Company Name')
        terms = data.get('terms', '')
        
        # Get bank details
        bank_details = data.get('bankDetails', {})
        bank_name = bank_details.get('bankName') or company.get('bankName', '')
        account_name = bank_details.get('accountName') or company.get('accountName', '')
        account_number = bank_details.get('accountNumber') or company.get('accountNumber', '')
        ifsc_code = bank_details.get('ifscCode') or company.get('ifscCode', '')
        branch = bank_details.get('branch') or company.get('branch', '')
        upi_id = bank_details.get('upiId') or company.get('upiId', '')
        
        # Calculate positions
        margin = 3*mm if self.paper_size_name == "A5" else 5*mm
        content_margin = margin + 1*mm
        footer_top = 58*mm if self.paper_size_name == "A5" else 62*mm
        terms_top = 32*mm if self.paper_size_name == "A5" else 35*mm  # Where terms/auth row starts - closer to bank details
        content_width = self.page_width - 2*content_margin
        half_width = content_width / 2
        
        # Font sizes
        label_font_size = int(8 * self.scale) if self.scale < 1 else 8
        value_font_size = int(7 * self.scale) if self.scale < 1 else 7
        
        mid_x = self.page_width / 2
        
        # === HORIZONTAL LINE above bank details ===
        canvas_obj.setStrokeColor(colors.HexColor('#1a5490'))
        canvas_obj.setLineWidth(1)
        canvas_obj.line(content_margin, footer_top, self.page_width - content_margin, footer_top)
        
        # === BANK DETAILS (Left side, above terms row) ===
        canvas_obj.setLineWidth(0.5)
        
        # Bank Details title
        canvas_obj.setFillColor(colors.HexColor('#666666'))
        canvas_obj.setFont('Helvetica-Bold', label_font_size)
        y_pos = footer_top - 3*mm
        canvas_obj.drawString(content_margin + 2*mm, y_pos, "Bank Details")
        
        # Underline for title
        canvas_obj.line(content_margin + 2*mm, y_pos - 1*mm, content_margin + 30*mm, y_pos - 1*mm)
        
        # Bank details content
        canvas_obj.setFont('Helvetica', value_font_size)
        canvas_obj.setFillColor(colors.black)
        y_pos -= 5*mm
        
        # Row 1: Bank Name | IFSC Code
        canvas_obj.setFont('Helvetica-Bold', value_font_size)
        canvas_obj.drawString(content_margin + 2*mm, y_pos, "Bank:")
        canvas_obj.setFont('Helvetica', value_font_size)
        canvas_obj.drawString(content_margin + 15*mm, y_pos, bank_name if bank_name else '________________')
        
        canvas_obj.setFont('Helvetica-Bold', value_font_size)
        canvas_obj.drawString(content_margin + 55*mm, y_pos, "IFSC:")
        canvas_obj.setFont('Helvetica', value_font_size)
        canvas_obj.drawString(content_margin + 67*mm, y_pos, ifsc_code if ifsc_code else '________________')
        
        y_pos -= 3.5*mm
        
        # Row 2: Account No | Branch
        canvas_obj.setFont('Helvetica-Bold', value_font_size)
        canvas_obj.drawString(content_margin + 2*mm, y_pos, "A/C No:")
        canvas_obj.setFont('Helvetica', value_font_size)
        canvas_obj.drawString(content_margin + 15*mm, y_pos, account_number if account_number else '________________')
        
        canvas_obj.setFont('Helvetica-Bold', value_font_size)
        canvas_obj.drawString(content_margin + 55*mm, y_pos, "Branch:")
        canvas_obj.setFont('Helvetica', value_font_size)
        canvas_obj.drawString(content_margin + 67*mm, y_pos, branch if branch else '________________')
        
        # === HORIZONTAL LINE separating bank details from terms/auth ===
        canvas_obj.setStrokeColor(colors.HexColor('#1a5490'))
        canvas_obj.setLineWidth(1)
        canvas_obj.line(content_margin, terms_top, self.page_width - content_margin, terms_top)
        
        # Draw middle vertical line for terms/auth section
        canvas_obj.line(mid_x, margin + 6*mm, mid_x, terms_top)
        
        # === LEFT SIDE: Terms & Conditions ===
        canvas_obj.setFillColor(colors.HexColor('#666666'))
        canvas_obj.setFont('Helvetica-Bold', label_font_size)
        y_pos = terms_top - 4*mm
        canvas_obj.drawString(content_margin + 2*mm, y_pos, "Terms & Conditions:")
        
        # Terms content
        canvas_obj.setFont('Helvetica', value_font_size)
        canvas_obj.setFillColor(colors.black)
        y_pos -= 3.5*mm
        
        if terms:
            terms_list = terms.split('\n')
            for term in terms_list:
                if term.strip() and y_pos > margin + 8*mm:
                    canvas_obj.drawString(content_margin + 2*mm, y_pos, f"• {term.strip()[:45]}")
                    y_pos -= 3*mm
        else:
            # Placeholder terms
            placeholder_terms = [
                "Goods once sold will not be taken back.",
                "Payment is due within 30 days.",
                "Subject to local jurisdiction."
            ]
            for term in placeholder_terms:
                if y_pos > margin + 8*mm:
                    canvas_obj.drawString(content_margin + 2*mm, y_pos, f"• {term}")
                    y_pos -= 3*mm
        
        # === RIGHT SIDE: Authorized Signature ===
        sig_center_x = mid_x + half_width / 2
        
        # Company name
        canvas_obj.setFont('Helvetica-Bold', value_font_size)
        canvas_obj.setFillColor(colors.black)
        y_pos = terms_top - 4*mm
        company_text = f"For {company_name}"
        text_width = canvas_obj.stringWidth(company_text, 'Helvetica-Bold', value_font_size)
        canvas_obj.drawString(sig_center_x - text_width/2, y_pos, company_text)
        
        # Signature line
        y_pos = margin + 14*mm
        line_width = 45*mm * self.scale
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(sig_center_x - line_width/2, y_pos, sig_center_x + line_width/2, y_pos)
        
        # Authorized Signatory label
        canvas_obj.setFont('Helvetica', label_font_size)
        canvas_obj.setFillColor(colors.HexColor('#666666'))
        y_pos -= 3*mm
        label_text = "Authorized Signatory"
        text_width = canvas_obj.stringWidth(label_text, 'Helvetica', label_font_size)
        canvas_obj.drawString(sig_center_x - text_width/2, y_pos, label_text)


def generate_invoice_pdf(data, options, preview=False):
    """
    Wrapper function to generate invoice PDF
    
    Args:
        data: Invoice data dictionary
        options: Print options dictionary
        preview: Boolean indicating preview mode
        
    Returns:
        Path to generated PDF file
    """
    # Create generator with the correct paper size from options
    paper_size = options.get('paper_size', 'A4')
    generator = InvoicePDFGenerator(paper_size)
    return generator.generate_invoice_pdf(data, options, preview)
