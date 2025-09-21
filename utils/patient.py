from dataclasses import dataclass
from typing import Optional, List
import random
import datetime
from .ICD import ICD_CATEGORIES
from .triage_levels import TRIAGE_LEVELS, get_triage_level, get_triage_description
from .ICD import get_category_by_description, get_category_by_code

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", 
               "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
              "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

def get_patient_dict(patient):
    return{
        'id': patient.id,
        'name': patient.name,
        'sex': patient.sex,
        'age': patient.age,
        'ED_arrival_time': patient.ED_arrival_time,
        'ED_exit_time': patient.ED_exit_time,
        'IP_arrival_time': patient.IP_arrival_time,
        'IP_exit_time': patient.IP_exit_time,
        'triage_level_desc': get_triage_level(patient.triage_level_desc),
        'ICD_desc': get_category_by_description(patient.ICD_desc)['id'],
        'requires_inpatient_care': patient.requires_inpatient_care
    }

@dataclass
class Patient:
    id: int
    name: str
    sex: str  # 'M' or 'F'
    age: int
    triage_level_desc: str
    ICD_desc: str
    requires_inpatient_care: bool
    current_loc: str
    destination_loc: str
    ED_arrival_time: datetime.datetime
    ED_exit_time: Optional[datetime.datetime] = None
    IP_arrival_time: Optional[datetime.datetime] = None
    IP_exit_time: Optional[datetime.datetime] = None


class PatientGenerator:
    def __init__(self, start_time) -> None:
        self.start_time = start_time
        self.id_counter = 1000
        self.patients = []

    def generate_name(self) -> str:
        """Generate a random full name"""
        return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

    def create_ed_patient_from_app(self, patient_from_app, requires_inpatient_care):
        self.id_counter += 1

        # icd_desc = ICD_CATEGORIES[patient_from_app['primary_diagnosis_ICD10AM_chapter']].description
        # triage_level_desc = get_triage_description(patient_from_app['triage_category'])

        # age: int
        # icdCode: str
        # name: str
        # sex: str
        # triageLevel: int

        # icd_desc = ICD_CATEGORIES[patient_from_app.icdCode].description
        icd_desc = get_category_by_code(patient_from_app.icdCode)['description']
        triage_level_desc = get_triage_description(patient_from_app.triageLevel)
        dest_ward = get_category_by_code(patient_from_app.icdCode)['ward']

        random_hours = random.randint(2, 20)
        rand_stay_hours = random.randint(8, 140)

        IP_arrival_time=self.start_time + datetime.timedelta(hours=random_hours)
        IP_exit_time=IP_arrival_time + datetime.timedelta(hours=rand_stay_hours)



        return Patient( #TODO
                id=self.id_counter,
                name=patient_from_app.name,
                sex=patient_from_app.sex,
                age=patient_from_app.age,
                triage_level_desc=triage_level_desc,
                ICD_desc=icd_desc,
                requires_inpatient_care=requires_inpatient_care,
                current_loc="ED",
                destination_loc=dest_ward,
                ED_arrival_time=self.start_time,
                ED_exit_time=self.start_time + datetime.timedelta(minutes=random.randint(10, 30)),
                IP_arrival_time=IP_arrival_time,
                IP_exit_time=IP_exit_time
            )

    def generate_patient(self, current_loc, destination_loc, is_inpatient=False, inpatient_duration=None) -> Patient:
        """Generate a random patient arriving at the ED"""
        self.id_counter += 1
        # Generate random triage level (weighted towards less urgent)
        triage_weights = [0.05, 0.15, 0.25, 0.25, 0.30]  # Weights for levels 1-5
        triage_level = random.choices(list(range(1, 6)), weights=triage_weights)[0]
        triage_desc = get_triage_description(triage_level)

        # Generate random ICD category (excluding certain categories that are less common in ED)
        excluded_categories = [15, 16, 17, 21, 22]  # Pregnancy, perinatal, congenital, factors, special
        valid_categories = [i for i in range(1, 23) if i not in excluded_categories]
        icd_category = random.choice(valid_categories)
        icd_desc = ICD_CATEGORIES[icd_category].description

        if is_inpatient:

            return Patient(
                id=self.id_counter,
                name=self.generate_name(),
                sex=random.choice(['M', 'F']),
                age=random.randint(18, 90),
                triage_level_desc=triage_desc,
                ICD_desc=icd_desc,
                requires_inpatient_care= True,
                current_loc=current_loc,
                destination_loc='HOME',
                ED_arrival_time=None,
                ED_exit_time=None,
                IP_arrival_time=self.start_time,
                IP_exit_time=self.start_time + datetime.timedelta(minutes=inpatient_duration)
            )

        else:
            requires_inpatient_care=random.choice([True, False])
            if requires_inpatient_care:
                dest_ward = 'AMU'
                destination_loc=dest_ward
                ED_exit_time=self.start_time + datetime.timedelta(minutes=30)
            else:
                destination_loc='HOME'
                ED_exit_time=self.start_time + datetime.timedelta(minutes=30)

            return Patient(
                id=self.id_counter,
                name=self.generate_name(),
                sex=random.choice(['M', 'F']),
                age=random.randint(18, 90),
                triage_level_desc=triage_desc,
                ICD_desc=icd_desc,
                requires_inpatient_care=requires_inpatient_care,
                current_loc='ED',
                destination_loc=destination_loc,
                ED_arrival_time=self.start_time,
                ED_exit_time=ED_exit_time,
                IP_arrival_time=None,
                IP_exit_time=None
            )

    def generate_patients(self, num_patients: int = 10) -> List[Patient]:
        """Generate a list of random patients"""
        self.patients = [self.generate_patient() for _ in range(num_patients)]
        return self.patients

    def determine_ward_for_patient(self, icd_desc) -> str:
        """Determine the ward for a patient"""
        return 'ICU'


if __name__ == "__main__":
    generator = PatientGenerator()
    patients = generator.generate_patients(5)
    for patient in patients:
        print(f"\nPatient: {patient.name}")
        print(f"Age: {patient.age}, Sex: {patient.sex}")
        print(f"Triage Level: {patient.triage_level_desc}")
        print(f"ICD Category: {patient.ICD_desc}")