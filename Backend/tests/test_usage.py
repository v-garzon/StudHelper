import pytest

def test_get_my_usage(client, auth_headers_student, test_class, test_db):
    """Test getting personal usage statistics"""
    # Create membership first
    from app.models import ClassMembership
    membership = ClassMembership(
        user_id=1,
        class_id=test_class.id
    )
    test_db.add(membership)
    test_db.commit()
    
    response = client.get("/api/v1/usage/my-usage", headers=auth_headers_student)
    assert response.status_code == 200
    usage = response.json()
    assert isinstance(usage, list)

def test_get_class_usage_overview(client, auth_headers_teacher, test_class):
    """Test getting class usage overview as manager"""
    response = client.get(
        f"/api/v1/usage/classes/{test_class.id}/members",
        headers=auth_headers_teacher
    )
    assert response.status_code == 200
    overview = response.json()
    assert isinstance(overview, list)

def test_get_class_usage_not_manager(client, auth_headers_student, test_class):
    """Test getting class usage when not manager"""
    response = client.get(
        f"/api/v1/usage/classes/{test_class.id}/members",
        headers=auth_headers_student
    )
    assert response.status_code == 403

def test_update_user_limits(client, auth_headers_teacher, test_class, test_user, test_db):
    """Test updating user token limits"""
    # Add user to class
    from app.models import ClassMembership
    membership = ClassMembership(
        user_id=test_user.id,
        class_id=test_class.id
    )
    test_db.add(membership)
    test_db.commit()
    
    response = client.put(
        f"/api/v1/usage/classes/{test_class.id}/limits/{test_user.id}?daily_limit=2000000&weekly_limit=10000000&monthly_limit=30000000",
        headers=auth_headers_teacher
    )
    assert response.status_code == 200

