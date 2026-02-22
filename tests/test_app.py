import pytest
from app import app, db
from models import Contact


# ----------------------------
# Fixtures
# ----------------------------
@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def sample_contact():
    contact = Contact(
        name="John Doe",
        phone="1234567890",
        email="john@example.com",
        type="Personal"
    )
    db.session.add(contact)
    db.session.commit()
    return contact


# ----------------------------
# Basic Route Tests
# ----------------------------
def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_add_contact_page(client):
    response = client.get("/add")
    assert response.status_code == 200


# ----------------------------
# CRUD Functionality Tests
# ----------------------------
def test_create_contact(client):
    response = client.post(
        "/add",
        data={
            "name": "Alice",
            "phone": "9876543210",
            "email": "alice@example.com",
            "type": "Work"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    # after adding, app redirects to /contacts
    assert b"Alice" in response.data


def test_read_contact(client, sample_contact):
    # contacts are displayed on /contacts (not /)
    response = client.get("/contacts")
    assert response.status_code == 200
    assert b"John Doe" in response.data


def test_update_contact(client, sample_contact):
    # update route is /update/<id> (not /edit/<id>)
    response = client.post(
        f"/update/{sample_contact.id}",
        data={
            "name": "John Updated",
            "phone": "1111111111",
            "email": "john_updated@example.com",
            "type": "Work"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    # after updating, app redirects to /contacts
    assert b"John Updated" in response.data


def test_delete_contact(client, sample_contact):
    response = client.get(
        f"/delete/{sample_contact.id}",
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"John Doe" not in response.data