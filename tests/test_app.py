import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly games",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ella@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act, direct, and produce school plays and performances",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu", "jack@mergington.edu"]
        },
        "Mathletes": {
            "description": "Compete in math competitions and solve challenging problems",
            "schedule": "Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["oliver@mergington.edu", "charlotte@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["henry@mergington.edu", "amelia@mergington.edu"]
        }
    })
    yield
    activities.clear()


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have the correct structure."""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_participants_count(self, client):
        """Test that activities have the correct number of participants."""
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 2
        assert len(data["Programming Class"]["participants"]) == 2


class TestSignUp:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant(self, client):
        """Test signing up a new participant."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup adds the participant to the activity."""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert "newstudent@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 3

    def test_signup_duplicate_participant_fails(self, client):
        """Test that signing up the same participant twice fails."""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails."""
        response = client.post(
            "/activities/NonExistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_case_insensitive_email(self, client):
        """Test that signup handles email case-insensitively."""
        response = client.post(
            "/activities/Chess Club/signup?email=NewStudent@MERGINGTON.EDU"
        )
        assert response.status_code == 200
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert any("newstudent@mergington.edu" in p.lower() 
                   for p in chess_club["participants"])


class TestUnregister:
    """Tests for the POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant."""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes the participant from the activity."""
        client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert "michael@mergington.edu" not in chess_club["participants"]
        assert len(chess_club["participants"]) == 1

    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering a non-existent participant fails."""
        response = client.post(
            "/activities/Chess Club/unregister?email=notasignup@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregistering from a non-existent activity fails."""
        response = client.post(
            "/activities/NonExistent Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_case_insensitive_email(self, client):
        """Test that unregister handles email case-insensitively."""
        response = client.post(
            "/activities/Chess Club/unregister?email=MICHAEL@MERGINGTON.EDU"
        )
        assert response.status_code == 200
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert "michael@mergington.edu" not in chess_club["participants"]


class TestIntegration:
    """Integration tests for signup and unregister flows."""

    def test_signup_then_unregister_flow(self, client):
        """Test the complete flow of signing up and then unregistering."""
        # Sign up
        response = client.post(
            "/activities/Chess Club/signup?email=testuser@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert "testuser@mergington.edu" in chess_club["participants"]
        initial_count = len(chess_club["participants"])
        
        # Unregister
        response = client.post(
            "/activities/Chess Club/unregister?email=testuser@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert "testuser@mergington.edu" not in chess_club["participants"]
        assert len(chess_club["participants"]) == initial_count - 1

    def test_multiple_participants_signup(self, client):
        """Test that multiple participants can sign up for the same activity."""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/Chess Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        for email in emails:
            assert email in chess_club["participants"]
        assert len(chess_club["participants"]) == 5  # 2 original + 3 new
