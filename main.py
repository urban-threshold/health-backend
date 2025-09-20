from asyncio import Queue
import datetime
import time
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from utils.patient import PatientGenerator


class PatientAdmission(BaseModel):
    name: str
    # id: int
    sex: str  # 'M' or 'F'
    age: int
    triage_level_desc: str
    ICD_desc: str
    # requires_inpatient_care: bool

class HosptialState(BaseModel):
    ed_patients: list



class PateintTiemResponse(BaseModel):
    predictedEntryTs: datetime.datetime


# Generator function to stream events
def event_generator(patient_generator):
    while True:
        # Simulate some dynamic data generation
        time.sleep(1)  # Delay to simulate event interval
        new_data = HosptialState(
            ed_patients=patient_generator.patients
            )
        yield new_data.model_dump_json()


def app_factory():
    app = FastAPI(description="Health app API")
    app.state.q = Queue()

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

    @app.post("/patient")
    async def receive_admission(p: PatientAdmission) -> PateintTiemResponse:
        # ml_model_result = run_ml(p)
        # update_sim(p, ml_model_result, app.state.q)
        return  # PateintTiemResponse(predictedEntryTs=ml_model_result.ts)

    @app.get("/dashboard")
    async def sse():
        return StreamingResponse(event_generator(app.state.patient_generator), media_type="text/event-stream")

    return app



if __name__ == "__main__":
    uvicorn.run(app_factory(), host="127.0.0.1", port=8000)
