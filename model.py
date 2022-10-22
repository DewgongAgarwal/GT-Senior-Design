""" Database Configurations 

"""

from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select
import os

class Records(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    questions: Optional[str] = Field(default=None)
    prediction: Optional[str] = Field(default=None)
    actual: Optional[str] = Field(default=None)
    validated: bool = Field(default=False)

class User(SQLModel, table=True):
    username: Optional[str] = Field(default=None, primary_key=True)
    auth: Optional[str] = Field(default=None) 

# engine = create_engine("sqlite:///database.db")
# SQLModel.metadata.create_all(engine)
DBURL = os.environ.get('DB_URL', None)
engine = create_engine(DBURL)
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
    
    return record.questions, record.prediction if record else None, None

def totalUnverified(): 
    with Session(engine) as session:
        statement = select(Records).where(Records.validated == False)
        results = list(session.exec(statement))
        return len(results)

def update_authToken(user, auth_token):
    with Session(engine) as session:
        userRecord = session.get(User, user)
        if not userRecord:
            return
        userRecord.auth = auth_token 
        session.add(userRecord)
        session.commit()
        session.refresh(userRecord)

def add_to_user(user, auth_token):
    with Session(engine) as session:
        userRecord = session.get(User, user)
        if userRecord:
            update_authToken(user, auth_token)
        else:
            data = User(username = user, auth = auth_token)
            session.add(data)
            session.commit()

def check_user(decoded_user, auth_token):
    with Session(engine) as session:
        user = session.get(User, decoded_user)
        if not user:
            return False
        return str(user.auth).strip() == str(auth_token).strip()

def remove_from_user(user):
    with Session(engine) as session:
        userRecord = session.get(User, user)
        if not userRecord:
            return
        session.delete(userRecord)
        session.commit()

def resetDb(recordsReset=False):
    with Session(engine) as session:
        statement = select(User)
        results = session.exec(statement)
        results = results.all()
        for record in results:
            session.delete(record)
        session.commit()

    if recordsReset:
        with Session(engine) as session:
            statement = select(Records)
            results = session.exec(statement)
            for record in results:
                record.validated = False
                record.actual = ''
                session.add(record)
                session.commit()
                session.refresh(record)