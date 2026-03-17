import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_get_root_redirect(client):
    """Test that GET / redirects to the static index page."""
    # Arrange: No special setup needed

    # Act: Make GET request to root without following redirects
    response = client.get("/", follow_redirects=False)

    # Assert: Should redirect to /static/index.html
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test that GET /activities returns all activities."""
    # Arrange: No special setup needed

    # Act: Make GET request to activities endpoint
    response = client.get("/activities")

    # Assert: Should return 200 and contain activity data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange: Use an activity and a new email
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 200 and success message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" in data["message"]


def test_signup_duplicate(client):
    """Test signup fails when student is already signed up."""
    # Arrange: First sign up a student
    activity_name = "Programming Class"
    email = "testduplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Try to sign up the same student again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 400 with error message
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity(client):
    """Test signup fails for non-existent activity."""
    # Arrange: Use invalid activity name
    activity_name = "NonExistent Club"
    email = "student@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 404 with error message
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_success(client):
    """Test successful unregistration from an activity."""
    # Arrange: First sign up a student, then unregister
    activity_name = "Gym Class"
    email = "testunregister@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 200 and success message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from {activity_name}" in data["message"]


def test_unregister_not_signed_up(client):
    """Test unregister fails when student is not signed up."""
    # Arrange: Use an activity and email not signed up
    activity_name = "Basketball Team"
    email = "notsignedup@mergington.edu"

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 400 with error message
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_unregister_invalid_activity(client):
    """Test unregister fails for non-existent activity."""
    # Arrange: Use invalid activity name
    activity_name = "Invalid Activity"
    email = "student@mergington.edu"

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 404 with error message
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]