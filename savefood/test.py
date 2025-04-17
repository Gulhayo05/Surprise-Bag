# test.py
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt
from datetime import datetime, timedelta, UTC
import logging
import os

from main import app
from database import Base, get_db
from models import User, UserRole, SurpriseBag, Business
from routers.auth import (
    get_password_hash, 
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)

# Initialize TestClient
client = TestClient(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database setup - use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create tables once at module level
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def test_customer(db_session):
    try:
        user = User(
            id=uuid.uuid4(),
            email="customer@test.com",
            password_hash=get_password_hash("testpassword123"),
            name="Test Customer",
            phone="+1234567890",
            role=UserRole.customer,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        logger.debug(f"Test customer created: {user.email}")
        return user
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error creating test customer: {e}")
        raise e

@pytest.fixture
def test_business_owner(db_session):
    try:
        user = User(
            id=uuid.uuid4(),
            email="business@test.com",
            password_hash=get_password_hash("testpassword123"),
            name="Test Business",
            phone="+1234567890",
            role=UserRole.business_owner,
            is_active=True
        )
        db_session.add(user)
        
        business = Business(
            id=user.id,
            name="Test Business",
            description="Test description",
            address="Test address"
        )
        db_session.add(business)
        
        db_session.commit()
        db_session.refresh(user)
        logger.debug(f"Test business owner created: {user.email}")
        return user
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error creating test business owner: {e}")
        raise e

@pytest.fixture
def test_bag(db_session, test_business_owner):
    try:
        bag = SurpriseBag(
            id=uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
            business_id=test_business_owner.id,
            title="Test Bag",
            description="Test description",
            original_price=10.0,
            discount_price=5.0,
            quantity_available=10,
            quantity_sold=0,
            pickup_start=datetime.now(UTC),
            pickup_end=datetime.now(UTC) + timedelta(hours=1),
            is_active=True
        )
        db_session.add(bag)
        db_session.commit()
        db_session.refresh(bag)
        logger.debug(f"Test bag created: {bag.id}")
        return bag
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error creating test bag: {e}")
        raise e

def test_create_order(test_customer, test_bag, db_session):
    """Test creating an order"""
    try:
        # Override get_db dependency
        def override_get_db():
            try:
                yield db_session
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        
        # Verify customer exists in DB
        customer_check = db_session.query(User).filter(User.email == test_customer.email).first()
        logger.debug(f"Customer in DB before request: {customer_check.email if customer_check else 'None'}")
        
        # Create valid token
        token = create_access_token({"sub": test_customer.email})
        headers = {"Authorization": f"Bearer {token}"}
        logger.debug(f"Generated token: {token}")
        
        # Create order with UUID converted to string
        order_data = {
            "bag_id": str(test_bag.id),  # Convert UUID to string
            "quantity": 1
        }
        
        # Verify unauthorized access first
        unauth_response = client.post("/orders/", json=order_data)
        assert unauth_response.status_code == 401, f"Expected 401, got {unauth_response.status_code}"
        
        # Make authenticated request
        response = client.post("/orders/", json=order_data, headers=headers)
        logger.debug(f"Order creation response: {response.status_code} - {response.text}")
        
        # Verify response
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        response_data = response.json()
        assert response_data["customer_id"] == str(test_customer.id)
        assert response_data["bag_id"] == str(test_bag.id)
        assert response_data["status"] == "pending"
        assert "pickup_code" in response_data
        assert len(response_data["pickup_code"]) == 8
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise
    finally:
        # Cleanup
        app.dependency_overrides.clear()