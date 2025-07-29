from fastapi import FastAPI

user_db = {
    'jack':{'username':'jack','date-of-join':'18-Dec-2009','location':'SantaKarla'},
    'jill':{'username':'jill','date-of-join':'18-Jan-2019','location':'SanDiago'},
    'kanailal':{'username':'kanailal','date-of-join':'10-Apr-1999','location':'NewDelhi'},
    'chacha':{'username':'chacha','date-of-join':'10-Nov-1975','location':'Karachi'}
}

app = FastAPI()

@app.get('/users')
def get_users():
    users = list(user_db.values())
    return users

@app.get('/users/{username}')
def get_user(username:str):
    user = user_db[username]
    return user

@app.get('/fewusers')
def get_few_users(limit: int):
    users = list(user_db.values())
    return users[:limit]


print ('Hello Python')