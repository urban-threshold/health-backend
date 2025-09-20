from utils.simulation_manager import HospitalSimulator

hospital_simulator = HospitalSimulator(1, 10)

# print(hospital_simulator.ed.patients)
# print(hospital_simulator.ICU_ward.patients)
# print(hospital_simulator.simulation_chunks)

# print("ED patients:")
# for patient in hospital_simulator.ed.patients:
#     print(patient.name, patient.id)

print("ICU patients:")
for patient in hospital_simulator.wards_dict['ICU'].patients:
    print(patient.name, patient.id)

# for chunk in hospital_simulator.simulation_chunks:
#     print(hospital_simulator.ed.patients)
#     print(f"-----------------------")