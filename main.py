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
                wards_data[ward_name] = {
                    'name': ward.name,
                    'patients': ward.patients,
                    'capacity': ward.capacity,
                    'occupied_beds': ward.occupied_beds
                }

            # Create chunk data with ED and wards
            chunk_data = {
                'current_time': chunk.current_time,
                'ED': {
                    'name': chunk.ed.name,
                    'patients': chunk.ed.patients,
                    'capacity': chunk.ed.capacity,
                    'occupied_beds': chunk.ed.occupied_beds
                },
                'wards': wards_data
            }
            sim_chunks.append(chunk_data)

        new_data = HospitalSimulationStruct(
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

    app.state.hospital_simulator = HospitalSimulator(total_sim_hours, sim_time_step_minutes)

    @app.get("/dashboard")
    async def sse():
        return StreamingResponse(event_generator(app.state.hospital_simulator), media_type="text/event-stream")

    return app


if __name__ == "__main__":
    uvicorn.run(app_factory(), host="127.0.0.1", port=8000)