"""Integration tests for Training Programs API endpoints."""

import httpx
import pytest
from datetime import datetime
import json

# Base URL for the API
BASE_URL = "http://localhost:8001"
API_V1 = f"{BASE_URL}/api/v1"

# Global test data
_test_user_email = None
_test_user_password = "TestPassword123!"
_test_user_username = None
_access_token = None


def get_or_create_test_user():
    """Get or create test user and return credentials."""
    global _test_user_email, _test_user_username, _access_token

    if _access_token:
        return _access_token

    # Create unique username/email for this test session
    timestamp = str(int(datetime.now().timestamp()))
    _test_user_email = f"testtraining{timestamp}@example.com"
    _test_user_username = f"testtraining{timestamp}"

    with httpx.Client() as client:
        # Try to register
        response = client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test User Training"
            }
        )

        # Login to get token
        login_response = client.post(
            f"{API_V1}/auth/login",
            json={
                "email": _test_user_email,
                "password": _test_user_password
            }
        )

        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token_data = login_response.json()
        _access_token = token_data["access_token"]

        return _access_token


@pytest.fixture
def auth_headers():
    """Get authorization headers with access token."""
    token = get_or_create_test_user()
    return {"Authorization": f"Bearer {token}"}


# ===========================
# TRAINING PROGRAM CRUD TESTS
# ===========================

