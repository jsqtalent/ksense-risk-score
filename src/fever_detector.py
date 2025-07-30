from typing import List

from collector import PatientData


class FeverDetector:
    def __init__(self, collection: List[PatientData]):
        self.collection = collection

    def detect(self):
        return_ = []

        for patient in self.collection:
            if (isinstance(patient.temperature, float) or isinstance(patient.temperature, int)) and patient.temperature >= 99.6:
                return_.append(patient)

        return return_
