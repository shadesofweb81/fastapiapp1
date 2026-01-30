from fastapi.responses import HTMLResponse


class UIService:
    """Service class for handling UI/HTML content"""

    @staticmethod
    def get_upload_page() -> HTMLResponse:
        """
        Generate HTML file upload and management interface

        Returns:
            HTMLResponse with the upload page
        """
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
                    const response = await fetch('/api/images/files');
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
                    const response = await fetch('/api/images/upload/multiple/', {
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
                window.location.href = `/api/images/download/${filename}`;
            }

            // Load files on page load
            loadFiles();
        </script>
    </body>
    </html>
    """
        return HTMLResponse(content=html_content)
