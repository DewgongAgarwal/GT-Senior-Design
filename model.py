""" Database Configurations 

"""

from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine

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