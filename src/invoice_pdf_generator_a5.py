"""
Invoice PDF Generator A5 - Generate professional invoice PDFs for A5 paper using ReportLab
This is a separate implementation optimized for A5 paper size (half of A4)
"""
import os
import re
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepInFrame, KeepTogether, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.pdfgen import canvas


class InvoicePDFA5Generator:
    """Generate professional invoice PDFs for A5 paper size"""
    
    def __init__(self):
        self.page_size = A5
        self.page_width, self.page_height = self.page_size
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
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
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for A5 paper size"""
        # Company name style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=12,
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
            fontSize=6,
            textColor=colors.HexColor('#444444'),
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0
        ))
        
        # Document title style
        self.styles.add(ParagraphStyle(
            name='DocumentTitle',
            parent=self.styles['Heading1'],
            fontSize=11,
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
            fontSize=7,
            textColor=colors.white,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        ))
        
        # Label style
        self.styles.add(ParagraphStyle(
            name='Label',
            parent=self.styles['Normal'],
            fontSize=6,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Bold'
        ))
        
        # Value style
        self.styles.add(ParagraphStyle(
            name='Value',
            parent=self.styles['Normal'],
            fontSize=6,
            textColor=colors.HexColor('#000000')
        ))
        
        # Copy type style (ORIGINAL/DUPLICATE/TRIPLICATE)
        self.styles.add(ParagraphStyle(
            name='CopyType',
            parent=self.styles['Normal'],
            fontSize=6,
            textColor=colors.HexColor('#d32f2f'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
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
                self.currency_symbol = 'Rs.'  # Default fallback
            
            # A5 margins - compact for smaller paper
            margins = {'right': 1*mm, 'left': 1*mm, 'top': 1*mm, 'bottom': 45*mm}

            # Create PDF title for metadata
            company_name = company.get('name') or company.get('companyName', 'Company')
            pdf_title = f"Invoice {invoice_num} - {company_name}"

            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A5,
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
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            
            return str(output_path)
        
        except Exception as e:
            print(f"Error generating A5 invoice PDF: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _build_invoice_content(self, data, copy_type):
        """Build invoice content for one copy - A5 optimized layout"""
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
        content_width = self.page_width - 6*mm
        side_width = 20*mm
        center_width = content_width - 2*side_width
        
        title_table_data = [[
            Paragraph('', self.styles['Value']),
            Paragraph(doc_title, self.styles['DocumentTitle']),
            Paragraph(copy_type, self.styles['CopyType'])
        ]]
        title_table = Table(title_table_data, colWidths=[side_width, center_width, side_width])
        title_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))
        content.append(title_table)

        # Company header
        content.extend(self._build_company_header(data))
        content.append(Spacer(1, 1*mm))

        # Invoice details and Party details
        content.extend(self._build_details_section(data))
        content.append(Spacer(1, 1*mm))
        
        # Items table
        content.extend(self._build_items_table(data))
        content.append(Spacer(1, 1*mm))
        
        # Totals section with amount in words
        content.extend(self._build_totals_section(data))

        return content
    
    def _build_company_header(self, data):
        """Build company header section - compact for A5"""
        content = []
        
        company = data.get('company', {})
        company_name = company.get('name') or company.get('companyName', 'Company Name')
        address = company.get('address', '')
        city = company.get('city', '')
        state = company.get('state', '')
        country = company.get('country', '')
        zipcode = company.get('zipCode', '')
        phone = company.get('phone') or company.get('phoneNumber', '')
        email = company.get('email', '')
        gstin = company.get('gstin') or company.get('taxId', '')
        
        # Company name
        content.append(Paragraph(company_name, self.styles['CompanyName']))
        
        # Combined address line
        address_parts = []
        if address:
            address_parts.append(address)
        location_parts = []
        if city:
            location_parts.append(city)
        if state:
            location_parts.append(state)
        if zipcode:
            location_parts.append(zipcode)
        if location_parts:
            address_parts.append(', '.join(location_parts))
        
        if address_parts:
            content.append(Paragraph(' | '.join(address_parts), self.styles['CompanyDetails']))
        
        # Contact and GSTIN on same line
        contact_parts = []
        if phone:
            contact_parts.append(f"Ph: {phone}")
        if email:
            contact_parts.append(f"Email: {email}")
        if gstin:
            contact_parts.append(f"GSTIN: {gstin}")
        
        if contact_parts:
            content.append(Paragraph(' | '.join(contact_parts), self.styles['CompanyDetails']))

        # Add horizontal border line
        content_width = self.page_width - 6*mm
        line_table = Table([['']], colWidths=[content_width])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor('#1a5490')),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        content.append(line_table)

        return content
    
    def _build_details_section(self, data):
        """Build invoice details and party details - A5 compact layout"""
        content = []
        
        transaction_header = data.get('transactionHeader', data)
        party_data = data.get('party', {})
        transport_data = data.get('transport', {})
        
        content_width = self.page_width - 6*mm
        col_width = content_width / 2
        
        # Helper function to create compact label-value table
        def create_details_table(details_list, title):
            table_data = []
            table_data.append([Paragraph(f"<b>{title}</b>", self.styles['Label']), ''])
            for label, value in details_list:
                table_data.append([
                    Paragraph(f"{label}:", self.styles['Label']),
                    Paragraph(str(value), self.styles['Value'])
                ])
            
            label_width = 18*mm
            value_width = col_width - label_width - 2*mm
            tbl = Table(table_data, colWidths=[label_width, value_width])
            tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 1),
                ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('SPAN', (0, 0), (1, 0)),
            ]))
            return tbl
        
        # Left column - Invoice details
        invoice_details = []
        invoice_no = transaction_header.get('invoiceNumber') or data.get('invoiceNumber', 'N/A')
        invoice_details.append(('Inv No', f"<b>{invoice_no}</b>"))
        
        trans_date = transaction_header.get('transactionDate') or data.get('transactionDate', '')
        invoice_details.append(('Date', self._format_date(trans_date)))
        
        due_date = transaction_header.get('dueDate') or data.get('dueDate', '')
        if due_date:
            invoice_details.append(('Due', self._format_date(due_date)))
        
        invoice_table = create_details_table(invoice_details, 'Invoice Details')
        
        # Right column - Party details (compact)
        party_name = party_data.get('name') or data.get('partyName', 'N/A')
        billing_address = party_data.get('billingAddress', party_data)
        
        party_details = []
        party_details.append(('Party', f"<b>{party_name[:25]}</b>"))
        
        if billing_address.get('city'):
            party_details.append(('City', billing_address.get('city', '')))
        
        party_gstin = party_data.get('taxId') or party_data.get('gstin', '')
        if party_gstin:
            party_details.append(('GSTIN', party_gstin))
        
        party_table = create_details_table(party_details, 'Bill To')
        
        # Create table for both sections
        details_table = Table([[invoice_table, party_table]], colWidths=[col_width, col_width])
        details_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ]))
        content.append(details_table)
        
        return content
    
    def _build_items_table(self, data):
        """Build items table - A5 compact layout"""
        content = []
        
        # Simplified header for A5
        table_data = [[
            Paragraph('<b>#</b>', self.styles['Label']),
            Paragraph('<b>Description</b>', self.styles['Label']),
            Paragraph('<b>HSN</b>', self.styles['Label']),
            Paragraph('<b>Qty</b>', self.styles['Label']),
            Paragraph('<b>Rate</b>', self.styles['Label']),
            Paragraph('<b>Amount</b>', self.styles['Label'])
        ]]
        
        # Items rows
        items = data.get('items', [])
        for idx, item in enumerate(items, 1):
            serial_no = item.get('serialNumber') if item.get('serialNumber') else idx
            description = item.get('description') or item.get('productName', '')
            # Truncate description for A5
            if len(description) > 30:
                description = description[:27] + '...'
            hsn_code = item.get('hsnCode', '')
            quantity = float(item.get('quantity', 0) or 0)
            unit = item.get('unit') or item.get('unitName', '')
            unit_price = float(item.get('unitPrice', 0) or 0)
            line_total = float(item.get('lineTotal', 0) or 0)

            qty_display = f"{quantity:.0f}" if quantity == int(quantity) else f"{quantity:.1f}"
            if unit:
                qty_display += f" {unit[:3]}"
            
            table_data.append([
                Paragraph(str(serial_no), self.styles['Value']),
                Paragraph(description, self.styles['Value']),
                Paragraph(hsn_code, self.styles['Value']),
                Paragraph(qty_display, self.styles['Value']),
                Paragraph(f"{unit_price:,.0f}", self.styles['Value']),
                Paragraph(f"{line_total:,.0f}", self.styles['Value'])
            ])
        
        # A5 column widths - more compact
        content_width = self.page_width - 6*mm
        col_widths = [
            content_width * 0.05,  # #
            content_width * 0.40,  # Description
            content_width * 0.12,  # HSN
            content_width * 0.13,  # Qty
            content_width * 0.14,  # Rate
            content_width * 0.16   # Amount
        ]
        
        items_table = Table(table_data, colWidths=col_widths)
        
        items_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 6),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
            
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 5),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (3, 1), (5, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#1a5490')),
            ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.grey),
            ('LINEAFTER', (0, 0), (-2, -1), 0.25, colors.grey),
            
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        
        content.append(items_table)
        
        return content
    
    def _build_totals_section(self, data):
        """Build totals section - A5 compact"""
        content = []
        
        summary = data.get('summary', data)
        
        totals_data = []
        
        # Subtotal
        subtotal = float(summary.get('subTotal', 0) or 0)
        totals_data.append([
            Paragraph('<b>Subtotal:</b>', self.styles['Label']),
            Paragraph(f"{self.currency_symbol}{subtotal:,.0f}", self.styles['Value'])
        ])

        # Taxes - simplified for A5
        tax_components_summary = summary.get('taxComponentsSummary', [])
        if tax_components_summary:
            total_tax = sum(float(comp.get('amount', 0) or 0) for comp in tax_components_summary)
            totals_data.append([
                Paragraph('Tax:', self.styles['Value']),
                Paragraph(f"{self.currency_symbol}{total_tax:,.0f}", self.styles['Value'])
            ])
        else:
            taxes = data.get('taxes', [])
            if taxes:
                total_tax = sum(float(tax.get('taxAmount') or tax.get('amount', 0) or 0) for tax in taxes)
                totals_data.append([
                    Paragraph('Tax:', self.styles['Value']),
                    Paragraph(f"{self.currency_symbol}{total_tax:,.0f}", self.styles['Value'])
                ])

        # Grand total
        total = float(summary.get('total', 0) or 0)
        totals_data.append([
            Paragraph('<b>Total:</b>', self.styles['Label']),
            Paragraph(f"<b>{self.currency_symbol}{total:,.0f}</b>", self.styles['Value'])
        ])
        
        # Compact totals table
        totals_table = Table(totals_data, colWidths=[25*mm, 25*mm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#1a5490')),
        ]))
        
        # Right-align totals
        content_width = self.page_width - 6*mm
        totals_container = Table([[totals_table]], colWidths=[content_width])
        totals_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        content.append(totals_container)
        
        # Amount in words - compact
        amount_in_words = self._number_to_words(total)
        content.append(Spacer(1, 1*mm))
        content.append(Paragraph(f"<b>In Words:</b> {self.currency_symbol} {amount_in_words} Only", self.styles['Value']))
        
        return content
    
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
    
    def _format_date(self, date_str):
        """Format date string - compact for A5"""
        if not date_str:
            return 'N/A'
        
        try:
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%y')  # Shorter date format for A5
        except:
            return date_str
    
    def _add_page_number(self, canvas_obj, doc):
        """Add page number, border, and footer to each page"""
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.setFont('Helvetica', 5)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawRightString(self.page_width - 8*mm, 3*mm, text)
        
        # Draw border around the page
        canvas_obj.setStrokeColor(colors.HexColor('#1a5490'))
        canvas_obj.setLineWidth(0.5)
        margin = 2*mm
        canvas_obj.rect(
            margin, 
            margin, 
            self.page_width - 2*margin, 
            self.page_height - 2*margin
        )
        
        # Draw footer section
        self._draw_footer(canvas_obj)
    
    def _draw_footer(self, canvas_obj):
        """Draw footer with Bank Details and Authorized Signature - A5 compact"""
        data = getattr(self, 'footer_data', {})
        company = data.get('company', {})
        company_name = company.get('name') or company.get('companyName', 'Company Name')
        
        # Get bank details
        bank_details = data.get('bankDetails', {})
        bank_name = bank_details.get('bankName') or company.get('bankName', '')
        account_number = bank_details.get('accountNumber') or company.get('accountNumber', '')
        ifsc_code = bank_details.get('ifscCode') or company.get('ifscCode', '')
        
        # Calculate positions
        margin = 2*mm
        content_margin = margin + 1*mm
        footer_top = 43*mm
        content_width = self.page_width - 2*content_margin
        
        # Font sizes - smaller for A5
        label_font_size = 5
        value_font_size = 5
        
        mid_x = self.page_width / 2
        
        # Horizontal line above footer
        canvas_obj.setStrokeColor(colors.HexColor('#1a5490'))
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(content_margin, footer_top, self.page_width - content_margin, footer_top)
        
        # Bank Details (left side)
        canvas_obj.setFillColor(colors.HexColor('#666666'))
        canvas_obj.setFont('Helvetica-Bold', label_font_size)
        y_pos = footer_top - 3*mm
        canvas_obj.drawString(content_margin + 1*mm, y_pos, "Bank Details")
        
        canvas_obj.setFont('Helvetica', value_font_size)
        canvas_obj.setFillColor(colors.black)
        y_pos -= 3*mm
        
        if bank_name:
            canvas_obj.drawString(content_margin + 1*mm, y_pos, f"Bank: {bank_name}")
            y_pos -= 2.5*mm
        if account_number:
            canvas_obj.drawString(content_margin + 1*mm, y_pos, f"A/C: {account_number}")
            y_pos -= 2.5*mm
        if ifsc_code:
            canvas_obj.drawString(content_margin + 1*mm, y_pos, f"IFSC: {ifsc_code}")
        
        # Vertical line
        canvas_obj.line(mid_x, margin + 4*mm, mid_x, footer_top)
        
        # Authorized Signature (right side)
        sig_center_x = mid_x + (content_width / 4)
        
        canvas_obj.setFont('Helvetica-Bold', value_font_size)
        y_pos = footer_top - 3*mm
        company_text = f"For {company_name[:20]}"
        text_width = canvas_obj.stringWidth(company_text, 'Helvetica-Bold', value_font_size)
        canvas_obj.drawString(sig_center_x - text_width/2, y_pos, company_text)
        
        # Signature line
        y_pos = margin + 10*mm
        line_width = 30*mm
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(sig_center_x - line_width/2, y_pos, sig_center_x + line_width/2, y_pos)
        
        # Label
        canvas_obj.setFont('Helvetica', label_font_size)
        canvas_obj.setFillColor(colors.HexColor('#666666'))
        y_pos -= 2.5*mm
        label_text = "Authorized Signatory"
        text_width = canvas_obj.stringWidth(label_text, 'Helvetica', label_font_size)
        canvas_obj.drawString(sig_center_x - text_width/2, y_pos, label_text)


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