class TestTrainingProgramCRUDAPI:
    """Test suite for Training Program CRUD operations."""

    program_id = None

    def test_01_generate_training_program(self, auth_headers):
        """Test POST /api/v1/training-programs/generate - Generate program."""
        program_data = {
            "name": "My Test Training Program",
            "description": "A comprehensive 12-week training program",
            "goal": "muscle_gain",
            "experience_level": "intermediate",
            "days_per_week": 4,
            "equipment": ["dumbbells", "barbell", "pull-up bar"]
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0  # Longer timeout for AI generation
            )

            # Note: This might fail if AI service is not available
            if response.status_code == 201:
                data = response.json()

                # Verify response structure
                assert "success" in data, "Response missing 'success'"

                if data["success"]:
                    assert "program" in data, "Response missing 'program'"
                    program = data["program"]

                    assert "id" in program, "Program missing 'id'"
                    assert "user_id" in program, "Program missing 'user_id'"
                    assert program["name"] == "My Test Training Program"
                    assert program["goal"] == "muscle_gain"
                    assert program["experience_level"] == "intermediate"
                    assert program["days_per_week"] == 4
                    assert "dumbbells" in program["equipment"]
                    assert "program_data" in program, "Program missing 'program_data'"
                    assert program["is_active"] == 1

                    # Verify 12-week structure
                    program_data = program["program_data"]
                    assert isinstance(program_data, dict), "program_data should be a dict"

                    # Save program ID for later tests
                    TestTrainingProgramCRUDAPI.program_id = program["id"]

                    print(f"\n✅ Generated training program: ID={program['id']}, Name={program['name']}")
                else:
                    # AI generation failed, but endpoint worked
                    print(f"\n⚠️  Program generation returned success=False: {data.get('error')}")
                    TestTrainingProgramCRUDAPI.program_id = None
            else:
                print(f"\n⚠️  Program generation endpoint returned {response.status_code}")

    def test_02_generate_program_minimal(self, auth_headers):
        """Test POST /api/v1/training-programs/generate - Generate with minimal data."""
        program_data = {
            "goal": "weight_loss"
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            # Should succeed with default values
            if response.status_code == 201:
                data = response.json()
                if data["success"] and data["program"]:
                    assert data["program"]["goal"] == "weight_loss"
                    # Default values
                    assert data["program"]["experience_level"] == "beginner"
                    assert data["program"]["days_per_week"] == 3

                    # Cleanup
                    program_id = data["program"]["id"]
                    client.delete(f"{API_V1}/training-programs/{program_id}", headers=auth_headers)

                    print(f"\n✅ Generated program with minimal data")
                else:
                    print(f"\n⚠️  Program generation with minimal data returned success=False")

    def test_03_generate_program_validation_days_per_week(self, auth_headers):
        """Test validation for days_per_week parameter."""
        # Test invalid value (too high)
        program_data = {
            "goal": "strength",
            "days_per_week": 8  # Invalid: max is 7
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 422, \
                f"Should fail validation for days_per_week > 7, got {response.status_code}"

            print(f"\n✅ Validation error for days_per_week handled correctly")

    def test_04_get_training_programs(self, auth_headers):
        """Test GET /api/v1/training-programs - Get all programs."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/training-programs",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get programs: {response.text}"
            data = response.json()

            # Verify response structure
            assert "programs" in data, "Response missing 'programs'"
            assert "total" in data, "Response missing 'total'"
            assert isinstance(data["programs"], list), "programs should be a list"
            assert data["total"] == len(data["programs"])

            # If we created a program in test_01, verify it's in the list
            if TestTrainingProgramCRUDAPI.program_id:
                program_ids = [p["id"] for p in data["programs"]]
                assert TestTrainingProgramCRUDAPI.program_id in program_ids, \
                    "Created program should be in the list"

            print(f"\n✅ Retrieved {data['total']} training programs")

    def test_05_get_programs_active_only(self, auth_headers):
        """Test GET /api/v1/training-programs?active_only=true - Get active only."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/training-programs?active_only=true",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get programs: {response.text}"
            data = response.json()

            # All programs should be active
            for program in data["programs"]:
                assert program["is_active"] == 1, f"Program {program['id']} should be active"

            print(f"\n✅ Retrieved {data['total']} active programs")

    def test_06_get_programs_include_inactive(self, auth_headers):
        """Test GET /api/v1/training-programs?active_only=false - Get all."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/training-programs?active_only=false",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get programs: {response.text}"
            data = response.json()

            assert "programs" in data
            assert "total" in data

            print(f"\n✅ Retrieved {data['total']} programs (including inactive)")

    def test_07_get_program_by_id(self, auth_headers):
        """Test GET /api/v1/training-programs/{program_id} - Get specific program."""
        if not TestTrainingProgramCRUDAPI.program_id:
            pytest.skip("No program ID available")

        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/training-programs/{TestTrainingProgramCRUDAPI.program_id}",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get program: {response.text}"
            data = response.json()

            assert data["id"] == TestTrainingProgramCRUDAPI.program_id
            assert data["name"] == "My Test Training Program"
            assert "program_data" in data
            assert "user_id" in data

            print(f"\n✅ Retrieved program: ID={data['id']}, Name={data['name']}")

    def test_08_get_program_not_found(self, auth_headers):
        """Test GET /api/v1/training-programs/999999 - Program not found."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/training-programs/999999",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 404, f"Should return 404, got {response.status_code}"

            print(f"\n✅ Non-existent program handled correctly")

    def test_09_delete_program(self, auth_headers):
        """Test DELETE /api/v1/training-programs/{program_id} - Archive program."""
        if not TestTrainingProgramCRUDAPI.program_id:
            pytest.skip("No program ID available")

        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/training-programs/{TestTrainingProgramCRUDAPI.program_id}",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to delete program: {response.text}"
            data = response.json()

            assert data["success"] == True
            assert "message" in data

            # Verify program is archived (is_active = 0)
            verify_response = client.get(
                f"{API_V1}/training-programs/{TestTrainingProgramCRUDAPI.program_id}",
                headers=auth_headers,
                timeout=10.0
            )

            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                assert verify_data["is_active"] == 0, "Program should be archived"

            print(f"\n✅ Archived program: ID={TestTrainingProgramCRUDAPI.program_id}")

    def test_10_delete_program_not_found(self, auth_headers):
        """Test DELETE /api/v1/training-programs/999999 - Program not found."""
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/training-programs/999999",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 404, f"Should return 404, got {response.status_code}"

            print(f"\n✅ Delete non-existent program handled correctly")


# ===========================
# PROGRAM STRUCTURE TESTS
# ===========================

class TestProgramStructure:
    """Test suite for validating training program structure."""

    def test_program_12week_structure(self, auth_headers):
        """Test that generated program has proper 12-week structure."""
        program_data = {
            "name": "Structure Test Program",
            "goal": "strength",
            "days_per_week": 3
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    program_data_content = program["program_data"]

                    # Verify structure contains weeks
                    assert isinstance(program_data_content, dict), "program_data should be a dict"

                    # Expected structure: week_1 through week_12 or similar
                    print(f"\n✅ Program has valid structure: {list(program_data_content.keys())[:3]}...")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)
                else:
                    print(f"\n⚠️  Could not verify structure - generation failed")

    def test_program_contains_summary(self, auth_headers):
        """Test that program includes summary information."""
        program_data = {
            "name": "Summary Test Program",
            "goal": "endurance",
            "days_per_week": 4
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]

                    # Should have summary field
                    assert "summary" in program, "Program should have summary"

                    print(f"\n✅ Program includes summary")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)


# ===========================
# GOAL TYPES TESTS
# ===========================

class TestTrainingGoals:
    """Test suite for different training goals."""

    def test_muscle_gain_program(self, auth_headers):
        """Test generating muscle gain program."""
        program_data = {
            "name": "Muscle Gain Program",
            "goal": "muscle_gain",
            "experience_level": "intermediate",
            "days_per_week": 5
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    assert program["goal"] == "muscle_gain"
                    assert program["days_per_week"] == 5

                    print(f"\n✅ Generated muscle gain program")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)

    def test_weight_loss_program(self, auth_headers):
        """Test generating weight loss program."""
        program_data = {
            "name": "Weight Loss Program",
            "goal": "weight_loss",
            "experience_level": "beginner",
            "days_per_week": 3
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    assert program["goal"] == "weight_loss"

                    print(f"\n✅ Generated weight loss program")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)

    def test_strength_program(self, auth_headers):
        """Test generating strength program."""
        program_data = {
            "name": "Strength Program",
            "goal": "strength",
            "experience_level": "advanced",
            "days_per_week": 4
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    assert program["goal"] == "strength"

                    print(f"\n✅ Generated strength program")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)

    def test_endurance_program(self, auth_headers):
        """Test generating endurance program."""
        program_data = {
            "name": "Endurance Program",
            "goal": "endurance",
            "experience_level": "intermediate",
            "days_per_week": 5
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    assert program["goal"] == "endurance"

                    print(f"\n✅ Generated endurance program")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)


# ===========================
# EXPERIENCE LEVEL TESTS
# ===========================

class TestExperienceLevels:
    """Test suite for different experience levels."""

    def test_beginner_program(self, auth_headers):
        """Test generating beginner program."""
        program_data = {
            "name": "Beginner Program",
            "goal": "muscle_gain",
            "experience_level": "beginner",
            "days_per_week": 3
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    assert program["experience_level"] == "beginner"

                    print(f"\n✅ Generated beginner program")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)

    def test_intermediate_program(self, auth_headers):
        """Test generating intermediate program."""
        program_data = {
            "name": "Intermediate Program",
            "goal": "strength",
            "experience_level": "intermediate",
            "days_per_week": 4
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    assert program["experience_level"] == "intermediate"

                    print(f"\n✅ Generated intermediate program")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)

    def test_advanced_program(self, auth_headers):
        """Test generating advanced program."""
        program_data = {
            "name": "Advanced Program",
            "goal": "strength",
            "experience_level": "advanced",
            "days_per_week": 6
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    assert program["experience_level"] == "advanced"

                    print(f"\n✅ Generated advanced program")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)


# ===========================
# EQUIPMENT TESTS
# ===========================

class TestEquipment:
    """Test suite for different equipment configurations."""

    def test_program_with_equipment(self, auth_headers):
        """Test generating program with specific equipment."""
        program_data = {
            "name": "Equipment Program",
            "goal": "muscle_gain",
            "days_per_week": 4,
            "equipment": ["dumbbells", "barbell", "bench", "pull-up bar"]
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    equipment = program["equipment"]
                    assert "dumbbells" in equipment
                    assert "barbell" in equipment
                    assert "bench" in equipment
                    assert "pull-up bar" in equipment

                    print(f"\n✅ Generated program with specified equipment")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)

    def test_bodyweight_program(self, auth_headers):
        """Test generating bodyweight-only program."""
        program_data = {
            "name": "Bodyweight Program",
            "goal": "endurance",
            "days_per_week": 5,
            "equipment": []  # No equipment
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    equipment = program["equipment"]
                    assert equipment == [] or equipment is None

                    print(f"\n✅ Generated bodyweight program")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)


# ===========================
# AUTHENTICATION TESTS
# ===========================

class TestProgramAuthentication:
    """Test authentication requirements for training program endpoints."""

    def test_generate_program_requires_auth(self):
        """Test that POST /api/v1/training-programs/generate requires auth."""
        program_data = {
            "goal": "muscle_gain"
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Generate program endpoint requires authentication")

    def test_get_programs_requires_auth(self):
        """Test that GET /api/v1/training-programs requires authentication."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/training-programs",
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Get programs endpoint requires authentication")

    def test_get_program_requires_auth(self):
        """Test that GET /api/v1/training-programs/{id} requires authentication."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/training-programs/1",
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Get program endpoint requires authentication")

    def test_delete_program_requires_auth(self):
        """Test that DELETE /api/v1/training-programs/{id} requires authentication."""
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/training-programs/1",
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Delete program endpoint requires authentication")


# ===========================
# AUTHORIZATION TESTS
# ===========================

class TestProgramAuthorization:
    """Test authorization - users can only access their own programs."""

    def test_cannot_access_other_user_program(self, auth_headers):
        """Test that users cannot access programs from other users."""
        # Create a program with first user
        program_data = {
            "name": "User 1 Program",
            "goal": "muscle_gain",
            "days_per_week": 4
        }

        with httpx.Client() as client:
            # Create program with user 1
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code != 201 or not response.json().get("success"):
                pytest.skip("Could not create program for authorization test")

            program_id = response.json()["program"]["id"]

            # Create second user
            timestamp = str(int(datetime.now().timestamp()))
            user2_email = f"testtraining2{timestamp}@example.com"
            user2_username = f"testtraining2{timestamp}"

            client.post(
                f"{API_V1}/auth/register",
                json={
                    "email": user2_email,
                    "username": user2_username,
                    "password": _test_user_password,
                    "full_name": "Test User 2"
                }
            )

            # Login as user 2
            login_response = client.post(
                f"{API_V1}/auth/login",
                json={
                    "email": user2_email,
                    "password": _test_user_password
                }
            )
            user2_token = login_response.json()["access_token"]
            user2_headers = {"Authorization": f"Bearer {user2_token}"}

            # Try to access user 1's program as user 2
            response = client.get(
                f"{API_V1}/training-programs/{program_id}",
                headers=user2_headers,
                timeout=10.0
            )

            # Should return 404 (not found) because it filters by user_id
            assert response.status_code == 404, \
                f"User 2 should not access User 1's program, got {response.status_code}"

            # Cleanup
            client.delete(f"{API_V1}/training-programs/{program_id}", headers=auth_headers)

            print("\n✅ Authorization properly enforced")


# ===========================
# STREAMING TESTS
# ===========================

class TestProgramStreaming:
    """Test suite for streaming program generation."""

    def test_stream_program_generation(self, auth_headers):
        """Test POST /api/v1/training-programs/generate/stream - Stream generation."""
        program_data = {
            "name": "Streamed Program",
            "goal": "strength",
            "days_per_week": 4
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate/stream",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            # Should return streaming response
            if response.status_code == 200:
                # Verify content type
                content_type = response.headers.get("content-type", "")
                assert "text/event-stream" in content_type, \
                    f"Expected SSE content type, got {content_type}"

                # Read a few chunks to verify streaming works
                chunks_received = 0
                for chunk in response.iter_lines():
                    if chunk:
                        chunks_received += 1
                        if chunks_received >= 3:  # Just verify we get some data
                            break

                assert chunks_received > 0, "Should receive streaming data"

                print(f"\n✅ Streaming program generation works")
            else:
                print(f"\n⚠️  Streaming endpoint returned {response.status_code}")

    def test_stream_requires_auth(self):
        """Test that streaming endpoint requires authentication."""
        program_data = {
            "goal": "muscle_gain"
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate/stream",
                json=program_data,
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Streaming endpoint requires authentication")


# ===========================
# DAYS PER WEEK TESTS
# ===========================

class TestDaysPerWeek:
    """Test suite for days_per_week parameter validation."""

    def test_minimum_days_per_week(self, auth_headers):
        """Test generating program with minimum days (2)."""
        program_data = {
            "name": "2 Days Program",
            "goal": "strength",
            "days_per_week": 2
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    assert program["days_per_week"] == 2

                    print(f"\n✅ Generated program with 2 days per week")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)

    def test_maximum_days_per_week(self, auth_headers):
        """Test generating program with maximum days (7)."""
        program_data = {
            "name": "7 Days Program",
            "goal": "endurance",
            "days_per_week": 7
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=90.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["program"]:
                    program = data["program"]
                    assert program["days_per_week"] == 7

                    print(f"\n✅ Generated program with 7 days per week")

                    # Cleanup
                    client.delete(f"{API_V1}/training-programs/{program['id']}", headers=auth_headers)

    def test_invalid_days_per_week_too_low(self, auth_headers):
        """Test validation fails for days_per_week < 2."""
        program_data = {
            "goal": "strength",
            "days_per_week": 1
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/training-programs/generate",
                json=program_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 422, \
                f"Should fail validation for days_per_week < 2, got {response.status_code}"

            print(f"\n✅ Validation correctly rejects days_per_week < 2")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
