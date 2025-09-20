from datetime import datetime
from typing import List, Tuple
from .patient import Patient
from .triage_levels import get_triage_level

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

        patients_wanting_to_be_admitted = {# create keys for each ward, init with empty lists
            "ICU": [],
            "CCU": [],
            "AMU": [],
            "SSU": [],
            "SW": []

            }

        for patient in self.patients:
            if self.is_ed:
                if not patient.requires_inpatient_care:
                    if patient.ED_exit_time and current_time > patient.ED_exit_time:
                        self.remove_patient(patient)
                else: # need to go to a ward to be admitted
                    # sort patients by priority based on triage level. will need to convert the triage desc to a number
                    # self.patients.sort(key=lambda x: get_triage_level(x.triage_level_desc))

                    if patient.ED_exit_time and current_time > patient.ED_exit_time:
                        patients_wanting_to_be_admitted[patient.destination_loc].append(patient)

        if self.is_ed:
            print(patients_wanting_to_be_admitted)


        # create a dict of triage numbers and have a list of each patient that has that triage level
                    # triage_dict = {
                    #     1: [],
                    #     2: [],
                    #     3: [],
                    #     4: [],
                    #     5: []
                    # }

                    # for patient in self.patients:
                    #     if get_triage_level(patient.triage_level_desc) not in triage_dict:
                    #         triage_dict[get_triage_level(patient.triage_level_desc)] = []
                    #     triage_dict[get_triage_level(patient.triage_level_desc)].append(patient)

                    # # for each triage level, sort based on ED arrival time so that the first patient in the list is the most urgent
                    # for triage_level in triage_dict:
                    #     triage_dict[triage_level].sort(key=lambda x: x.ED_arrival_time)

                    # # patients_ordered

                    # print(triage_dict)

        # for patient in patients_queued_for_admission:
        #     pass
            
        return self.patients
