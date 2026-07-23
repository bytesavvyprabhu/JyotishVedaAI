from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from Geocode import resolve_birth_Location
from chart import compute_chart
from ask import ask

app = FastAPI(title="JyotishVedaAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConsultRequest(BaseModel):
    name: str
    place_of_birth: str
    date_of_birth: str  # "YYYY-MM-DD"
    time_of_birth: str  # "HH:MM" (24h, local time at place of birth)
    question: str


class ConsultResponse(BaseModel):
    name: str
    chart: dict
    answer: str


@app.post("/consult", response_model=ConsultResponse)
def consult(req: ConsultRequest):
    try:
        location = resolve_birth_Location(req.place_of_birth, req.date_of_birth, req.time_of_birth)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    chart = compute_chart(
        req.date_of_birth,
        req.time_of_birth,
        location["latitude"],
        location["longitude"],
        location["timezone_offset"],
    )

    try:
        answer = ask(chart, req.question)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ConsultResponse(name=req.name, chart=chart, answer=answer)
