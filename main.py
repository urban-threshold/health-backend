from asyncio import Queue
import datetime
import time
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from utils.patient import PatientGenerator
from utils.ward import Ward


class PatientAdmissionStruct(BaseModel):
    name: str
    # id: int
    sex: str  # 'M' or 'F'
    age: int
    triage_level_desc: str
    ICD_desc: str
    # requires_inpatient_care: bool

class HosptialStateStruct(BaseModel):
    current_time: datetime.datetime
    ED: Ward
    ICU_ward: Ward
    AMU_ward: Ward
    CCU_ward: Ward
    SW_ward: Ward
    SSU_ward: Ward

class HosptialStateSimulationStruct(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    time_step: datetime.timedelta
    simulation_chunks: list


class PateintTiemResponse(BaseModel):
    predictedEntryTs: datetime.datetime


# Generator function to stream events
def event_generator(hosptial_state_simulation, patient_generator):
    while True:
        # Simulate some dynamic data generation
        time.sleep(1)  # Delay to simulate event interval
        new_data = hosptial_state_simulation
        yield new_data.model_dump_json()


def app_factory():
    app = FastAPI(description="Health app API")
    app.state.q = Queue()

    total_sim_hours = 1
    sim_time_step_minutes = 10

    app.state.hosptial_state_simulation = HosptialStateSimulationStruct(
        start_time=datetime.datetime.now(),
        end_time=datetime.datetime.now() + datetime.timedelta(hours=total_sim_hours),
        time_step=datetime.timedelta(minutes=sim_time_step_minutes),
        simulation_chunks=[]
    )

    patient_generator = PatientGenerator()
    app.state.patient_generator = patient_generator

    patients = app.state.patient_generator.generate_patients(3)
    app.state.patients = patients

    for patient in patients:
        print(f"\nPatient: {patient.name}")
        print(f"Age: {patient.age}, Sex: {patient.sex}")
        print(f"Triage Level: {patient.triage_level_desc}")
        print(f"ICD Category: {patient.ICD_desc}")
        print("--------------------------------")

    # app.state.hosptial_state_simulation

    @app.post("/patient")
    async def receive_admission(p: PatientAdmission) -> PateintTiemResponse:
        # ml_model_result = run_ml(p)
        # update_sim(p, ml_model_result, app.state.q)
        return  # PateintTiemResponse(predictedEntryTs=ml_model_result.ts)

    @app.get("/dashboard")
    async def sse():
        return StreamingResponse(event_generator(app.state.hosptial_state_simulation, app.state.patient_generator), media_type="text/event-stream")

    return app



if __name__ == "__main__":
    uvicorn.run(app_factory(), host="127.0.0.1", port=8000)
