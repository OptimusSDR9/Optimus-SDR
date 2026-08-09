import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Lead
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate
from app.services.lead_service import create_lead, update_lead


class LeadFieldTests(unittest.TestCase):
    required_fields = {
        "practice_name",
        "doctor_name",
        "contact_person",
        "designation",
        "specialty",
        "city",
        "state",
        "country",
        "website",
        "email",
        "phone",
        "linkedin_url",
        "npi",
        "practice_type",
        "independent_practice",
        "insurance_status",
        "lead_source",
        "lead_score",
        "priority",
        "status",
        "notes",
        "tags",
        "created_at",
        "updated_at",
    }

    def test_model_and_schemas_use_the_correct_field_set(self):
        model_fields = set(Lead.__table__.columns.keys())
        schema_fields = set(LeadResponse.model_fields)

        self.assertTrue(self.required_fields.issubset(model_fields))
        self.assertTrue(self.required_fields.issubset(schema_fields))
        self.assertNotIn("insurance", model_fields)
        self.assertNotIn("decision_maker", model_fields)
        self.assertNotIn("insurance", schema_fields)
        self.assertNotIn("decision_maker", schema_fields)

    def test_service_round_trip_supports_corrected_fields(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        session = sessionmaker(bind=engine)()
        try:
            values = {
                "practice_name": "Field Test Practice",
                "doctor_name": "Dr. Field",
                "contact_person": "Casey Contact",
                "designation": "Operations Director",
                "specialty": "Cardiology",
                "city": "Austin",
                "state": "TX",
                "country": "USA",
                "website": "https://example.com",
                "email": "field@example.com",
                "phone": "555-0100",
                "linkedin_url": "https://linkedin.com/in/field",
                "npi": "1234567890",
                "practice_type": "Private",
                "independent_practice": True,
                "insurance_status": "Verified",
                "lead_source": "Referral",
                "lead_score": 85.0,
                "priority": "High",
                "status": "New",
                "notes": "Field coverage",
                "tags": "module-1",
            }
            lead = create_lead(session, LeadCreate(**values))
            self.assertEqual(LeadResponse.model_validate(lead).model_dump(exclude_none=True)["insurance_status"], "Verified")

            updated = update_lead(session, lead, LeadUpdate(city="Dallas", insurance_status="Pending"))
            self.assertEqual(updated.city, "Dallas")
            self.assertEqual(updated.insurance_status, "Pending")
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
