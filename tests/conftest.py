import pytest
from app import app, db, User, Completion


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # create a default user
            user = User(username="testuser", is_admin=False)
            user.set_password("password")
            db.session.add(user)

            # admin user
            admin = User(username="admin", is_admin=True)
            admin.set_password("adminpass")
            db.session.add(admin)

            db.session.commit()

        yield client

        with app.app_context():
            db.drop_all()