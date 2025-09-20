from utils.ward import Ward
from utils.patient import PatientGenerator
import datetime

class HospitalState:
    def __init__(self, current_time, wards, ed):
        self.current_time = current_time
        self.wards = wards
        self.ed = ed

class HospitalSimulator:
    def __init__(self, total_sim_hours, sim_time_step_minutes):
        self.start_time = datetime.datetime.now()
        self.end_time = datetime.datetime.now() + datetime.timedelta(hours=total_sim_hours)
        self.time_step = datetime.timedelta(minutes=sim_time_step_minutes)
        self.simulation_chunks = []
        self.patient_generator = PatientGenerator()
        self.ed = Ward(name="ED", capacity=10, occupied_beds=5, patient_generator=self.patient_generator, is_ed=True)
        
        self.ICU_ward = Ward(name="ICU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)
        self.AMU_ward = Ward(name="AMU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)
        self.CCU_ward = Ward(name="CCU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)
        self.SW_ward = Ward(name="SW", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)
        self.SSU_ward = Ward(name="SSU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)
        
        self.wards = [
            self.ICU_ward,
            self.AMU_ward,
            self.CCU_ward,
            self.SW_ward,
            self.SSU_ward
        ]

        self.simulation_chunks.append(
            HospitalState(
                current_time=self.start_time,
                wards=self.wards,
                ed=self.ed
            )
        )

        self.run_simulation()

    def run_simulation(self):
        current_time = self.start_time
        while current_time < self.end_time:
            current_time += self.time_step
            self.run_simulation_step(current_time)

            self.simulation_chunks.append(
                HospitalState(
                    current_time=current_time,
                    wards=self.wards,
                    ed=self.ed
                )
            )

    def run_simulation_step(self, current_time):
        self.ed.process_patients(current_time)
        for ward in self.wards:
            ward.process_patients(current_time)


if __name__ == "__main__":
    hospital_simulator = HospitalSimulator(1, 10)

    # print(hospital_simulator.ed.patients)
    # print(hospital_simulator.ICU_ward.patients)