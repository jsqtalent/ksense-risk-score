import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

import requests
from pydantic import BaseModel, Field
from pydantic import ValidationError as PydanticValidationError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class PatientData:
    patient_id: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_pressure: Optional[str] = None
    temperature: Optional[float] = None
    visit_date: Optional[str] = None
    diagnosis: Optional[str] = None
    medications: Optional[str] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatientData':
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'patient_id': self.patient_id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'blood_pressure': self.blood_pressure,
            'temperature': self.temperature,
            'visit_date': self.visit_date,
            'diagnosis': self.diagnosis,
            'medications': self.medications,
            'bp_systolic': self.bp_systolic,
            'bp_diastolic': self.bp_diastolic
        }


class Pagination(BaseModel):
    page: int = Field(ge=1)
    limit: int = Field(ge=1)
    total: int = Field(ge=0)
    totalPages: int = Field(ge=0)
    hasNext: bool
    hasPrevious: bool


class Metadata(BaseModel):
    timestamp: str
    version: str
    requestId: str


class PatientsResponse(BaseModel):
    data: List[Dict[str, Any]]
    pagination: Pagination
    metadata: Metadata


class Collector:
    def __init__(self, base_url: str, token: str, inform):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.inform = inform

    def collect(self):
        return self._get_all_patients()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        session = self._session()

        url = f"{self.base_url}{endpoint}"

        self.inform(f"request with method {method} to {endpoint} with kwargs {json.dumps(kwargs)}")

        response = session.request(
            method=method,
            url=url,
            headers={
                "x-api-key": self.token,
                "Content-Type": "application/json"
            },
            **kwargs
        )

        response.raise_for_status()
        response_data = response.json()
        return response_data

    def _session(self):
        session = requests.Session()
        retry_strategy = Retry(
            total=10,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            backoff_factor=0.5,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _make_request_with_validation_retry(self, method: str, endpoint: str, max_retries: int = 3, **kwargs) -> PatientsResponse:
        for attempt in range(max_retries):
            try:
                response_data = self._make_request(method, endpoint, **kwargs)
                validated_response = PatientsResponse(**response_data)
                return validated_response
            except PydanticValidationError:
                if attempt < max_retries - 1:
                    continue
                else:
                    raise

    def _get_patients(self, page: int = 1, limit: int = 20) -> PatientsResponse:
        params = {"page": page, "limit": limit}
        return self._make_request_with_validation_retry("GET", "/patients", params=params)

    def _get_all_patients(self) -> list[PatientData]:
        all_patients = []
        page = 1

        while True:
            response = self._get_patients(page=page)
            all_patients.extend(response.data)

            if not response.pagination.hasNext:
                break

            page += 1

        return [PatientData(**patient) for patient in all_patients]
