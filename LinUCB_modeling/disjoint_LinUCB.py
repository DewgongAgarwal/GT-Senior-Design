# import necessary packages
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import json


# global constants
ARMS = ["Academic Services", "Career Exploration and Coaching", "Wellness Enhancement Opportunities",
        "Physical Wellbeing Resources", "Mindfulness Resources", "Social Wellbeing and Engagement",
        "Spiritual Engagement and Volunteering", "Disability Services", "Academic Support - Dean of Students",
        "One-on-One Consultation", "Other"]
CONTEXT_DIM = 25
alpha = 0.05

adjacency_list = {
    ("Academic Services", "Academic Support - Dean of Students") : 0.5,
    ("Academic Support - Dean of Students", "Academic Services") : 0.3
}


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


def get_prediction(input_context, input_A=None, input_b=None):
    '''
    Input:
        input_context: survey response data, a 1D CONTEXT_DIM dimensional array
        input_A: passed in list of matrices for A
        input_b: passed in list of vectors for b
    
    Output:
        prediction: the arm that should be pulled, a string name 
    '''
    # TODO: read A and b from JSON file --> maybe should check if input_A, input_b not None
    A = get_data_from_JSONfile("A.json")
    # is A = {arm: np.identity(CONTEXT_DIM) for arm in ARMS} on start
    b = get_data_from_JSONfile("b.json")
    # is b = {arm: np.zeros(CONTEXT_DIM) for arm in ARMS}

    # convert input context to an np array
    context = np.array(input_context)

    # run model on current parameters
    UCB = []
    for arm in ARMS:
        # theta_hat = A[arm]^{-1} b[arm]
        theta_hat = np.linalg.solve(A[arm], b[arm])
        # ucb = theta_hat^T context + alpha * sqrt(context^T A[arm]^{-1} context)
        ucb = np.dot(theta_hat, context) + alpha * np.sqrt(np.dot(np.dot(context, np.linalg.inv(A[arm])), context))
        UCB.append(ucb)

    max_ucb = np.max(UCB)
    candidates = [arm for arm in ARMS if UCB[arm] == max_ucb]
    prediction = np.random.choice(candidates)

    return prediction


def update_model_parameters(input_context, prediction, ground_truth):
    '''
    Input:
        input_context: survey response data, a 1D CONTEXT_DIM dimensional array
        prediction: predicted arm to pull, result from model
        ground_truth: true value of arm to pull, result from validation from GTCC
    '''
    # TODO: read A and b from JSON file
    A = get_data_from_JSONfile("A.json")
    b = get_data_from_JSONfile("b.json")

    # convert input context to an np array
    context = np.array(input_context)

    # generate reward given prediction and ground truth (true arm)
    r = generate_reward(prediction, ground_truth)

    A[prediction] = A[prediction] + ( context.reshape((CONTEXT_DIM,1)) @ context.reshape((1,CONTEXT_DIM)) )
    b[prediction] = b[prediction] + (r * context)
    # Note: these are for the pulled arm (so need to set A[prediction] = output_A_arm, and
    # b[prediction] = output_b_arm to actually update the values)

    # replace JSON file contents
    with open("A.json", "w") as Afile:
        json.dump(A, Afile)
    
    with open("b.json", "w") as bfile:
        json.dump(b, bfile)


def generate_reward(prediction, ground_truth):
    #TODO: figure out how to calculate reward
    if(prediction == ground_truth):
        return 1.0
    else:
        if((ground_truth, prediction) in adjacency_list):
            return adjacency_list[(ground_truth, prediction)]
        else:
            return 0.0
