from typing import Any, Dict, List


def build_onboarding_steps(total_leads: int, total_notes: int, settings_configured: bool) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = [
        {
            "id": "lead",
            "title": "Add your first lead",
            "description": "Create a practice profile and capture the initial contact details.",
            "completed": total_leads > 0,
        },
        {
            "id": "notes",
            "title": "Capture notes",
            "description": "Record context so follow-up conversations stay organized.",
            "completed": total_notes > 0,
        },
        {
            "id": "score",
            "title": "Review scoring",
            "description": "Open the scoring module to prioritize the highest-fit opportunities.",
            "completed": total_leads > 0,
        },
        {
            "id": "settings",
            "title": "Configure integrations",
            "description": "Add your API and mail defaults in Settings so outbound can run smoothly.",
            "completed": settings_configured,
        },
    ]

    completed_count = sum(1 for step in steps if step["completed"])
    percent = int(round((completed_count / len(steps)) * 100))

    return {
        "steps": steps,
        "completed": completed_count,
        "total": len(steps),
        "percent": percent,
    }
