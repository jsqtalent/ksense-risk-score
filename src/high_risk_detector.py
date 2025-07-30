from typing import List
import re

from collector import PatientData


class HighRiskDetector:
    def __init__(self, collection: List[PatientData]):
        self.collection = collection

    def detect(self):
        return_ = []

        for patient in self.collection:
            if self._risk_of(patient) >= 4:
                return_.append(patient)

        return return_

    def _risk_of(self, patient: PatientData):
        return self._blood_pressure_risk_of(patient) + self._temperature_risk_of(patient) + self._age_risk_of(patient)

    def _age_risk_of(self, patient: PatientData):
        if not isinstance(patient.age, int):
            return 0

        if patient.age < 40:
            return 0

        if patient.age <= 65:
            return 1

        return 2

    def _temperature_risk_of(self, patient: PatientData):
        if not isinstance(patient.temperature, float) or not isinstance(patient.temperature, int):
            return 0

        if patient.temperature < 99.6:
            return 0

        if patient.temperature < 101:
            return 1

        return 2

    def _blood_pressure_risk_of(self, patient: PatientData):
        if not isinstance(patient.blood_pressure, str):
            return 0

        pattern = r'^(\d{2,3})/(\d{2,3})$'
        match = re.match(pattern, patient.blood_pressure)

        if not match:
            return 0

        systolic = int(match[1])
        diastolic = int(match[2])

        return max(self._systolic_pressure_risk(systolic), self._diastolic_pressure_risk(diastolic))

    def _systolic_pressure_risk(self, systolic: int) -> int:
        if systolic < 120:
            return 0

        if systolic < 130:
            return 1

        if systolic < 140:
            return 2

        return 3

    def _diastolic_pressure_risk(self, diastolic: int) -> int:
        if diastolic < 80:
            return 0

        if diastolic < 80:
            return 1

        if diastolic < 90:
            return 2

        return 3
