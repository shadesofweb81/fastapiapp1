"""
Ledger PDF Generator - A4 paper size
Generates ledger statement PDFs matching the Busy software layout style
"""
import os
import re
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfgen import canvas


class LedgerPDFGenerator:
    """Generate professional ledger statement PDFs with Busy-style template for A4/A5 paper"""

    def __init__(self, paper_size='A4'):
        self.paper_size_name = paper_size.upper()
        # Set page size based on parameter
        if self.paper_size_name == 'A5':
            self.page_size = A5
            self.outer_margin = 5 * mm
            self.font_scale = 0.85  # Scale fonts for A5
        else:
            self.page_size = A4
            self.outer_margin = 8 * mm
            self.font_scale = 1.0
        self.page_width, self.page_height = self.page_size
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.currency_symbol = '\u20b9'
        self.currency_map = {
            'INR': '\u20b9',
            'USD': '$',
            'EUR': '\u20ac',
            'GBP': '\u00a3',
            'JPY': '\u00a5',
            'AUD': 'A$',
            'CAD': 'C$'
        }
        self.content_width = self.page_width - (2 * self.outer_margin)

    def _create_custom_styles(self):
        """Create custom paragraph styles for ledger template"""
        scale = self.font_scale

        self.styles.add(ParagraphStyle(
            name='LedgerCompanyName',
            parent=self.styles['Heading1'],
            fontSize=int(14 * scale),
            textColor=colors.black,
            spaceAfter=0,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerGSTIN',
            parent=self.styles['Normal'],
            fontSize=int(8 * scale),
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerTitle',
            parent=self.styles['Normal'],
            fontSize=int(11 * scale),
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceBefore=2,
            spaceAfter=2,
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerDateRange',
            parent=self.styles['Normal'],
            fontSize=int(8 * scale),
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerAccountName',
            parent=self.styles['Normal'],
            fontSize=int(9 * scale),
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerTableHeader',
            parent=self.styles['Normal'],
            fontSize=int(7 * scale) if scale < 1 else 7,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerCell',
            parent=self.styles['Normal'],
            fontSize=int(7 * scale) if scale < 1 else 7,
            textColor=colors.black,
            fontName='Helvetica'
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerCellCenter',
            parent=self.styles['Normal'],
            fontSize=int(7 * scale) if scale < 1 else 7,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerCellRight',
            parent=self.styles['Normal'],
            fontSize=int(7 * scale) if scale < 1 else 7,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=TA_RIGHT
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerCellBold',
            parent=self.styles['Normal'],
            fontSize=int(7 * scale) if scale < 1 else 7,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerCellBoldRight',
            parent=self.styles['Normal'],
            fontSize=int(7 * scale) if scale < 1 else 7,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerCellBoldCenter',
            parent=self.styles['Normal'],
            fontSize=int(7 * scale) if scale < 1 else 7,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='LedgerNarration',
            parent=self.styles['Normal'],
            fontSize=6,
            textColor=colors.black,
            fontName='Helvetica-Oblique'
        ))

    def generate_ledger_pdf(self, data, options, preview=False):
        """
        Generate ledger PDF

        Args:
            data: Dictionary containing ledger data
            options: Dictionary containing print options
            preview: If True, generate for preview

        Returns:
            Path to generated PDF file
        """
        try:
            ledger_name = data.get('ledgerName', 'Ledger')
            safe_name = re.sub(r'[\\/:*?"<>|\s]+', '_', str(ledger_name)).strip('_')

            if preview:
                output_dir = Path(os.environ.get('TEMP', '/tmp'))
                filename = f"preview_ledger_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            elif options.get('save_file'):
                output_dir = Path(options.get('save_location'))
                filename = options.get('filename', f"ledger_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                filename = re.sub(r'[\\/:*?"<>|\s]+', '_', str(filename)).strip('_')
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
            else:
                output_dir = Path(os.environ.get('TEMP', '/tmp'))
                filename = f"ledger_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / filename

            # Set currency symbol from company data
            company = data.get('company', {}) or {}
            currency_symbol = company.get('currencySymbol') or company.get('currency_symbol')
            currency_code = company.get('currencyCode') or company.get('currency')

            if currency_symbol:
                self.currency_symbol = currency_symbol
            elif currency_code and currency_code in self.currency_map:
                self.currency_symbol = self.currency_map[currency_code]
            else:
                self.currency_symbol = '\u20b9'

            company_name = company.get('name') or company.get('companyName', 'Company')
            pdf_title = f"Ledger - {ledger_name}"

            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=self.page_size,
                rightMargin=self.outer_margin,
                leftMargin=self.outer_margin,
                topMargin=self.outer_margin + 2 * mm,
                bottomMargin=self.outer_margin + 6 * mm,
                title=pdf_title,
                author=company_name,
                subject=f"Ledger - {ledger_name}"
            )

            story = self._build_ledger_content(data)

            self._ledger_data = data
            doc.build(story, onFirstPage=self._add_page_border, onLaterPages=self._add_page_border)

            return str(output_path)

        except Exception as e:
            print(f"Error generating ledger PDF: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _build_ledger_content(self, data):
        """Build the full ledger content"""
        content = []

        # Header section
        content.extend(self._build_header(data))
        content.append(Spacer(1, 3 * mm))

        # Transaction table (includes opening balance, transactions, totals)
        content.extend(self._build_transaction_table(data))

        return content

    def _build_header(self, data):
        """Build ledger header: company name, GSTIN, title, date range, account name"""
        content = []
        company = data.get('company', {}) or {}

        # Company name
        company_name = company.get('name') or company.get('companyName', '')
        if company_name:
            content.append(Paragraph(company_name.upper(), self.styles['LedgerCompanyName']))

        # GSTIN
        gstin = company.get('gstin') or company.get('taxId', '')
        if gstin:
            content.append(Paragraph(f"GSTIN : {gstin}", self.styles['LedgerGSTIN']))
            content.append(Spacer(1, 1 * mm))

        # Title
        content.append(Paragraph("L E D G E R", self.styles['LedgerTitle']))

        # Date range
        from_date = self._format_date_short(data.get('fromDate', ''))
        to_date = self._format_date_short(data.get('toDate', ''))
        if from_date and to_date:
            content.append(Paragraph(f"( From {from_date} to {to_date} )", self.styles['LedgerDateRange']))

        content.append(Spacer(1, 1 * mm))

        # Account name
        ledger_name = data.get('ledgerName', '')
        if ledger_name:
            content.append(Paragraph(f"Account : {ledger_name}", self.styles['LedgerAccountName']))

        return content

    def _build_transaction_table(self, data):
        """Build the main transaction table with header, rows, and totals"""
        content = []

        # Column widths: Date, Type, Vch No., Particulars, Narration, Debit, Credit, Balance
        col_widths = [
            self.content_width * 0.09,   # Date
            self.content_width * 0.07,   # Type
            self.content_width * 0.10,   # Vch No.
            self.content_width * 0.17,   # Particulars
            self.content_width * 0.17,   # Narration
            self.content_width * 0.13,   # Debit
            self.content_width * 0.13,   # Credit
            self.content_width * 0.14,   # Balance
        ]

        # Header row
        header_row = [
            Paragraph('<b>Date</b>', self.styles['LedgerTableHeader']),
            Paragraph('<b>Type</b>', self.styles['LedgerTableHeader']),
            Paragraph('<b>Vch No.</b>', self.styles['LedgerTableHeader']),
            Paragraph('<b>Particulars</b>', self.styles['LedgerTableHeader']),
            Paragraph('<b>Narration</b>', self.styles['LedgerTableHeader']),
            Paragraph(f'<b>Debit ({self.currency_symbol})</b>', self.styles['LedgerTableHeader']),
            Paragraph(f'<b>Credit ({self.currency_symbol})</b>', self.styles['LedgerTableHeader']),
            Paragraph(f'<b>Balance ({self.currency_symbol})</b>', self.styles['LedgerTableHeader']),
        ]

        table_data = [header_row]

        # Opening balance row
        opening_balance = data.get('openingBalance', 0)
        opening_balance_type = data.get('openingBalanceType', '')
        opening_date = self._format_date_short(data.get('openingBalanceDate', data.get('fromDate', '')))

        if opening_balance:
            ob_debit = ''
            ob_credit = ''
            if opening_balance_type.lower() == 'dr':
                ob_debit = self._format_amount(opening_balance)
            else:
                ob_credit = self._format_amount(opening_balance)

            balance_str = f"{self._format_amount(opening_balance)} {opening_balance_type}"

            table_data.append([
                Paragraph(opening_date, self.styles['LedgerCell']),
                Paragraph('', self.styles['LedgerCellCenter']),
                Paragraph('', self.styles['LedgerCell']),
                Paragraph('<b>Opening Balance</b>', self.styles['LedgerCellBold']),
                Paragraph('', self.styles['LedgerCell']),
                Paragraph(ob_debit, self.styles['LedgerCellRight']),
                Paragraph(ob_credit, self.styles['LedgerCellRight']),
                Paragraph(balance_str, self.styles['LedgerCellRight']),
            ])

        # Transaction rows
        transactions = data.get('transactions', [])
        for txn in transactions:
            date_str = self._format_date_short(txn.get('transactionDate', ''))
            txn_type = self._get_short_type(txn.get('type', ''))
            vch_no = txn.get('transactionNumber', '')
            # Use invoice number if available
            if txn.get('invoiceNumber'):
                vch_no = txn['invoiceNumber']

            # Particulars = counter entry ledger names
            counter_entries = txn.get('counterEntries', [])
            particulars = ', '.join(ce.get('ledgerName', '') for ce in counter_entries) if counter_entries else txn.get('partyName', '')

            narration = txn.get('notes', '')

            entry_type = txn.get('entryType', '')
            amount = txn.get('amount', 0)
            running_balance = txn.get('runningBalance', 0)

            debit_str = ''
            credit_str = ''
            if entry_type.lower() == 'debit':
                debit_str = self._format_amount(amount)
            elif entry_type.lower() == 'credit':
                credit_str = self._format_amount(amount)

            # Determine balance type based on closing balance type or default to Dr
            balance_type = data.get('closingBalanceType', 'Dr')
            balance_str = f"{self._format_amount(running_balance)} {balance_type}"

            table_data.append([
                Paragraph(date_str, self.styles['LedgerCell']),
                Paragraph(txn_type, self.styles['LedgerCellCenter']),
                Paragraph(vch_no, self.styles['LedgerCell']),
                Paragraph(particulars, self.styles['LedgerCell']),
                Paragraph(narration, self.styles['LedgerNarration']),
                Paragraph(debit_str, self.styles['LedgerCellRight']),
                Paragraph(credit_str, self.styles['LedgerCellRight']),
                Paragraph(balance_str, self.styles['LedgerCellRight']),
            ])

        # Total row
        total_debits = data.get('totalDebits', 0)
        total_credits = data.get('totalCredits', 0)

        table_data.append([
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('<b>Total</b>', self.styles['LedgerCellBoldRight']),
            Paragraph(f'<b>{self._format_amount(total_debits)}</b>', self.styles['LedgerCellBoldRight']),
            Paragraph(f'<b>{self._format_amount(total_credits)}</b>', self.styles['LedgerCellBoldRight']),
            Paragraph('', self.styles['LedgerCellRight']),
        ])

        # Closing Balance row
        closing_balance = data.get('closingBalance', 0)
        closing_balance_type = data.get('closingBalanceType', '')

        closing_debit = ''
        closing_credit = ''
        if closing_balance_type.lower() == 'dr':
            closing_debit = self._format_amount(closing_balance)
        elif closing_balance_type.lower() == 'cr':
            closing_credit = self._format_amount(closing_balance)

        table_data.append([
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('<b>Closing Balance</b>', self.styles['LedgerCellBoldRight']),
            Paragraph(f'<b>{closing_debit}</b>', self.styles['LedgerCellBoldRight']),
            Paragraph(f'<b>{closing_credit}</b>', self.styles['LedgerCellBoldRight']),
            Paragraph('', self.styles['LedgerCellRight']),
        ])

        # Grand Total row
        grand_debit = total_debits + (closing_balance if closing_balance_type.lower() == 'cr' else 0)
        grand_credit = total_credits + (closing_balance if closing_balance_type.lower() == 'dr' else 0)

        table_data.append([
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('', self.styles['LedgerCell']),
            Paragraph('<b>Grand Total</b>', self.styles['LedgerCellBoldRight']),
            Paragraph(f'<b>{self._format_amount(grand_debit)}</b>', self.styles['LedgerCellBoldRight']),
            Paragraph(f'<b>{self._format_amount(grand_credit)}</b>', self.styles['LedgerCellBoldRight']),
            Paragraph('', self.styles['LedgerCellRight']),
        ])

        # Calculate row indices for styling
        num_data_rows = len(table_data)
        total_row_idx = num_data_rows - 3
        closing_row_idx = num_data_rows - 2
        grand_total_row_idx = num_data_rows - 1

        table = Table(table_data, colWidths=col_widths, repeatRows=1)

        style_commands = [
            # Header
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),

            # Borders
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEBEFORE', (1, 0), (1, -1), 0.5, colors.black),
            ('LINEBEFORE', (2, 0), (2, -1), 0.5, colors.black),
            ('LINEBEFORE', (3, 0), (3, -1), 0.5, colors.black),
            ('LINEBEFORE', (4, 0), (4, -1), 0.5, colors.black),
            ('LINEBEFORE', (5, 0), (5, -1), 0.5, colors.black),
            ('LINEBEFORE', (6, 0), (6, -1), 0.5, colors.black),
            ('LINEBEFORE', (7, 0), (7, -1), 0.5, colors.black),

            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 1), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),

            # Total row styling
            ('LINEABOVE', (0, total_row_idx), (-1, total_row_idx), 0.5, colors.black),
            ('BACKGROUND', (0, total_row_idx), (-1, total_row_idx), colors.HexColor('#f5f5f5')),

            # Closing Balance row
            ('LINEABOVE', (0, closing_row_idx), (-1, closing_row_idx), 0.5, colors.black),

            # Grand Total row
            ('LINEABOVE', (0, grand_total_row_idx), (-1, grand_total_row_idx), 0.5, colors.black),
            ('BACKGROUND', (0, grand_total_row_idx), (-1, grand_total_row_idx), colors.HexColor('#e8e8e8')),
        ]

        table.setStyle(TableStyle(style_commands))
        content.append(table)

        return content

    def _get_short_type(self, txn_type):
        """Convert transaction type to short form"""
        type_map = {
            'SaleInvoice': 'Sale',
            'PurchaseInvoice': 'Purc',
            'CashReceipt': 'Rcpt',
            'CashPayment': 'Pymt',
            'BankReceipt': 'Rcpt',
            'BankPayment': 'Pymt',
            'JournalEntry': 'Jrnl',
            'CreditNote': 'CrNt',
            'DebitNote': 'DrNt',
        }
        return type_map.get(txn_type, txn_type[:4] if txn_type else '')

    def _format_date_short(self, date_str):
        """Format date string to DD-MM-YYYY"""
        if not date_str:
            return ''
        try:
            if 'T' in str(date_str):
                date_obj = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%Y')
        except Exception:
            return str(date_str)

    def _format_amount(self, amount):
        """Format amount with Indian numbering (commas)"""
        if amount is None or amount == 0:
            return '0.00'
        try:
            amount = float(amount)
            # Use Indian numbering format
            is_negative = amount < 0
            amount = abs(amount)
            int_part = int(amount)
            dec_part = f"{amount - int_part:.2f}"[1:]  # .XX

            s = str(int_part)
            if len(s) > 3:
                last3 = s[-3:]
                rest = s[:-3]
                # Group rest in pairs from right
                groups = []
                while len(rest) > 2:
                    groups.insert(0, rest[-2:])
                    rest = rest[:-2]
                if rest:
                    groups.insert(0, rest)
                formatted = ','.join(groups) + ',' + last3
            else:
                formatted = s

            result = formatted + dec_part
            if is_negative:
                result = '-' + result
            return result
        except (ValueError, TypeError):
            return '0.00'

    def _add_page_border(self, canvas_obj, doc):
        """Add outer page border and page number"""
        page_num = canvas_obj.getPageNumber()

        # Draw outer border
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.rect(
            self.outer_margin,
            self.outer_margin,
            self.page_width - 2 * self.outer_margin,
            self.page_height - 2 * self.outer_margin
        )

        # Page number at bottom right
        text = f"Page {page_num}"
        canvas_obj.setFont('Helvetica', 7)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawRightString(self.page_width - 10 * mm, 4 * mm, text)


def generate_ledger_pdf(data, options, preview=False):
    """
    Wrapper function to generate ledger PDF

    Args:
        data: Ledger data dictionary
        options: Print options dictionary (includes 'paper_size': 'A4' or 'A5')
        preview: Boolean indicating preview mode

    Returns:
        Path to generated PDF file
    """
    paper_size = options.get('paper_size', 'A4')
    generator = LedgerPDFGenerator(paper_size=paper_size)
    return generator.generate_ledger_pdf(data, options, preview)
