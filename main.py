from asyncio import Queue
import datetime
import time
from uuid import UUID, uuid4
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from utils.patient import PatientGenerator, get_patient_dict
from utils.ward import Ward
from utils.simulation_manager import HospitalSimulator
from utils.triage_levels import get_triage_level
from utils.ICD import get_category_by_description
from fastapi.middleware.cors import CORSMiddleware


class WardStruct(BaseModel):
    name: str
    patients: list
    capacity: int
    occupied_beds: int


class HospitalStateStruct(BaseModel):
    current_time: datetime.datetime
    ED: WardStruct
    wards: dict[str, WardStruct]


class HospitalSimulationStruct(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    time_step: datetime.timedelta
    simulation_chunks: list


class PatientIncomingModel(BaseModel):
    age: int
    icdCode: str
    name: str
    sex: str
    triageLevel: int


class PatientOutgoingModel(BaseModel):
    id: UUID

class IndividualPatientModel(BaseModel):
    id: int
    name: str
    sex: str
    age: int
    triage_level: int
    ICD_int: int
    requires_inpatient_care: bool

def event_generator(hospital_simulator):
    while True:
        # Simulate some dynamic data generation
        time.sleep(1)  # Delay to simulate event interval

        sim_chunks_raw = hospital_simulator.simulation_chunks
        sim_chunks = []
        for chunk in sim_chunks_raw:
            # Create ward data dictionary
            wards_data = {}
            for ward_name, ward in chunk.wards_dict.items():
                patients_formatted = []
                for patient in ward.patients:
                    patients_formatted.append(get_patient_dict(patient))

                wards_data[ward_name] = {
                    "name": ward.name,
                    "patients": patients_formatted,
                    "capacity": ward.capacity,
                    "occupied_beds": ward.occupied_beds,
                }

            # Create chunk data with ED and wards
            patients_formatted = []
            for patient in chunk.ed.patients:
                patients_formatted.append(get_patient_dict(patient))
            chunk_data = {
                "current_time": chunk.current_time,
                "ED": {
                    "name": chunk.ed.name,
                    "patients": patients_formatted,
                    "capacity": chunk.ed.capacity,
                    "occupied_beds": chunk.ed.occupied_beds,
                },
                "wards": wards_data,
            }
            sim_chunks.append(chunk_data)

        new_data = HospitalSimulationStruct(
            start_time=hospital_simulator.start_time,
            end_time=hospital_simulator.end_time,
            time_step=hospital_simulator.time_step,
            simulation_chunks=sim_chunks,
        )

        yield new_data.model_dump_json()


def app_factory():
    app = FastAPI(description="Health app API")
    app.state.q = Queue()

    origins = ["http://localhost:3000", "https://mediqc.urbanthreshold.com"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    total_sim_hours = 1
    sim_time_step_minutes = 10

    app.state.hospital_simulator = HospitalSimulator(
        total_sim_hours, sim_time_step_minutes
    )

    @app.get("/api/dashboard")
    async def sse():
        return StreamingResponse(
            event_generator(app.state.hospital_simulator),
            media_type="text/event-stream",
        )

    @app.post("/api/patient")
    async def create_patient(patient: PatientIncomingModel):
        # TODO: model
        # TODO: results to simulator
        return PatientOutgoingModel(id=uuid4())

    @app.get("/api/patient/{id}")
    async def get_patient(id: int) -> IndividualPatientModel:
        # TODO: refer to stored model result
        patient = app.state.hospital_simulator.get_patient_from_id(id)
        patient_model = IndividualPatientModel(
            id=patient.id,
            name=patient.name,
            sex=patient.sex,
            age=patient.age,
            triage_level=get_triage_level(patient.triage_level_desc),
            ICD_int=get_category_by_description(patient.ICD_desc)['id'],
            requires_inpatient_care=patient.requires_inpatient_care
        )
        print(patient_model)
        return patient_model

    return app


if __name__ == "__main__":
    uvicorn.run(app_factory(), host="127.0.0.1", port=8000)
