import os
from pathlib import Path
from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse


class FileService:
    """Service class for handling file operations"""

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".pdf"}

    def __init__(self, upload_dir: Path):
        """
        Initialize FileService with upload directory

        Args:
            upload_dir: Path to the upload directory
        """
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(exist_ok=True)

    def _validate_file_extension(self, filename: str) -> str:
        """
        Validate file extension

        Args:
            filename: Name of the file

        Returns:
            File extension in lowercase

        Raises:
            HTTPException: If file extension is not allowed
        """
        file_extension = Path(filename).suffix.lower()

        if file_extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        return file_extension

    def _get_unique_filepath(self, filename: str) -> Path:
        """
        Generate a unique file path to avoid overwriting existing files

        Args:
            filename: Original filename

        Returns:
            Unique file path
        """
        file_extension = Path(filename).suffix.lower()
        file_path = self.upload_dir / filename
        counter = 1

        while file_path.exists():
            stem = Path(filename).stem
            file_path = self.upload_dir / f"{stem}_{counter}{file_extension}"
            counter += 1

        return file_path

    async def upload_single_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Upload a single file

        Args:
            file: The file to upload

        Returns:
            Dictionary with file information

        Raises:
            HTTPException: If file upload fails
        """
        # Check if file was provided
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Validate file type
        file_extension = self._validate_file_extension(file.filename)

        # Get unique file path
        file_path = self._get_unique_filepath(file.filename)

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

    async def upload_multiple_files(self, files: List[UploadFile]) -> Dict[str, Any]:
        """
        Upload multiple files

        Args:
            files: List of files to upload

        Returns:
            Dictionary with upload results
        """
        uploaded_files = []

        for file in files:
            # Get file extension
            file_extension = Path(file.filename).suffix.lower()

            # Validate file type
            if file_extension not in self.ALLOWED_EXTENSIONS:
                uploaded_files.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": f"File type not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}"
                })
                continue

            # Get unique file path
            file_path = self._get_unique_filepath(file.filename)

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

    def list_files(self) -> Dict[str, Any]:
        """
        List all uploaded files with metadata

        Returns:
            Dictionary with file list and count
        """
        files = []

        for file_path in self.upload_dir.iterdir():
            if file_path.is_file():
                file_extension = file_path.suffix.lower()

                # Only include allowed file types
                if file_extension in self.ALLOWED_EXTENSIONS:
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
                        "download_url": f"/api/images/download/{file_path.name}"
                    })

        # Sort by filename
        files.sort(key=lambda x: x["filename"])

        return {
            "total": len(files),
            "files": files
        }

    def download_file(self, filename: str) -> FileResponse:
        """
        Download a specific file

        Args:
            filename: Name of the file to download

        Returns:
            FileResponse with the file

        Raises:
            HTTPException: If file not found or invalid
        """
        file_path = self.upload_dir / filename

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

    @staticmethod
    def format_file_size(file_size: int) -> str:
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
