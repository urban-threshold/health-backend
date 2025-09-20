from utils.simulation_manager import HospitalSimulator
import time
import datetime

start_time="2025-09-21 17:00:00"
hospital_simulator = HospitalSimulator(1, 10, start_time=start_time)
current_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

print('initial ed patients:', hospital_simulator.ed.patients)

while True:
    print(f'--------------------------------')
    hospital_simulator.run_simulation_step(current_time)
    current_time += datetime.timedelta(minutes=10)
    time.sleep(1)
    # print(current_time)
    # print(hospital_simulator.ed.patients)


# print(hospital_simulator.ed.patients)
# print(hospital_simulator.ICU_ward.patients)
# print(hospital_simulator.simulation_chunks)

# print("ED patients:")
# for patient in hospital_simulator.ed.patients:
#     print(patient.name, patient.id)

# print("ICU patients:")
# for patient in hospital_simulator.wards_dict['ICU'].patients:
#     print(patient.name, patient.id)

# for chunk in hospital_simulator.simulation_chunks:
#     print(hospital_simulator.ed.patients)
#     print(f"-----------------------")