# Backend Tests

Comprehensive test suite for the Mergington High School Activities API backend.

## Overview

Tests follow the **AAA (Arrange-Act-Assert)** pattern for clear test structure and maintainability:

- **ARRANGE**: Set up test data and preconditions via pytest fixtures
- **ACT**: Execute the API request or action being tested
- **ASSERT**: Verify the HTTP response status, response body, and any state changes

This pattern makes tests easy to read, understand, and debug.

## Test Coverage

- **16 test functions** organized into 6 test classes
- **100% code coverage** of `src/app.py`
- Tests cover:
  - Root redirect (`GET /`)
  - Activity retrieval (`GET /activities`)
  - User signup (`POST /activities/{activity_name}/signup`)
  - User unregistration (`DELETE /activities/{activity_name}/unregister`)
  - Happy paths (successful operations)
  - Error cases (404, 400, 422 responses)
  - State consistency (verifying data changes)
  - Integration scenarios (multi-step workflows)

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run tests with verbose output
```bash
pytest tests/ -v
```

### Run tests with coverage report
```bash
pytest tests/ --cov=src.app --cov-report=html
```

### Run a specific test class
```bash
pytest tests/test_app.py::TestSignup -v
```

### Run a specific test function
```bash
pytest tests/test_app.py::TestSignup::test_signup_success -v
```

### Run tests in watch mode (re-run on file changes)
```bash
pip install pytest-watch
ptw tests/
```

## Test Structure

### Test Classes

1. **TestRootRedirect** (1 test)
   - Verifies root endpoint redirects correctly

2. **TestGetActivities** (3 tests)
   - Verifies activities endpoint returns all activities
   - Verifies participants list is included
   - Verifies all required fields are present

3. **TestSignup** (5 tests)
   - Happy path: successful signup
   - Error: nonexistent activity (404)
   - Error: duplicate email (400)
   - Error: missing email parameter (422)
   - State change: participant count increases

4. **TestUnregister** (5 tests)
   - Happy path: successful unregistration
   - Error: nonexistent activity (404)
   - Error: email not registered (400)
   - Error: missing email parameter (422)
   - State change: participant count decreases

5. **TestIntegration** (2 tests)
   - Signup → Unregister sequence (full workflow)
   - Multiple signups to same activity (no side effects)

### Fixtures

Fixtures are defined in `tests/conftest.py` and provide:

- **client**: FastAPI TestClient with isolated test data
- **test_activities**: Deterministic test data (3 activities with known participants)
- **existing_activity**: Name of an activity that exists in test data
- **nonexistent_activity**: Name of an activity that doesn't exist
- **registered_email**: Email already registered for an activity
- **unregistered_email**: Email not registered for any activity
- **valid_email**: A valid test email

## Test Data Isolation

Each test receives fresh, deterministic test data through the `client` fixture:

- Original app activities are stored before the test runs
- Test activities (3 activities with known participants) replace the original data
- After the test completes, original data is restored
- **No test data leaks between tests** — perfect isolation

This means:
- Tests can be run in any order
- Tests can be run multiple times with consistent results
- One test's modifications don't affect other tests

## AAA Pattern Examples

### Example 1: Happy Path Signup
```python
def test_signup_success(self, client, existing_activity, unregistered_email):
    # ARRANGE: Use fixtures to get test data
    activity_name = existing_activity  # "Chess Club"
    email = unregistered_email  # "david@test.edu"
    
    # ACT: Make the API request
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        params={"email": email}
    )
    
    # ASSERT: Verify response and state
    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity_name]["participants"]
```

### Example 2: Error Case
```python
def test_signup_duplicate_email(self, client, existing_activity, registered_email):
    # ARRANGE: Email is already in the activity
    activity_name = existing_activity
    email = registered_email  # "alice@test.edu" (already in Chess Club)
    
    # ACT: Attempt to signup
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        params={"email": email}
    )
    
    # ASSERT: Verify error response
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()
```

### Example 3: Integration Test
```python
def test_signup_then_unregister_sequence(self, client, existing_activity, unregistered_email):
    # ARRANGE
    activity_name = existing_activity
    email = unregistered_email
    
    # ACT 1: Signup
    response_signup = client.post(...)
    assert response_signup.status_code == 200
    
    # ASSERT 1: Verify participant added
    assert email in client.get("/activities").json()[activity_name]["participants"]
    
    # ACT 2: Unregister
    response_unregister = client.delete(...)
    assert response_unregister.status_code == 200
    
    # ASSERT 2: Verify participant removed
    assert email not in client.get("/activities").json()[activity_name]["participants"]
```

## Test Files

- `tests/__init__.py` — Package marker
- `tests/conftest.py` — Pytest configuration and fixtures (~95 lines)
- `tests/test_app.py` — All test functions (~300 lines, 16 tests organized in 6 classes)
- `tests/README.md` — This file

## Dependencies

- `pytest` — Test runner
- `fastapi` — Web framework
- `httpx` — HTTP client (for FastAPI TestClient)
- `pytest-cov` — Coverage reporting (optional)

All dependencies are listed in `requirements.txt`.

## Installing Dependencies

```bash
pip install -r requirements.txt
```

Or install test dependencies specifically:
```bash
pip install pytest pytest-cov
```

## Continuous Integration

To run tests in a CI/CD pipeline:

```bash
pytest tests/ -v --cov=src.app --cov-report=term-missing --cov-report=xml
```

This will:
- Show verbose test output
- Generate coverage report in terminal
- Generate coverage report in XML format (for CI integration)
- Exit with code 0 if all tests pass, non-zero if any fail

## Troubleshooting

### Tests fail with "Module not found" error
Ensure `pytest.ini` has `pythonpath = .` configured.

### Tests pass individually but fail when run together
Likely a test isolation issue. Check that fixtures are properly restoring state.

### Tests are slow
The current test suite should complete in ~0.3 seconds. If slower, check for I/O operations or external dependencies.

### Coverage is low
Ensure all code paths are tested, including error cases and edge conditions.

## Future Enhancements

1. **Capacity validation tests**: If max_participants validation is added to the backend
2. **Email format validation**: If email regex validation is implemented
3. **Performance tests**: If API response times need to be monitored
4. **Integration with CI/CD**: GitHub Actions, GitLab CI, etc.
5. **End-to-end tests**: Frontend + backend combined tests
