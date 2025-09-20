from asyncio import Queue
import datetime
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI


class PatientAdmission(BaseModel):
    name: str


class PateintTiemResponse(BaseModel):
    predictedEntryTs: datetime.datetime


def app_factory():
    app = FastAPI(description="Health app API")
    app.state.q = Queue()

    @app.post("/patient")
    async def receive_admission(p: PatientAdmission) -> PateintTiemResponse:
        # ml_model_result = run_ml(p)
        # update_sim(p, ml_model_result, app.state.q)
        return #PateintTiemResponse(predictedEntryTs=ml_model_result.ts)

    return app


if __name__ == "__main__":
    uvicorn.run(app_factory(), host="127.0.0.1", port=8000)
