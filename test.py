from utils.simulation_manager import HospitalSimulator

hospital_simulator = HospitalSimulator(1, 10)

# print(hospital_simulator.ed.patients)
# print(hospital_simulator.ICU_ward.patients)
# print(hospital_simulator.simulation_chunks)

for chunk in hospital_simulator.simulation_chunks:
    print(hospital_simulator.ed.patients)
    print(f"-----------------------")