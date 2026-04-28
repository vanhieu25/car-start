"""Test session timeout với QTimer."""
import pytest
from PyQt6.QtCore import QCoreApplication

from src.app.session import Session


def test_session_login_sets_user():
    """Test login lưu user."""
    session = Session(timeout_seconds=1800)
    user = {"id": 1, "username": "test", "role": "admin"}
    session.login(user)

    assert session.is_logged_in()
    assert session.user == user


def test_session_logout_clears_user():
    """Test logout xóa user."""
    session = Session(timeout_seconds=1800)
    session.login({"id": 1, "username": "test", "role": "admin"})
    session.logout()

    assert not session.is_logged_in()
    assert session.user is None


def test_session_is_admin():
    """Test kiểm tra admin role."""
    session = Session()
    assert not session.is_admin()

    session.login({"id": 1, "username": "admin", "role": "admin"})
    assert session.is_admin()

    session.login({"id": 2, "username": "user", "role": "nhan_vien"})
    assert not session.is_admin()
