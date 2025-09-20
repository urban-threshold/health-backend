from utils.ward import Ward, ED
from utils.patient import PatientGenerator, Patient
import datetime
from typing import Optional, Dict, Union
from utils.triage_levels import get_triage_level

class HospitalState:
    def __init__(self, current_time, wards_dict, ed):
        self.current_time = current_time
        self.wards_dict = wards_dict
        self.ed = ed

class HospitalSimulator:
    def __init__(self, total_sim_hours: int, sim_time_step_minutes: int, 
                 start_time: Union[datetime.datetime, str, None] = None):

        # Set start time
        if start_time is None:
            self.start_time = datetime.datetime.now()
        elif isinstance(start_time, str):
            self.start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        else:
            self.start_time = start_time

        self.end_time = self.start_time + datetime.timedelta(hours=total_sim_hours)
        self.time_step = datetime.timedelta(minutes=sim_time_step_minutes)
        self.simulation_chunks = []
        self.patient_generator = PatientGenerator(self.start_time)
        self.ed = ED(name="ED", capacity=10, occupied_beds=5, patient_generator=self.patient_generator, is_ed=True)
        
        # Initialize all wards
        self.wards_dict = {
            'ICU': Ward(name="ICU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator),
            'AMU': Ward(name="AMU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator),
            'CCU': Ward(name="CCU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator),
            'SW': Ward(name="SW", capacity=10, occupied_beds=8, patient_generator=self.patient_generator),
            'SSU': Ward(name="SSU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)
        }


        self.patient_generator.id_counter = 0  # reset id counter

    def create_ed_patient_from_app(self, patient_from_app, requires_inpatient_care):
        new_patient = self.patient_generator.create_ed_patient_from_app(patient_from_app, requires_inpatient_care)
        self.ed.add_patient(new_patient)
        return new_patient

    def get_patient_from_id(self, patient_id: int) -> Optional[Patient]:
        """Find a patient by their ID across all wards and ED"""
        # Check ED
        for patient in self.ed.patients:
            if patient.id == patient_id:
                return patient
                
        # Check all wards
        for ward in self.wards_dict.values():
            for patient in ward.patients:
                if patient.id == patient_id:
                    return patient
        
        return None


    def get_ward_from_name(self, ward_name: str) -> Ward:
        return self.wards_dict[ward_name]

    def assign_patient_to_ward(self, patient: Patient) -> bool:
        """
        Assign a patient to an appropriate ward based on their condition.
        Returns True if successfully assigned, False if no capacity available.
        """
        # Simple ward assignment logic - can be made more sophisticated
        priority_order = ['ICU', 'CCU', 'AMU', 'SSU', 'SW']
        
        for ward_name in priority_order:
            ward = self.wards_dict[ward_name]
            if ward.occupied_beds < ward.capacity:
                ward.add_patient(patient)
                return True
        
        return False

    def run_simulation(self):
        current_time = self.start_time
        while current_time < self.end_time:
            current_time += self.time_step
            self.run_simulation_step(current_time)

            self.simulation_chunks.append(
                HospitalState(
                    current_time=current_time,
                    wards_dict=self.wards_dict,
                    ed=self.ed
                )
            )

    def run_simulation_step(self, current_time):
        # Process ED patients and get transitions
        print(f"Current time: {current_time}")

        for ward in self.wards_dict.values():
            ward.process_patients(current_time)
        


        ed_patients, patients_wanting_to_be_admitted_to = self.ed.process_patients(current_time)

        for ward_name in patients_wanting_to_be_admitted_to:

            ward_obj = self.wards_dict[ward_name]
            destination_ward_patients = patients_wanting_to_be_admitted_to[ward_name]
            # create a dict of triage numbers and have a list of each patient that has that triage level
            triage_dict = {
                1: [],
                2: [],
                3: [],
                4: [],
                5: []
            }

            for patient in destination_ward_patients:
                if get_triage_level(patient.triage_level_desc) not in triage_dict:
                    triage_dict[get_triage_level(patient.triage_level_desc)] = []
                triage_dict[get_triage_level(patient.triage_level_desc)].append(patient)

            # for each triage level, sort based on ED arrival time so that the first patient in the list is the most urgent
            for triage_level in triage_dict:
                triage_dict[triage_level].sort(key=lambda x: x.ED_arrival_time)

            print('!!!!!!!!!!!!! triage_dict for', ward_name, triage_dict)
            print()
            print()

            # check how many beds are available in the ward
            available_beds = ward_obj.capacity - ward_obj.occupied_beds
            print('!!!!!!!!!!!!! available_beds for', ward_name, available_beds)
            print()
            print()

            patients_to_remove = []

            for key in triage_dict.keys():
                for patient in triage_dict[key]:
                    available_beds = ward_obj.capacity - ward_obj.occupied_beds
                    if available_beds > 0:
                        patient.destination_loc = 'HOME'
                        ward_obj.add_patient(patient)
                        patients_to_remove.append(patient)
                        print('!!!!!!!!!!!!! added patient', patient.id, 'to', ward_name)
                        print()
                        print()

            for patient in patients_to_remove:
                self.ed.remove_patient(patient)


        # for patient in patients_going_home:
        #     if patient.id == 1: print(patient.name, "going home")

        # for patient in patients_needing_inpatient:
        #     if patient.id == 1: print(patient.name, "needing inpatient", current_time, patient.ED_arrival_time, patient.ED_exit_time)

        # # Handle patients going to inpatient care
        # for patient in patients_needing_inpatient:
        #     success = self.assign_patient_to_ward(patient)
        #     if not success:
        #         print(f"Warning: No capacity for inpatient {patient.id} in any ward")
        #         # Could implement waiting list or other handling here
        
        # # Process each ward's patients
        # for ward in self.wards_dict.values():
        #     ward.process_patients(current_time)


if __name__ == "__main__":
    # Example with specific start time
    start_time = "2024-01-01 08:00:00"
    simulator = HospitalSimulator(
        total_sim_hours=1,
        sim_time_step_minutes=10,
        start_time=start_time
    )