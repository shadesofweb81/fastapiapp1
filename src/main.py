import os
from pathlib import Path
from typing import Union
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from invoice_pdf_generator import generate_invoice_pdf
from models import TransactionPrintDto


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

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".pdf"}

# Mount the uploads directory for serving files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>File Manager</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .container {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .upload-section {
                margin-bottom: 30px;
                padding: 20px;
                background-color: #f9f9f9;
                border-radius: 5px;
            }
            .file-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .file-card {
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                text-align: center;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .file-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .file-preview {
                width: 100%;
                height: 200px;
                object-fit: cover;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            .pdf-icon {
                width: 100%;
                height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #e74c3c;
                color: white;
                font-size: 48px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            .file-name {
                font-weight: bold;
                margin-bottom: 10px;
                word-break: break-all;
            }
            .file-info {
                font-size: 12px;
                color: #666;
                margin-bottom: 10px;
            }
            .file-path {
                font-size: 11px;
                color: #999;
                margin-bottom: 5px;
                word-break: break-all;
                background-color: #f0f0f0;
                padding: 5px;
                border-radius: 3px;
                font-family: monospace;
                text-align: left;
            }
            .btn {
                padding: 8px 16px;
                margin: 5px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.2s;
            }
            .btn-download {
                background-color: #3498db;
                color: white;
            }
            .btn-download:hover {
                background-color: #2980b9;
            }
            .btn-upload {
                background-color: #2ecc71;
                color: white;
            }
            .btn-upload:hover {
                background-color: #27ae60;
            }
            .btn-refresh {
                background-color: #9b59b6;
                color: white;
            }
            .btn-refresh:hover {
                background-color: #8e44ad;
            }
            input[type="file"] {
                margin: 10px 0;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <h1>📁 File Manager - Images & PDFs</h1>
        <div class="container">
            <div class="upload-section">
                <h2>Upload Files</h2>
                <input type="file" id="fileInput" multiple accept=".jpg,.jpeg,.png,.gif,.bmp,.pdf">
                <button class="btn btn-upload" onclick="uploadFiles()">Upload</button>
                <button class="btn btn-refresh" onclick="loadFiles()">Refresh List</button>
                <div id="uploadStatus"></div>
            </div>
            
            <h2>Available Files</h2>
            <div id="fileGrid" class="file-grid">
                <div class="loading">Loading files...</div>
            </div>
        </div>

        <script>
            async function loadFiles() {
                try {
                    const response = await fetch('/files');
                    const data = await response.json();
                    const fileGrid = document.getElementById('fileGrid');
                    
                    if (data.files.length === 0) {
                        fileGrid.innerHTML = '<div class="loading">No files uploaded yet.</div>';
                        return;
                    }
                    
                    fileGrid.innerHTML = data.files.map(file => {
                        const isImage = file.type === 'image';
                        const baseUrl = window.location.origin;
                        return `
                            <div class="file-card">
                                ${isImage ? 
                                    `<img src="${baseUrl}/uploads/${file.filename}" class="file-preview" alt="${file.filename}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22><text x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22>Image Error</text></svg>'">` :
                                    `<div class="pdf-icon">📄</div>`
                                }
                                <div class="file-name">${file.filename}</div>
                                <div class="file-info">Size: ${file.size}</div>
                                <div class="file-path" title="${file.full_path}">📂 ${file.full_path}</div>
                                <div class="file-path" title="${baseUrl}${file.url_path}">🔗 ${baseUrl}${file.url_path}</div>
                                <button class="btn btn-download" onclick="downloadFile('${file.filename}')">Download</button>
                            </div>
                        `;
                    }).join('');
                } catch (error) {
                    console.error('Error loading files:', error);
                    document.getElementById('fileGrid').innerHTML = 
                        '<div class="loading">Error loading files.</div>';
                }
            }

            async function uploadFiles() {
                const fileInput = document.getElementById('fileInput');
                const files = fileInput.files;
                
                if (files.length === 0) {
                    alert('Please select files to upload');
                    return;
                }
                
                const formData = new FormData();
                for (let file of files) {
                    formData.append('files', file);
                }
                
                const statusDiv = document.getElementById('uploadStatus');
                statusDiv.innerHTML = '<p style="color: blue;">Uploading...</p>';
                
                try {
                    const response = await fetch('/upload/multiple/', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    statusDiv.innerHTML = `<p style="color: green;">✓ Uploaded ${result.uploaded_files.length} file(s) successfully!</p>`;
                    fileInput.value = '';
                    loadFiles();
                } catch (error) {
                    statusDiv.innerHTML = `<p style="color: red;">✗ Error uploading files: ${error.message}</p>`;
                }
            }

            function downloadFile(filename) {
                window.location.href = `/download/${filename}`;
            }

            // Load files on page load
            loadFiles();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


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


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload an image or PDF file
    Note: The form field name must be 'file'
    """
    # Check if file was provided
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Get file extension
    file_extension = Path(file.filename).suffix.lower()
    
    # Validate file type
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create a unique filename to avoid overwriting
    file_path = UPLOAD_DIR / file.filename
    counter = 1
    while file_path.exists():
        stem = Path(file.filename).stem
        file_path = UPLOAD_DIR / f"{stem}_{counter}{file_extension}"
        counter += 1
    
    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "filename": file_path.name,
            "file_path": str(file_path),
            "content_type": file.content_type,
            "size": len(content),
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")


@app.post("/upload/multiple/")
async def upload_multiple_files(files: list[UploadFile] = File(...)):
    """
    Upload multiple images or PDF files
    """
    uploaded_files = []
    
    for file in files:
        # Get file extension
        file_extension = Path(file.filename).suffix.lower()
        
        # Validate file type
        if file_extension not in ALLOWED_EXTENSIONS:
            uploaded_files.append({
                "filename": file.filename,
                "status": "error",
                "message": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            })
            continue
        
        # Create a unique filename
        file_path = UPLOAD_DIR / file.filename
        counter = 1
        while file_path.exists():
            stem = Path(file.filename).stem
            file_path = UPLOAD_DIR / f"{stem}_{counter}{file_extension}"
            counter += 1
        
        # Save the file
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append({
                "filename": file_path.name,
                "file_path": str(file_path),
                "content_type": file.content_type,
                "size": len(content),
                "status": "success"
            })
        except Exception as e:
            uploaded_files.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
    
    return {
        "total_files": len(files),
        "uploaded_files": uploaded_files
    }


@app.get("/files")
async def list_files():
    """
    List all uploaded images and PDFs with metadata
    """
    files = []
    
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            file_extension = file_path.suffix.lower()
            
            # Only include allowed file types
            if file_extension in ALLOWED_EXTENSIONS:
                file_size = file_path.stat().st_size
                
                # Format file size
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.2f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"
                
                # Determine file type
                file_type = "pdf" if file_extension == ".pdf" else "image"
                
                files.append({
                    "filename": file_path.name,
                    "size": size_str,
                    "type": file_type,
                    "extension": file_extension,
                    "full_path": str(file_path.absolute()),
                    "url_path": f"/uploads/{file_path.name}",
                    "download_url": f"/download/{file_path.name}"
                })
    
    # Sort by filename
    files.sort(key=lambda x: x["filename"])
    
    return {
        "total": len(files),
        "files": files
    }


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a specific file
    """
    file_path = UPLOAD_DIR / filename
    
    # Check if file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if it's a file (not a directory)
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Invalid file")
    
    # Determine media type
    extension = file_path.suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".pdf": "application/pdf"
    }
    
    media_type = media_type_map.get(extension, "application/octet-stream")
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )


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


@app.post("/generate-pdf")
async def generate_transaction_pdf(transaction_data: TransactionPrintDto, paper_size: str = "A4"):
    """
    Generate PDF for a transaction from the provided transaction data

    Args:
        transaction_data: The complete transaction data (TransactionPrintDto)
        paper_size: Paper size for PDF (A4 or A5), default is A4

    Returns:
        JSON with download link and file information
    """
    try:
        # Get transaction identifier for filename (use invoice number, transaction number, or timestamp)
        # Ensure we get a non-empty transaction_id
        transaction_id = (
            (transaction_data.transaction_header.invoice_number and
             transaction_data.transaction_header.invoice_number.strip()) or
            (transaction_data.transaction_header.transaction_number and
             transaction_data.transaction_header.transaction_number.strip()) or
            datetime.now().strftime('%Y%m%d_%H%M%S')
        )

        print(f"DEBUG: transaction_id = '{transaction_id}'")
        print(f"DEBUG: invoice_number = '{transaction_data.transaction_header.invoice_number}'")
        print(f"DEBUG: transaction_number = '{transaction_data.transaction_header.transaction_number}'")

        # Convert Pydantic model to dict for PDF generator
        # Use mode='json' to properly serialize UUID and Decimal types
        transaction_dict = transaction_data.model_dump(mode='json', by_alias=True)

        # Prepare PDF generation options
        filename = f"invoice_{transaction_id}.pdf"
        print(f"DEBUG: filename = '{filename}'")

        options = {
            'paper_size': paper_size,
            'save_file': True,
            'save_location': str(UPLOAD_DIR),
            'filename': filename,
            'copy_types': ["ORIGINAL"]
        }

        print(f"DEBUG: save_location = '{UPLOAD_DIR}'")

        # Generate PDF
        pdf_path = generate_invoice_pdf(transaction_dict, options, preview=False)
        pdf_file = Path(pdf_path)

        print(f"DEBUG: pdf_path = '{pdf_path}'")
        print(f"DEBUG: pdf_file.name = '{pdf_file.name}'")
        print(f"DEBUG: pdf_file.exists() = {pdf_file.exists()}")

        if not pdf_file.exists():
            raise HTTPException(status_code=500, detail="PDF generation failed")

        # Get file size
        file_size = pdf_file.stat().st_size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.2f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.2f} MB"

        print(f"DEBUG: file_size = {file_size}, size_str = '{size_str}'")

        # Construct download URL using the download_file endpoint
        # This ensures the URL is consistent with the download_file method
        download_url = f"/download/{pdf_file.name}"

        print(f"DEBUG: download_url = '{download_url}'")

        # Return download information with proper values
        response_data = {
            "status": "success",
            "message": "PDF generated successfully",
            "transaction_id": transaction_id,
            "filename": pdf_file.name,
            "file_size": size_str,
            "download_url": download_url,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8100)