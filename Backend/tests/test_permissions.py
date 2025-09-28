import pytest

def test_get_class_members_as_manager(client, auth_headers_teacher, test_class):
    """Test getting class members as manager"""
    response = client.get(f"/api/v1/classes/{test_class.id}/members", headers=auth_headers_teacher)
    assert response.status_code == 200
    members = response.json()
    assert isinstance(members, list)
    assert len(members) >= 1

def test_get_class_members_not_manager(client, auth_headers_student, test_class, test_db):
    """Test getting class members when not manager"""
    # Join class first
    from app.models import ClassMembership
    membership = ClassMembership(
        user_id=1,  # Assuming student ID
        class_id=test_class.id,
        is_manager=False
    )
    test_db.add(membership)
    test_db.commit()
    
    response = client.get(f"/api/v1/classes/{test_class.id}/members", headers=auth_headers_student)
    assert response.status_code == 403

def test_update_member_permissions(client, auth_headers_teacher, test_class, test_user, test_db):
    """Test updating member permissions"""
    # Add user to class first
    from app.models import ClassMembership
    membership = ClassMembership(
        user_id=test_user.id,
        class_id=test_class.id,
        is_manager=False,
        can_chat=True,
        daily_token_limit=500000
    )
    test_db.add(membership)
    test_db.commit()
    
    # Update permissions
    update_data = {
        "can_chat": False,
        "daily_token_limit": 2000000
    }
    response = client.put(
        f"/api/v1/classes/{test_class.id}/members/{test_user.id}",
        json=update_data,
        headers=auth_headers_teacher
    )
    assert response.status_code == 200
    data = response.json()
    assert data["can_chat"] == False
    assert data["daily_token_limit"] == 2000000

def test_update_sponsorship(client, auth_headers_teacher, test_class):
    """Test updating class sponsorship"""
    sponsorship_data = {"is_sponsored": True}
    response = client.put(
        f"/api/v1/classes/{test_class.id}/sponsorship",
        json=sponsorship_data,
        headers=auth_headers_teacher
    )
    assert response.status_code == 200

def test_update_sponsorship_not_manager(client, auth_headers_student, test_class):
    """Test updating sponsorship when not manager"""
    sponsorship_data = {"is_sponsored": True}
    response = client.put(
        f"/api/v1/classes/{test_class.id}/sponsorship",
        json=sponsorship_data,
        headers=auth_headers_student
    )
    assert response.status_code == 403

