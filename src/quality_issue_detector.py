from typing import List

from collector import PatientData
from pydantic import BaseModel, Field, validator, ValidationError


class Patient(BaseModel):
    patient_id: str
    name: str
    age: int = Field(None, ge=0, le=150)
    gender: str = Field()
    blood_pressure: str = Field()
    temperature: float = Field(ge=90, le=110)
    visit_date: str = None
    diagnosis: str = None
    medications: str = None

    @validator('gender')
    def validate_gender(cls, v):
        if v is not None:
            if v not in ['M', 'F']:
                raise ValueError(f"Invalid gender: {v}")
        return v

    @validator('blood_pressure')
    def validate_blood_pressure(cls, v):
        if v is not None:
            import re
            pattern = r'^\d{2,3}/\d{2,3}$'
            if not re.match(pattern, v):
                raise ValueError(f"Invalid blood pressure format: {v}")
        return v


class QualityIssueDetector:
    def __init__(self, collection: List[PatientData]):
        self.collection = collection

    def detect(self):
        return_ = []
        for patient in self.collection:
            try:
                Patient(**patient.to_dict())
            except ValidationError:
                return_.append(patient)

        return return_
