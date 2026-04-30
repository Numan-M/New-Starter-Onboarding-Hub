import pytest
from app import create_app, db
from app import User


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        FEATURE_ADMIN_ENABLED=True,,
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        db.create_all()

        # seed users
        user = User(username="testuser", is_admin=False)
        user.set_password("password")

        admin = User(username="admin", is_admin=True)
        admin.set_password("adminpass")

        db.session.add_all([user, admin])
        db.session.commit()

    yield app

    # teardown (THIS ONLY AFFECTS SQLITE TEST DB)
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()