from utils.ward import Ward
from utils.patient import PatientGenerator
import datetime

class HospitalState:
    def __init__(self, current_time, wards_dict, ed):
        self.current_time = current_time
        self.wards_dict = wards_dict
        self.ed = ed

class HospitalSimulator:
    def __init__(self, total_sim_hours, sim_time_step_minutes):
        self.start_time = datetime.datetime.now()
        self.end_time = datetime.datetime.now() + datetime.timedelta(hours=total_sim_hours)
        self.time_step = datetime.timedelta(minutes=sim_time_step_minutes)
        self.simulation_chunks = []
        self.patient_generator = PatientGenerator()
        self.ed = Ward(name="ED", capacity=10, occupied_beds=5, patient_generator=self.patient_generator, is_ed=True)
        
        # Initialize all wards
        self.wards_dict = {
            'ICU': Ward(name="ICU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator),
            'AMU': Ward(name="AMU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator),
            'CCU': Ward(name="CCU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator),
            'SW': Ward(name="SW", capacity=10, occupied_beds=8, patient_generator=self.patient_generator),
            'SSU': Ward(name="SSU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)
        }

        # Store initial state
        self.simulation_chunks.append(
            HospitalState(
                current_time=self.start_time,
                wards_dict=self.wards_dict,
                ed=self.ed
            )
        )

        self.run_simulation()

    def get_patient_from_id(self, id):
        for ward in self.wards_dict.values():
            for patient in ward.patients:
                if patient.id == id:
                    return patient
        for patient in self.ed.patients:
            if patient.id == id:
                return patient
        return None

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
        # Process ED patients
        self.ed.process_patients(current_time)
        
        # Process each ward's patients
        for ward in self.wards_dict.values():
            ward.process_patients(current_time)


if __name__ == "__main__":
    hospital_simulator = HospitalSimulator(1, 10)  # 1 hour simulation with 10-minute steps