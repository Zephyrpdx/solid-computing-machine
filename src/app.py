"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# In-memory activity database
activities = {
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
    "Basketball Team": {
        "description": "Practice team drills and compete in interscholastic games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["mason@mergington.edu", "ava@mergington.edu"]
    },
    "Soccer Club": {
        "description": "Play friendly matches and improve soccer skills",
        "schedule": "Wednesdays and Saturdays, 3:30 PM - 5:00 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and mixed media art projects",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["mia@mergington.edu", "noah@mergington.edu"]
    },
    "Drama Club": {
        "description": "Rehearse scenes, develop stage performance skills, and put on plays",
        "schedule": "Tuesdays and Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "lucas@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Prepare for academic competitions in science and engineering",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["amelia@mergington.edu", "jack@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging math problems and compete in math tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["ethan@mergington.edu", "harper@mergington.edu"]
    }
}


VALID_EMAIL_DOMAIN = "@mergington.edu"


def _validate_email_domain(email: str) -> tuple[bool, str]:
    """Validate and normalize email. Returns (is_valid, normalized_email)."""
    if not email or "@" not in email:
        return False, ""
    normalized = email.strip().lower()
    is_valid = normalized.endswith(VALID_EMAIL_DOMAIN)
    return is_valid, normalized


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    # Validate and normalize email
    is_valid, normalized_email = _validate_email_domain(email)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid email domain")

    # Validate student is not already signed up
    if normalized_email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up")

    # Check capacity
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is at maximum capacity")

    # Add student
    activity["participants"].append(normalized_email)
    return {"message": f"Signed up {normalized_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    # Normalize email
    _, normalized_email = _validate_email_domain(email)

    # If the email is already registered, allow removal even if the domain
    # is not the expected one (this handles legacy or malformed entries).
    if normalized_email in activity["participants"]:
        activity["participants"].remove(normalized_email)
        return {"message": f"Removed {normalized_email} from {activity_name}"}

    # If the email is not registered, validate domain
    is_valid, _ = _validate_email_domain(email)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid email domain")

    raise HTTPException(status_code=404, detail="Participant not found for this activity")
