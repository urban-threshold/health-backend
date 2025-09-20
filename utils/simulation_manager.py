from utils.ward import Ward
from utils.patient import PatientGenerator


class HospitalSimulator:
    def __init__(self):
        self.patient_generator = PatientGenerator()
        self.ed = Ward(name="ED", capacity=10, occupied_beds=5, patient_generator=self.patient_generator, is_ed=True)
        self.ICU_ward = Ward(name="ICU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)
        self.AMU_ward = Ward(name="AMU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)
        self.CCU_ward = Ward(name="CCU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)
        self.SW_ward = Ward(name="SW", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)
        self.SSU_ward = Ward(name="SSU", capacity=10, occupied_beds=8, patient_generator=self.patient_generator)

        

if __name__ == "__main__":
    hospital_simulator = HospitalSimulator()

    print(hospital_simulator.ed.patients)