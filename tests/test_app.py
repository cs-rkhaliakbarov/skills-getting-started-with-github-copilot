from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


BASELINE_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture
def client():
    original_activities = app_module.activities
    app_module.activities = deepcopy(BASELINE_ACTIVITIES)

    try:
        with TestClient(app_module.app) as test_client:
            yield test_client
    finally:
        app_module.activities = original_activities


def test_get_activities_returns_participants(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "michael@mergington.edu" in response.json()["Chess Club"]["participants"]


def test_signup_adds_participant(client):
    email = "student@example.com"
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = "michael@mergington.edu"

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404


def test_unregister_removes_participant(client):
    email = "michael@mergington.edu"

    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404


def test_unregister_rejects_unregistered_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404