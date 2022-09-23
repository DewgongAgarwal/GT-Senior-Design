""" Database Configurations 

"""

from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Records(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    questions: Optional[str] = Field(default=None)
    prediction: Optional[str] = Field(default=None)
    actual: Optional[str] = Field(default=None)
    validated: bool = Field(default=False)

engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

def add_response_to_db(responses, predictionGiven):
    responses = map(str, responses)
    responsesStr = ''.join(responses)

    data = Records(questions = responsesStr, validated = False, 
            prediction = predictionGiven)

    with Session(engine) as session:
        session.add(data)
        session.commit()

def read_next_invalidated():
    with Session(engine) as session:
        statement = select(Records).where(Records.validated == False).limit(1)
        results = list(session.exec(statement))
        if len(results) == 0:
            return {"data": False}
        return results[0]

def updatePrediction(id, actualValue):
    with Session(engine) as session:
        statement = select(Records).where(Records.id == id)
        results = session.exec(statement)
        record = results.one()
        record.validated = True
        record.actual = actualValue
        session.add(record)
        session.commit()
        session.refresh(record)
        print("Updated:", record)

def resetDb():
    with Session(engine) as session:
        statement = select(Records)
        results = session.exec(statement)
        for record in results:
            record.validated = False
            record.actual = ''
            session.add(record)
            session.commit()
            session.refresh(record)