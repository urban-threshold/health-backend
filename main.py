from asyncio import Queue
import datetime
import time
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse


class PatientAdmission(BaseModel):
    name: str


class PateintTiemResponse(BaseModel):
    predictedEntryTs: datetime.datetime


# Generator function to stream events
def event_generator():
    while True:
        # Simulate some dynamic data generation
        time.sleep(1)  # Delay to simulate event interval
        new_data = PateintTiemResponse(predictedEntryTs=datetime.datetime.now())
        yield new_data.model_dump_json()


def app_factory():
    app = FastAPI(description="Health app API")
    app.state.q = Queue()

    @app.post("/patient")
    async def receive_admission(p: PatientAdmission) -> PateintTiemResponse:
        # ml_model_result = run_ml(p)
        # update_sim(p, ml_model_result, app.state.q)
        return  # PateintTiemResponse(predictedEntryTs=ml_model_result.ts)

    @app.get("/dashboard")
    async def sse():
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return app



if __name__ == "__main__":
    uvicorn.run(app_factory(), host="127.0.0.1", port=8000)
