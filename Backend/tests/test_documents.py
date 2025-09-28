import pytest
import io

def test_upload_class_document(client, auth_headers_teacher, test_class, sample_txt_file):
    """Test uploading a document to a class"""
    filename, content, content_type = sample_txt_file
    files = {"file": (filename, io.BytesIO(content), content_type)}
    
    response = client.post(
        f"/api/v1/documents/classes/{test_class.id}/upload",
        files=files,
        headers=auth_headers_teacher
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == filename
    assert data["file_type"] == "txt"

def test_upload_document_no_access(client, auth_headers_student, test_class, sample_txt_file):
    """Test uploading document without access"""
    filename, content, content_type = sample_txt_file
    files = {"file": (filename, io.BytesIO(content), content_type)}
    
    response = client.post(
        f"/api/v1/documents/classes/{test_class.id}/upload",
        files=files,
        headers=auth_headers_student
    )
    assert response.status_code == 403

def test_get_class_documents(client, auth_headers_teacher, test_class):
    """Test getting class documents"""
    response = client.get(
        f"/api/v1/documents/classes/{test_class.id}",
        headers=auth_headers_teacher
    )
    assert response.status_code == 200
    documents = response.json()
    assert isinstance(documents, list)

def test_upload_large_file(client, auth_headers_teacher, test_class):
    """Test uploading file that exceeds size limit"""
    # Create large file content
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {"file": ("large.txt", io.BytesIO(large_content), "text/plain")}
    
    response = client.post(
        f"/api/v1/documents/classes/{test_class.id}/upload",
        files=files,
        headers=auth_headers_teacher
    )
    assert response.status_code == 400

def test_upload_invalid_file_type(client, auth_headers_teacher, test_class):
    """Test uploading invalid file type"""
    files = {"file": ("test.exe", io.BytesIO(b"executable"), "application/octet-stream")}
    
    response = client.post(
        f"/api/v1/documents/classes/{test_class.id}/upload",
        files=files,
        headers=auth_headers_teacher
    )
    assert response.status_code == 400

