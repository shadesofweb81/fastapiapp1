from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException
from fastapi.responses import FileResponse

from pdf_generator import (
    generate_invoice_pdf,
    generate_invoice_pdf_a5,
    generate_invoice_pdf_template_1,
    generate_ledger_pdf
)
from models import TransactionPrintDto, LedgerPrintDto, PrintSettings, LedgerReportPrintSettings


class PDFService:
    """Service class for handling PDF operations"""

    def __init__(self, upload_dir: Path):
        """
        Initialize PDFService with upload directory

        Args:
            upload_dir: Path to the upload directory
        """
        self.upload_dir = upload_dir.absolute()
        self.upload_dir.mkdir(exist_ok=True)

    def generate_transaction_pdf(
        self,
        transaction_data: TransactionPrintDto,
        print_settings: PrintSettings = None
    ) -> Dict[str, Any]:
        """
        Generate PDF for a transaction from the provided transaction data

        Args:
            transaction_data: The complete transaction data
            print_settings: Print settings including paper size, copies, and document types

        Returns:
            Dictionary with download link and file information

        Raises:
            HTTPException: If PDF generation fails
        """
        try:
            # Use default print settings if not provided
            if print_settings is None:
                print_settings = PrintSettings()

            # Get transaction identifier for filename
            transaction_id = (
                (transaction_data.transaction_header.invoice_number and
                 transaction_data.transaction_header.invoice_number.strip()) or
                (transaction_data.transaction_header.transaction_number and
                 transaction_data.transaction_header.transaction_number.strip()) or
                "invoice"
            )

            # Sanitize transaction_id - remove invalid filename characters and spaces
            import re
            transaction_id = re.sub(r'[\\/:*?"<>|\s]+', '_', str(transaction_id)).strip('_')

            # Always append datetime to ensure each PDF is unique
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{transaction_id}_{timestamp}.pdf"

            print(f"DEBUG: transaction_id = '{transaction_id}'")
            print(f"DEBUG: timestamp = '{timestamp}'")
            print(f"DEBUG: invoice_number = '{transaction_data.transaction_header.invoice_number}'")
            print(f"DEBUG: transaction_number = '{transaction_data.transaction_header.transaction_number}'")
            print(f"DEBUG: filename = '{filename}'")

            # Convert Pydantic model to dict for PDF generator
            transaction_dict = transaction_data.model_dump(mode='json', by_alias=True)

            # Process document types
            base_copy_types = self._process_document_types(print_settings)

            # Get number of copies
            num_copies = self._get_number_of_copies(print_settings)

            # Repeat document types based on paper_copies
            copy_types = base_copy_types * num_copies

            print(f"DEBUG: document_types from request = {print_settings.document_type}")
            print(f"DEBUG: paper_copies = {print_settings.paper_copies}")
            print(f"DEBUG: num_copies = {num_copies}")
            print(f"DEBUG: base_copy_types = {base_copy_types}")
            print(f"DEBUG: copy_types for PDF = {copy_types}")

            # Prepare options for PDF generation
            options = {
                'paper_size': print_settings.paper_size,
                'save_file': True,
                'save_location': str(self.upload_dir),
                'filename': filename,
                'copy_types': copy_types
            }

            print(f"DEBUG: save_location = '{self.upload_dir}'")

            # Generate PDF based on paper_size and template
            template = getattr(print_settings, 'template', 'default').lower()
            
            if print_settings.paper_size.upper() == "A5":
                # A5 paper size
                pdf_path = generate_invoice_pdf_a5(transaction_dict, options, preview=False)
            elif template == "original":
                # Original A4 template
                pdf_path = generate_invoice_pdf(transaction_dict, options, preview=False)
            else:
                # Default A4 template (Template 1 - Busy style)
                pdf_path = generate_invoice_pdf_template_1(transaction_dict, options, preview=False)
            pdf_file = Path(pdf_path)

            print(f"DEBUG: pdf_path = '{pdf_path}'")
            print(f"DEBUG: pdf_file.name = '{pdf_file.name}'")
            print(f"DEBUG: pdf_file.exists() = {pdf_file.exists()}")

            if not pdf_file.exists():
                raise HTTPException(status_code=500, detail="PDF generation failed")

            # Get file size
            file_size = pdf_file.stat().st_size
            size_str = self._format_file_size(file_size)

            print(f"DEBUG: file_size = {file_size}, size_str = '{size_str}'")

            # Construct URLs
            download_url = f"/api/images/download/{pdf_file.name}"
            open_url = f"/api/pdf/open/{pdf_file.name}"

            print(f"DEBUG: download_url = '{download_url}'")
            print(f"DEBUG: open_url = '{open_url}'")

            # Return download information
            response_data = {
                "status": "success",
                "message": "PDF generated successfully",
                "transaction_id": transaction_id,
                "filename": pdf_file.name,
                "file_size": size_str,
                "download_url": download_url,
                "open_url": open_url,
                "full_path": str(pdf_file.absolute())
            }

            print(f"DEBUG: Response data = {response_data}")

            return response_data

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating PDF: {str(e)}"
            )

    def generate_ledger_pdf_report(
        self,
        ledger_data: LedgerPrintDto,
        print_settings: LedgerReportPrintSettings = None
    ) -> Dict[str, Any]:
        """
        Generate PDF for a ledger statement

        Args:
            ledger_data: The ledger data
            print_settings: Print settings for ledger report

        Returns:
            Dictionary with download link and file information

        Raises:
            HTTPException: If PDF generation fails
        """
        try:
            if print_settings is None:
                print_settings = LedgerReportPrintSettings()

            ledger_name = ledger_data.ledger_name or "ledger"
            import re
            safe_name = re.sub(r'[\\/:*?"<>|\s]+', '_', str(ledger_name)).strip('_')

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ledger_{safe_name}_{timestamp}.pdf"

            ledger_dict = ledger_data.model_dump(mode='json', by_alias=True)

            options = {
                'paper_size': print_settings.paper_size,
                'copies': print_settings.paper_copies,
                'show_items': print_settings.show_items,
                'show_narration': print_settings.show_narration,
                'show_balance': print_settings.show_balance,
                'save_file': True,
                'save_location': str(self.upload_dir),
                'filename': filename,
            }

            pdf_path = generate_ledger_pdf(ledger_dict, options, preview=False)
            pdf_file = Path(pdf_path)

            if not pdf_file.exists():
                raise HTTPException(status_code=500, detail="Ledger PDF generation failed")

            file_size = pdf_file.stat().st_size
            size_str = self._format_file_size(file_size)

            download_url = f"/api/images/download/{pdf_file.name}"
            open_url = f"/api/pdf/open/{pdf_file.name}"

            return {
                "status": "success",
                "message": "Ledger PDF generated successfully",
                "ledger_name": ledger_name,
                "filename": pdf_file.name,
                "file_size": size_str,
                "download_url": download_url,
                "open_url": open_url,
                "full_path": str(pdf_file.absolute())
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating ledger PDF: {str(e)}"
            )

    def open_pdf(self, filename: str) -> FileResponse:
        """
        Open a PDF file in the browser (inline viewing instead of download)

        Args:
            filename: Name of the PDF file to open

        Returns:
            FileResponse with the PDF file

        Raises:
            HTTPException: If file not found or invalid
        """
        file_path = self.upload_dir / filename

        # Check if file exists
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")

        # Check if it's a file (not a directory)
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Invalid file")

        # Verify it's a PDF file
        if file_path.suffix.lower() != ".pdf":
            raise HTTPException(status_code=400, detail="File is not a PDF")

        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=filename,
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )

    @staticmethod
    def _process_document_types(print_settings: PrintSettings) -> list:
        """
        Process document types from print settings

        Args:
            print_settings: Print settings

        Returns:
            List of document types in uppercase
        """
        base_copy_types = []
        if print_settings.document_type and len(print_settings.document_type) > 0:
            base_copy_types = [doc_type.upper() for doc_type in print_settings.document_type]
        else:
            base_copy_types = ["ORIGINAL"]

        return base_copy_types

    @staticmethod
    def _get_number_of_copies(print_settings: PrintSettings) -> int:
        """
        Get number of copies from print settings

        Args:
            print_settings: Print settings

        Returns:
            Number of copies (minimum 1)
        """
        try:
            num_copies = int(print_settings.paper_copies) if print_settings.paper_copies else 1
            if num_copies < 1:
                num_copies = 1
        except ValueError:
            num_copies = 1

        return num_copies

    @staticmethod
    def _format_file_size(file_size: int) -> str:
        """
        Format file size in human-readable format

        Args:
            file_size: File size in bytes

        Returns:
            Formatted file size string
        """
        if file_size < 1024:
            return f"{file_size} B"
        elif file_size < 1024 * 1024:
            return f"{file_size / 1024:.2f} KB"
        else:
            return f"{file_size / (1024 * 1024):.2f} MB"
