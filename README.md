# Optimus AI SDR

Optimus AI SDR is an enterprise-grade, modular AI-powered Sales Development Representative platform for Optimus RCM Solutions. The system is designed to help acquire new healthcare clients through automated lead management, qualification, website analysis, AI-assisted outreach, and follow-up tracking.

## Current Status

The following modules are now implemented:
- Authentication
  - Secure registration and login flow
  - Session-based access control
  - Protected dashboard route
  - Password hashing with PBKDF2-HMAC-SHA256
- Dashboard
  - Authenticated overview screen
  - Live lead counts
  - Recent leads section tied to the SQLAlchemy model
- Lead Manager
  - Create, view, and edit leads
  - Lead status management
  - Responsive list and form interface
- CRM
  - Contact pipeline view
  - Stage updates for opportunities
  - Relationship tracking for outreach progression
- AI Website Analyzer
  - Analyze provider websites
  - Extract title, description, heading, and preview content
  - Generate a lightweight outreach insight
- AI Lead Scoring
  - Score leads by specialty fit, location, contact completeness, and engagement stage
  - Surface clear reasons behind the score
- AI Email Generator
  - Draft outreach emails from lead details
  - Support professional, friendly, or direct tones
- Zoho Mail
  - Send outreach emails through a configurable Zoho Mail endpoint
  - Use environment-based credentials for secure delivery
- Follow-up Engine
  - Schedule multi-step outreach cadences
  - Visualize follow-up stages per lead
- Reply Detection
  - Classify incoming replies as positive, neutral, or negative
  - Trigger different follow-up actions based on sentiment
- Notes
  - Attach internal notes to each lead
  - Capture activity history and contextual observations
- Analytics
  - View lead counts, conversion progress, and note activity
  - Track pipeline health by current status
- Settings
  - Manage environment-based integration values for AI and mail delivery
  - Keep operational defaults in one place

## Project Structure

- app/
  - main.py: FastAPI application entrypoint
  - config.py: environment-based configuration
  - database.py: SQLAlchemy engine/session setup
  - models.py: database models
  - routes/: feature modules such as authentication
  - templates/: Jinja2 HTML templates
  - static/: frontend assets
- data/: SQLite database storage
- tests/: regression tests

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   - pip install -r requirements.txt
   - pip install python-multipart
3. Run the app:
   - uvicorn app.main:app --reload

## Next Step

The next module will be the Dashboard module, pending your approval.
