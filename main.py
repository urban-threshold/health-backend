from asyncio import Queue
import datetime
import time
from uuid import UUID, uuid4
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from utils.patient import PatientGenerator, get_patient_dict, Patient
from utils.ward import Ward
from utils.simulation_manager import HospitalSimulator
from utils.triage_levels import get_triage_level
from utils.ICD import get_category_by_description, get_category_by_code
from fastapi.middleware.cors import CORSMiddleware
from ML_models.ed_to_inpatient_ML import EDToInpatientPredictor
from test import visualize_hospital

class TestReturnStruct(BaseModel):
    test_string: str


class WardStruct(BaseModel):
    name: str
    patients: list
    capacity: int
    occupied_beds: int


class HospitalStateStruct(BaseModel):
    current_time: datetime.datetime
    ED: WardStruct
    wards: dict[str, WardStruct]

class HospitalStateStruct2(BaseModel):
    current_time: datetime.datetime
    ED: dict
    wards: dict


class HospitalSimulationStruct(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    time_step: datetime.timedelta
    simulation_chunks: list[dict]


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


def run_simulation(app_state) -> HospitalSimulationStruct:
    app_state.hospital_simulator.simulation_chunks = [] # reset the chunks

    for i in range(10):
        app_state.hospital_simulator.run_simulation_step(app_state.current_time)
        app_state.current_time += app_state.hospital_simulator.time_step


    sim_chunks_raw = app_state.hospital_simulator.simulation_chunks
    print('sim_chunks_raw', sim_chunks_raw)
    
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
        start_time=app_state.hospital_simulator.start_time,
        end_time=app_state.hospital_simulator.end_time,
        time_step=app_state.hospital_simulator.time_step,
        simulation_chunks=sim_chunks,
    )

########################################################
    # print(f'--------------------------------')
    # print(f'Time: {app_state.current_time}')
    # app_state.hospital_simulator.run_simulation_step(app_state.current_time)
    # # visualize_hospital(app_state.hospital_simulator, app_state.current_time)
    # app_state.current_time += datetime.timedelta(minutes=10)

    # # Create ward data dictionary
    # wards_data = {}
    # for ward_name, ward in app_state.hospital_simulator.wards_dict.items():
    #     patients_formatted = []
    #     for patient in ward.patients:
    #         patients_formatted.append(get_patient_dict(patient))

    #     wards_data[ward_name] = {
    #         "name": ward.name,
    #         "patients": patients_formatted,
    #         "capacity": ward.capacity,
    #         "occupied_beds": ward.occupied_beds,
    #     }

    # # Create chunk data with ED and wards
    # patients_formatted = []
    # for patient in app_state.hospital_simulator.ed.patients:
    #     patients_formatted.append(get_patient_dict(patient))
    

    # ed_data = {
    #     "name": app_state.hospital_simulator.ed.name,
    #     "patients": patients_formatted,
    #     "capacity": app_state.hospital_simulator.ed.capacity,
    #     "occupied_beds": app_state.hospital_simulator.ed.occupied_beds,
    # }

    # new_data = HospitalStateStruct2(
    #     current_time=app_state.current_time,
    #     ED=ed_data,
    #     wards=wards_data,
    # )

    time.sleep(1)

    # new_data = TestReturnStruct(
    #     test_string="test"
    # )

    # new_data = HospitalSimulationStruct(
    #     start_time=app_state.hospital_simulator.start_time,
    #     end_time=app_state.hospital_simulator.end_time,
    #     time_step=app_state.hospital_simulator.time_step,
    #     simulation_chunks=app_state.hospital_simulator.simulation_chunks,
    # )

    return new_data


def app_factory():
    app = FastAPI(description="Health app API")
    app.state.q = Queue()

    app.state.simulation_running = False

    origins = ["http://localhost:3000", "https://mediq.urbanthreshold.com"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.ed_to_inpatient_predictor = EDToInpatientPredictor()

    start_time="2025-09-21 17:00:00"
    app.state.current_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

    total_sim_hours = 1
    sim_time_step_minutes = 10

    inpatient_duration_min_hrs = 2
    inpatient_duration_max_hrs = 14
    inpatient_duration_min = inpatient_duration_min_hrs * 60
    inpatient_duration_max = inpatient_duration_max_hrs * 60

    app.state.hospital_simulator = HospitalSimulator(total_sim_hours, sim_time_step_minutes, start_time=start_time, 
                                            npcs_in_ed=0, npcs_in_wards=8, wards_capacity=10, ed_capacity=10, 
                                            inpatient_duration_min=inpatient_duration_min, inpatient_duration_max=inpatient_duration_max)

    @app.get("/api/dashboard")
    # async def update_hospital_sim() -> HospitalSimulationStruct:
    #     return run_simulation(app.state)
    async def update_hospital_sim() -> HospitalSimulationStruct:
        return run_simulation(app.state)

    @app.post("/api/patient")
    async def create_patient(patient: PatientIncomingModel):

        # format the patient to work with the ML model
        primary_diagnosis_ICD10AM_chapter = get_category_by_code(patient.icdCode)["id"]

        test_patient = {
            "triage_category": patient.triageLevel,
            "age": patient.age,
            "primary_diagnosis_ICD10AM_chapter": primary_diagnosis_ICD10AM_chapter,
            "affected_by_drugs_and_or_alcohol": 0,
            "mental_health_admission": 0,
        }

        # print(test_patient)

        patient_probability = app.state.ed_to_inpatient_predictor.predict(test_patient)

        # print(patient_probability, patient, test_patient)

        # now create the patient in the simulator
        new_patient = app.state.hospital_simulator.create_ed_patient_from_app(
            patient, patient_probability > 0.5
        )

        print(new_patient)

        patient_model = IndividualPatientModel(
            id=new_patient.id,
            name=new_patient.name,
            sex=new_patient.sex,
            age=new_patient.age,
            triage_level=get_triage_level(new_patient.triage_level_desc),
            ICD_int=get_category_by_description(new_patient.ICD_desc)["id"],
            requires_inpatient_care=new_patient.requires_inpatient_care,
        )
        print(patient_model, "patient_model")
        print(f"--------------------------------")
        print(
            app.state.hospital_simulator.ed.patients, "hospital_simulator.ed.patients"
        )

        if not app.state.simulation_running:
            print("first patient received,starting simulation...")

        app.state.simulation_running = True

        return patient_model

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
            ICD_int=get_category_by_description(patient.ICD_desc)["id"],
            requires_inpatient_care=patient.requires_inpatient_care,
        )
        print(patient_model)
        return patient_model

    return app


if __name__ == "__main__":
    uvicorn.run(app_factory(), host="127.0.0.1", port=8000)
