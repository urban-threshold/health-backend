from datetime import datetime, timedelta
from typing import List, Tuple
from .patient import Patient
from .triage_levels import get_triage_level
import random

class Ward: 
    def __init__(self, name, capacity, occupied_beds, patient_generator, is_ed=False):
        self.name = name
        self.capacity = capacity
        self.patients = []
        self.occupied_beds = occupied_beds
        self.is_ed = is_ed
        self.patient_generator = patient_generator
        self.initialize_ward()

    def add_patient(self, patient: Patient, current_time):
        """Add a patient to the ward"""
        patient.IP_arrival_time = current_time
        patient.IP_exit_time = current_time + timedelta(minutes=random.randint(10, 100))

        self.patients.append(patient)
        self.occupied_beds = len(self.patients)

    def remove_patient(self, patient: Patient):
        """Remove a patient from the ward"""
        self.patients.remove(patient)
        self.occupied_beds = len(self.patients)

    def initialize_ward(self):
        """Initialize the ward with patients"""
        current_loc = self.name
        destination_loc = 'HOME'

        for i in range(self.occupied_beds):
            patient = self.patient_generator.generate_patient(current_loc, destination_loc, is_inpatient=True)
            self.patients.append(patient)

    def process_patients(self, current_time) -> Tuple[List[Patient], List[Patient]]:
        for patient in self.patients:
            if patient.IP_exit_time and current_time > patient.IP_exit_time:
                self.remove_patient(patient)
            
        return self.patients


class ED: 
    def __init__(self, name, capacity, occupied_beds, patient_generator, is_ed=False):
        self.name = name
        self.capacity = capacity
        self.patients = []
        self.occupied_beds = occupied_beds
        self.is_ed = is_ed
        self.patient_generator = patient_generator
        self.initialize_ward()

    def add_patient(self, patient: Patient):
        """Add a patient to the ward"""
        self.patients.append(patient)
        self.occupied_beds = len(self.patients)

    def remove_patient(self, patient: Patient):
        """Remove a patient from the ward"""
        self.patients.remove(patient)
        self.occupied_beds = len(self.patients)

    def initialize_ward(self):
        """Initialize the ward with patients"""
        if self.is_ed:
            current_loc = 'ED'
            destination_loc = 'ICU'
        else:
            current_loc = self.name
            destination_loc = 'HOME'

        for i in range(self.occupied_beds):
            patient = self.patient_generator.generate_patient(current_loc, destination_loc, is_inpatient=(not self.is_ed))
            self.patients.append(patient)

    def process_patients(self, current_time) -> Tuple[List[Patient], List[Patient]]:
        patients_wanting_to_be_admitted_to = {  # create keys for each ward, init with empty lists
            "ICU": [],
            "CCU": [],
            "AMU": [],
            "SSU": [],
            "SW": []
        }

        for patient in self.patients:
            print(patient.name, 'is in the ED')

        patients_to_remove = []

        for patient in self.patients:
            print('CHECKING', patient.name)

            if not patient.requires_inpatient_care:
                if patient.ED_exit_time and current_time > patient.ED_exit_time:
                    print(patient.name, 'going home')
                    patients_to_remove.append(patient)
                else:
                    print(patient.name, 'WAITING to go home')
            else:  # need to go to a ward to be admitted
                if patient.ED_exit_time and current_time > patient.ED_exit_time:
                    print(patient.name, 'going to', patient.destination_loc)
                    patients_wanting_to_be_admitted_to[patient.destination_loc].append(patient)
                else:
                    print(patient.name, 'WAITING to go to', patient.destination_loc)

        for patient in patients_to_remove:
            self.remove_patient(patient)

        print('patients_wanting_to_be_admitted_to', patients_wanting_to_be_admitted_to)
            
        return self.patients, patients_wanting_to_be_admitted_to