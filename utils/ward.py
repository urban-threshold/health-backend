from datetime import datetime
from typing import List, Tuple
from .patient import Patient


class Ward: 
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
        """
        Process patients in the ward, handling exits based on timing.
        
        Returns:
            For ED: Tuple of (patients going home, patients going to inpatient)
            For other wards: Empty lists
        """
        # patients_exiting_to_home = []
        # patients_exiting_to_inpatient = []
        
        # # Create a list of patients to remove to avoid modifying list while iterating
        # patients_to_remove = []
        
        # for patient in self.patients:
        #     if self.is_ed:
        #         if patient.ED_exit_time and current_time > patient.ED_exit_time:
        #             patients_to_remove.append(patient)
        #             if patient.requires_inpatient_care:
        #                 patients_exiting_to_inpatient.append(patient)
        #             else:
        #                 patients_exiting_to_home.append(patient)
        #     else:  # normal wards
        #         if patient.IP_exit_time and current_time > patient.IP_exit_time:
        #             patients_to_remove.append(patient)

        for patient in self.patients:
            if self.is_ed:
                if not patient.requires_inpatient_care:
                    # print(patient.name, "going home")
                    if patient.ED_exit_time and current_time > patient.ED_exit_time:
                        self.remove_patient(patient)
            #     else:
            #         if patient.IP_exit_time and current_time > patient.IP_exit_time:
            #             self.remove_patient(patient)
            # else:
            #     if patient.IP_exit_time and current_time > patient.IP_exit_time:
            #         self.remove_patient(patient)
        
        # Remove processed patients
        # for patient in patients_to_remove:
        #     self.remove_patient(patient)
            
        return self.patients
