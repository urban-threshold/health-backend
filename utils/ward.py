# from utils.patient import generate_patient
from datetime import datetime


class Ward: 
    def __init__(self, name, capacity, occupied_beds, patient_generator, is_ed=False):
        self.name = name
        self.capacity = capacity
        self.patients = []
        self.occupied_beds = occupied_beds
        self.is_ed = is_ed
        self.patient_generator = patient_generator
        self.initialize_ward()

    def add_patient(self, patient):
        self.patients.append(patient)

    def remove_patient(self, patient):
        self.patients.remove(patient)

    def initialize_ward(self):
        for i in range(self.occupied_beds):
            patient = self.patient_generator.generate_patient(i)
            self.patients.append(patient)

    def process_patients(self, current_time):
        for patient in self.patients:
            if patient.IP_exit_time and current_time > patient.IP_exit_time:
                self.remove_patient(patient)