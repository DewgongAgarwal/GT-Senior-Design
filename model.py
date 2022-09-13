from deta import Deta
from decouple import config

db_key = config('key', default='')
deta = Deta(db_key) # configure your Deta project
users_db = deta.Base('Validators')  # access your DB
records_db = deta.Base('Records')