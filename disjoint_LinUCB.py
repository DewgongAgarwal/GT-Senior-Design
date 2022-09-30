# import necessary packages
from os import pread
import numpy as np
import json


# global constants
ARMS = ["Academic Services", "Career Exploration and Coaching", "Wellness Enhancement Opportunities",
        "Physical Wellbeing Resources", "Mindfulness Resources", "Social Wellbeing and Engagement",
        "Spiritual Engagement and Volunteering", "Disability Services", "Academic Support - Dean of Students",
        "One-on-One Consultation", "Other"]
CONTEXT_DIM = 29
alpha = 0.05

adjacency_list = {
    ("Academic Services", "Academic Support - Dean of Students") : 0.5,
    ("Academic Support - Dean of Students", "Academic Services") : 0.3
}

def _resetJSON():
    Adict = {}
    bdict = {}

    for arm in ARMS:
        Adict[arm] = list(map(list, np.identity(CONTEXT_DIM)))
        bdict[arm] = list(np.zeros(CONTEXT_DIM))

    with open("A.json", "w") as Afile:
        json.dump(Adict, Afile)
    with open("b.json", "w") as bfile:
        json.dump(bdict, bfile)


# reading JSON from file
def get_data_from_JSONfile(filepath):
    f = open(filepath)
    data = json.load(f)
    f.close()

    return data


# reading JSON from a JSON string
def get_data_from_JSONstring(jstring):
    data = json.loads(jstring)

    return data

def _correctSize(array, inputSize, requiredSize):
    if inputSize == requiredSize:
        return array
    elif inputSize > requiredSize:
        return array[:requiredSize]
    else:
        return np.append(array, np.zeros(requiredSize - inputSize))


def get_prediction(input_context):
    '''
    Input:
        input_context: survey response data, a 1D CONTEXT_DIM dimensional array
        input_A: passed in list of matrices for A
        input_b: passed in list of vectors for b
    
    Output:
        prediction: the arm that should be pulled, a string name 
    '''
    print(input_context)
    # TODO: read A and b from JSON file --> maybe should check if input_A, input_b not None
    A = get_data_from_JSONfile("A.json")
    # is A = {arm: np.identity(CONTEXT_DIM) for arm in ARMS} on start
    b = get_data_from_JSONfile("b.json")
    # is b = {arm: np.zeros(CONTEXT_DIM) for arm in ARMS}
    size = len(b[ARMS[0]])
    # convert input context to an np array
    context = _correctSize(np.array(input_context), CONTEXT_DIM, size)

    # run model on current parameters
    UCB = []
    for arm in ARMS:
        # theta_hat = A[arm]^{-1} b[arm]
        theta_hat = np.linalg.solve(A[arm], b[arm])
        # ucb = theta_hat^T context + alpha * sqrt(context^T A[arm]^{-1} context)
        ucb = np.dot(theta_hat, context) + alpha * np.sqrt(np.dot(np.dot(context, np.linalg.inv(A[arm])), context))
        UCB.append(ucb)

    max_ucb = np.max(UCB)
    candidates = [ARMS[arm] for arm in range(len(ARMS)) if UCB[arm] == max_ucb]
    prediction = np.random.choice(candidates)

    return prediction


def update_model_parameters(input_context, prediction, ground_truth):
    try:
        A = get_data_from_JSONfile("A.json")
        b = get_data_from_JSONfile("b.json")

        size = len(b[ARMS[0]])

        context = _correctSize(np.array(input_context), CONTEXT_DIM, size)

        r = generate_reward(prediction, ground_truth)

        A[prediction] = A[prediction] + ( context.reshape((size,1)) @ context.reshape((1,size)) )
        b[prediction] = b[prediction] + (r * context)

        A[prediction] = list(map(list, A[prediction]))
        b[prediction] = list(b[prediction])

        with open("A.json", "w") as Afile:
            json.dump(A, Afile)
        
        with open("b.json", "w") as bfile:
            json.dump(b, bfile)
    except: return


def generate_reward(prediction, ground_truth):
    if(prediction == ground_truth):
        return 1.0
    else:
        if((ground_truth, prediction) in adjacency_list):
            return adjacency_list[(ground_truth, prediction)]
        else:
            return 0.0