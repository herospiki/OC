from fastapi import FastAPI
from prediction import Prediction
from prediction import predict
from compare import Bins, Clients
from compare import get_features,get_list


#uvicorn main:app --reload

#open http://127.0.0.1:8000/

#http://127.0.0.1:8000/redoc

#http://127.0.0.1:8000/docs


app = FastAPI()


# Sending a get request to the “/all” route with a request body. 
# The request body contains the key-value pair with the information
# We should expect a response with the list of client_ids

@app.get('/list/', response_model = Clients, response_model_exclude_unset=True)
def get_all():
    response = get_list()
    return response


# Sending a get request to the “/all” route with a request body. 
# The request body contains the key-value pair with the information
# We should expect a response with some information about the client

# Sending a get request to the “/scoring” route with a request body. 
# The request body contains the key-value pairs of the loaner information
# We should expect a response with the answer, the probability of that answer 
# the list of 20 features and the corresponding shap_values table  

@app.get('/scoring/{client_id}', response_model = Prediction, response_model_exclude_unset=True)
def get_score(client_id : int):
    response = predict(client_id)
    return response


# Sending a get request to the “/compare” route with a request body. 
# The request body contains the key-value pairs of the loaner information
# as well as the feature we want to compare the client to
# We should expect a response with the data target, list of bins and percent
#@app.get("/users/{user_id}/items/{item_id}")


@app.get('/client/{client_id}/feature/{feature}', response_model = Bins, response_model_exclude_unset=True)
def get_comparison_data(client_id : int, feature : str):
    response = get_features(client_id, feature)
    return response


# homepage route

@app.get("/")
async def root():
    return {"message": "Hello World"}

