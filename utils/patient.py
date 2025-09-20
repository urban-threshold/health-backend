from dataclasses import dataclass
from typing import Optional, List
import random
import datetime
from .triage_levels import TRIAGE_LEVELS, get_triage_description
from .ICD import ICD_CATEGORIES

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", 
               "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
              "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

@dataclass
class PatientArrivingAtED:
    """A patient arriving at the Emergency Department"""
    name: str
    sex: str  # 'M' or 'F'
    age: int
    triage_level_desc: str
    ICD_desc: str


class PatientGenerator:
    def __init__(self) -> None:
        self.id_counter = 0
        self.patients = []

    def generate_name(self) -> str:
        """Generate a random full name"""
        return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

    def generate_patient_arriving_at_ed(self) -> PatientArrivingAtED:
        """Generate a random patient arriving at the ED"""
        # Generate random triage level (weighted towards less urgent)
        triage_weights = [0.05, 0.15, 0.25, 0.25, 0.30]  # Weights for levels 1-5
        triage_level = random.choices(list(range(1, 6)), weights=triage_weights)[0]
        triage_desc = get_triage_description(triage_level)

        # Generate random ICD category (excluding certain categories that are less common in ED)
        excluded_categories = [15, 16, 17, 21, 22]  # Pregnancy, perinatal, congenital, factors, special
        valid_categories = [i for i in range(1, 23) if i not in excluded_categories]
        icd_category = random.choice(valid_categories)
        icd_desc = ICD_CATEGORIES[icd_category].description

        return PatientArrivingAtED(
            name=self.generate_name(),
            sex=random.choice(['M', 'F']),
            age=random.randint(18, 90),
            triage_level_desc=triage_desc,
            ICD_desc=icd_desc
        )

    def generate_patients(self, num_patients: int = 10) -> List[PatientArrivingAtED]:
        """Generate a list of random patients"""
        self.patients = [self.generate_patient_arriving_at_ed() for _ in range(num_patients)]
        return self.patients


if __name__ == "__main__":
    generator = PatientGenerator()
    patients = generator.generate_patients(5)
    for patient in patients:
        print(f"\nPatient: {patient.name}")
        print(f"Age: {patient.age}, Sex: {patient.sex}")
        print(f"Triage Level: {patient.triage_level_desc}")
        print(f"ICD Category: {patient.ICD_desc}")