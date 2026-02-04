from pathlib import Path
from typing import Union
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from models import TransactionPrintDto, LedgerPrintDto, PrintSettings, LedgerReportPrintSettings
from services import FileService, PDFService, UIService


app = FastAPI()

# Add CORS middleware to allow Vue.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Vue.js app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize services
file_service = FileService(UPLOAD_DIR)
pdf_service = PDFService(UPLOAD_DIR)
ui_service = UIService()

# Mount the uploads directory for serving files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def read_root():
    """
    Home page - returns basic API information
    """
    return {
        "name": "FastAPI PDF & Image Service",
        "version": "1.0.0",
        "endpoints": {
            "images": "/api/images/",
            "pdf": "/api/pdf/",
            "pdf_open": "/api/pdf/open/{filename}",
            "upload_ui": "/upload",
            "health": "/health"
        }
    }


@app.get("/upload", response_class=HTMLResponse)
def upload_page():
    """
    HTML file upload and management interface
    """
    return ui_service.get_upload_page()


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Docker and monitoring
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/images/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload an image or PDF file
    Note: The form field name must be 'file'
    """
    return await file_service.upload_single_file(file)


@app.post("/api/images/upload/multiple/")
async def upload_multiple_files(files: list[UploadFile] = File(...)):
    """
    Upload multiple images or PDF files
    """
    return await file_service.upload_multiple_files(files)


@app.get("/api/images/files")
async def list_files():
    """
    List all uploaded images and PDFs with metadata
    """
    return file_service.list_files()


@app.get("/api/images/download/{filename}")
async def download_file(filename: str):
    """
    Download a specific file
    """
    return file_service.download_file(filename)


@app.get("/api/pdf/open/{filename}")
async def open_pdf(filename: str):
    """
    Open a PDF file in the browser (inline viewing instead of download)
    """
    return pdf_service.open_pdf(filename)


@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """
    Custom handler for 422 errors to provide better error messages
    """
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error. Make sure you're sending the file with field name 'file' for single upload or 'files' for multiple uploads.",
            "error": str(exc)
        }
    )


@app.post("/api/pdf/generate-pdf")
async def generate_transaction_pdf(
    transaction_data: TransactionPrintDto = Body(...),
    print_settings: PrintSettings = Body(default=None)
):
    """
    Generate PDF for a transaction from the provided transaction data

    Args:
        transaction_data: The complete transaction data (TransactionPrintDto)
        print_settings: Print settings including paper size, copies, and document types (PrintSettings)

    Returns:
        JSON with download link and file information
    """
    return pdf_service.generate_transaction_pdf(transaction_data, print_settings)


@app.post("/api/pdf/generate-ledger-pdf")
async def generate_ledger_pdf(
    ledger_data: LedgerPrintDto = Body(...),
    print_settings: LedgerReportPrintSettings = Body(default=None)
):
    """
    Generate PDF for a ledger statement from the provided ledger data

    Args:
        ledger_data: The complete ledger data (LedgerPrintDto)
        print_settings: Print settings including paper size, copies, and display options (LedgerReportPrintSettings)
            - copies: Number of copies (default: 1)
            - printSize: Paper size A4/A5 (default: A4)
            - showItems: Show transaction items (default: true)
            - showNarration: Show narration/notes (default: true)
            - showBalance: Show balance column (default: true)
            - savePath: Path to save the PDF

    Returns:
        JSON with download link and file information
    """
    return pdf_service.generate_ledger_pdf_report(ledger_data, print_settings)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)