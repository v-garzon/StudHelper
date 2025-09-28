import pytest
from app.services.auth_service import AuthService
from app.services.permission_service import PermissionService
from app.services.document_service import DocumentService
from app.services.usage_service import UsageService
from app.schemas import UserCreate

@pytest.mark.asyncio
async def test_auth_service_create_user(test_db):
    """Test user creation service"""
    auth_service = AuthService()
    user_data = UserCreate(
        email="service_test@example.com",
        username="servicetest",
        full_name="Service Test",
        password="testpassword"
    )
    
    user = await auth_service.create_user(test_db, user_data)
    assert user.email == user_data.email
    assert user.username == user_data.username

@pytest.mark.asyncio
async def test_permission_service_check_membership(test_db, test_user, test_class):
    """Test permission service membership check"""
    permission_service = PermissionService()
    
    # Should return None for non-member
    membership = await permission_service.get_user_membership(test_db, test_user.id, test_class.id)
    assert membership is None

@pytest.mark.asyncio
async def test_usage_service_get_stats(test_db, test_user, test_class):
    """Test usage service statistics"""
    # Add user to class
    from app.models import ClassMembership
    membership = ClassMembership(
        user_id=test_user.id,
        class_id=test_class.id
    )
    test_db.add(membership)
    test_db.commit()
    
    usage_service = UsageService()
    stats = await usage_service.get_user_class_usage(test_db, test_user.id, test_class.id)
    
    assert stats.daily_tokens_used >= 0
    assert stats.daily_limit > 0

