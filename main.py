from asyncio import Queue
import datetime
import time
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from utils.patient import PatientGenerator
from utils.ward import Ward
from utils.simulation_manager import HospitalSimulator

# class PatientAdmissionStruct(BaseModel):
#     name: str
#     # id: int
#     sex: str  # 'M' or 'F'
#     age: int
#     triage_level_desc: str
#     ICD_desc: str
#     # requires_inpatient_care: bool

class WardStruct(BaseModel):
    name: str
    patients: list

class HosptialStateStruct(BaseModel):
    current_time: datetime.datetime
    ED: WardStruct
    ICU_ward: WardStruct
    AMU_ward: WardStruct
    CCU_ward: WardStruct
    SW_ward: WardStruct
    SSU_ward: WardStruct

class HosptialSimulationStruct(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    time_step: datetime.timedelta
    simulation_chunks: list


# class PateintTiemResponse(BaseModel):
#     predictedEntryTs: datetime.datetime


# Generator function to stream events
def event_generator(hospital_simulator):
    while True:
        # Simulate some dynamic data generation
        time.sleep(1)  # Delay to simulate event interval

        sim_chunks_raw = hospital_simulator.simulation_chunks
        sim_chunks = []
        for chunk in sim_chunks_raw:
            sim_chunks.append(
                {
                    'current_time': chunk.current_time,
                    'ED': {
                        'name': chunk.ed.name,
                        'patients': chunk.ed.patients,
                        'capacity': chunk.ed.capacity,
                        'occupied_beds': chunk.ed.occupied_beds
                    },
                    'ICU_ward': {
                        'name': chunk.ICU_ward.name,
                        'patients': chunk.ICU_ward.patients
                    },
                    'AMU_ward': {
                        'name': chunk.AMU_ward.name,
                        'patients': chunk.AMU_ward.patients
                    },
                    'CCU_ward': {
                        'name': chunk.CCU_ward.name,
                        'patients': chunk.CCU_ward.patients
                    },
                    'SW_ward': {
                        'name': chunk.SW_ward.name,
                        'patients': chunk.SW_ward.patients
                    },
                    'SSU_ward': {
                        'name': chunk.SSU_ward.name,
                        'patients': chunk.SSU_ward.patients
                    }
                }
                )

        new_data = HosptialSimulationStruct(
            start_time=hospital_simulator.start_time,
            end_time=hospital_simulator.end_time,
            time_step=hospital_simulator.time_step,
            simulation_chunks=sim_chunks
        )

        yield new_data.model_dump_json()


def app_factory():
    app = FastAPI(description="Health app API")
    app.state.q = Queue()

    total_sim_hours = 1
    sim_time_step_minutes = 10

    print(f"hello world!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    app.state.hospital_simulator = HospitalSimulator(total_sim_hours, sim_time_step_minutes)

    print(f"goodbye world!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    print(app.state.hospital_simulator.ICU_ward.patients)

    # app.state.hosptial_state_simulation = HosptialStateSimulationStruct(
    #     start_time=datetime.datetime.now(),
    #     end_time=datetime.datetime.now() + datetime.timedelta(hours=total_sim_hours),
    #     time_step=datetime.timedelta(minutes=sim_time_step_minutes),
    #     simulation_chunks=[]
    # )

    # patient_generator = PatientGenerator()
    # app.state.patient_generator = patient_generator

    # patients = app.state.patient_generator.generate_patients(3)
    # app.state.patients = patients

    # for patient in patients:
    #     print(f"\nPatient: {patient.name}")
    #     print(f"Age: {patient.age}, Sex: {patient.sex}")
    #     print(f"Triage Level: {patient.triage_level_desc}")
    #     print(f"ICD Category: {patient.ICD_desc}")
    #     print("--------------------------------")

    # app.state.hosptial_state_simulation

    # @app.post("/patient")
    # async def receive_admission(p: PatientAdmissionStruct) -> PateintTiemResponse:
    #     # ml_model_result = run_ml(p)
    #     # update_sim(p, ml_model_result, app.state.q)
    #     return  # PateintTiemResponse(predictedEntryTs=ml_model_result.ts)

    @app.get("/dashboard")
    async def sse():
        return StreamingResponse(event_generator(app.state.hospital_simulator), media_type="text/event-stream")

    return app



if __name__ == "__main__":
    uvicorn.run(app_factory(), host="127.0.0.1", port=8000)
