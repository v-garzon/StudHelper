import pytest

def test_create_class(client, auth_headers_teacher):
    """Test creating a class"""
    class_data = {
        "name": "Physics 101",
        "description": "Introduction to Physics"
    }
    response = client.post("/api/v1/classes/", json=class_data, headers=auth_headers_teacher)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == class_data["name"]
    assert data["description"] == class_data["description"]
    assert "class_code" in data
    assert len(data["class_code"]) == 8

def test_get_user_classes(client, auth_headers_teacher, test_class):
    """Test getting user's classes"""
    response = client.get("/api/v1/classes/", headers=auth_headers_teacher)
    assert response.status_code == 200
    classes = response.json()
    assert isinstance(classes, list)
    assert len(classes) >= 1
    assert any(c["id"] == test_class.id for c in classes)

def test_join_class(client, auth_headers_student, test_class):
    """Test joining a class"""
    join_data = {"class_code": test_class.class_code}
    response = client.post("/api/v1/classes/join", json=join_data, headers=auth_headers_student)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_class.id

def test_join_class_invalid_code(client, auth_headers_student):
    """Test joining with invalid class code"""
    join_data = {"class_code": "INVALID"}
    response = client.post("/api/v1/classes/join", json=join_data, headers=auth_headers_student)
    assert response.status_code == 404

def test_join_class_already_member(client, auth_headers_student, test_class, test_db):
    """Test joining a class when already a member"""
    # First join
    join_data = {"class_code": test_class.class_code}
    response = client.post("/api/v1/classes/join", json=join_data, headers=auth_headers_student)
    assert response.status_code == 200
    
    # Try to join again
    response = client.post("/api/v1/classes/join", json=join_data, headers=auth_headers_student)
    assert response.status_code == 400

def test_get_class_details(client, auth_headers_teacher, test_class):
    """Test getting class details"""
    response = client.get(f"/api/v1/classes/{test_class.id}", headers=auth_headers_teacher)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_class.id
    assert data["name"] == test_class.name

def test_get_class_details_no_access(client, auth_headers_student, test_class):
    """Test getting class details without access"""
    response = client.get(f"/api/v1/classes/{test_class.id}", headers=auth_headers_student)
    assert response.status_code == 403

def test_delete_class(client, auth_headers_teacher, test_class):
    """Test deleting a class"""
    response = client.delete(f"/api/v1/classes/{test_class.id}", headers=auth_headers_teacher)
    assert response.status_code == 200

def test_delete_class_not_owner(client, auth_headers_student, test_class):
    """Test deleting a class when not owner"""
    response = client.delete(f"/api/v1/classes/{test_class.id}", headers=auth_headers_student)
    assert response.status_code == 404

