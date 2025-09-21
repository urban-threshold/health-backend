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
                 start_time: Union[datetime.datetime, str, None] = None,
                 
                 npcs_in_ed: int = 0,
                 npcs_in_wards: int = 10,
                 wards_capacity: int = 10,
                 ed_capacity: int = 10,
                 inpatient_duration_min: int = 10,
                 inpatient_duration_max: int = 100):

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
        self.ed = ED(name="ED", capacity=ed_capacity, occupied_beds=npcs_in_ed, patient_generator=self.patient_generator, is_ed=True)
        
        # Initialize all wards
        self.wards_dict = {
            'ICU': Ward(name="ICU", capacity=wards_capacity, occupied_beds=npcs_in_wards, patient_generator=self.patient_generator, inpatient_duration_min=inpatient_duration_min, inpatient_duration_max=inpatient_duration_max),
            'AMU': Ward(name="AMU", capacity=wards_capacity, occupied_beds=npcs_in_wards, patient_generator=self.patient_generator, inpatient_duration_min=inpatient_duration_min, inpatient_duration_max=inpatient_duration_max),
            'CCU': Ward(name="CCU", capacity=wards_capacity, occupied_beds=npcs_in_wards, patient_generator=self.patient_generator, inpatient_duration_min=inpatient_duration_min, inpatient_duration_max=inpatient_duration_max),
            'SW': Ward(name="SW", capacity=wards_capacity, occupied_beds=npcs_in_wards, patient_generator=self.patient_generator, inpatient_duration_min=inpatient_duration_min, inpatient_duration_max=inpatient_duration_max),
            'SSU': Ward(name="SSU", capacity=wards_capacity, occupied_beds=npcs_in_wards, patient_generator=self.patient_generator, inpatient_duration_min=inpatient_duration_min, inpatient_duration_max=inpatient_duration_max)
        }


        self.patient_generator.id_counter = 0  # reset id counter

    def create_ed_patient_from_app(self, patient_from_app, requires_inpatient_care, current_time):
        new_patient = self.patient_generator.create_ed_patient_from_app(patient_from_app, requires_inpatient_care, current_time)
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
                        ward_obj.add_patient(patient, current_time)
                        patients_to_remove.append(patient)
                        print('!!!!!!!!!!!!! added patient', patient.id, 'to', ward_name)
                        print()
                        print()

            for patient in patients_to_remove:
                self.ed.remove_patient(patient)

        self.simulation_chunks.append(
                HospitalState(
                    current_time=current_time,
                    wards_dict=self.wards_dict,
                    ed=self.ed
                )
            )

if __name__ == "__main__":
    # Example with specific start time
    start_time = "2024-01-01 08:00:00"
    simulator = HospitalSimulator(
        total_sim_hours=1,
        sim_time_step_minutes=10,
        start_time=start_time
    )