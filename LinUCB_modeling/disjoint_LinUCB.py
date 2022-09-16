# import necessary packages
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import json


# global constants
ARMS = ["Academic Services", "Career Exploration and Coaching", "Wellness Enhancement Opportunities",
        "Physical Wellbeing Resources", "Mindfulness Resources", "Social Wellbeing and Engagement",
        "Spiritual Engagement and Volunteering", "Disability Services", "Academic Support - Dean of Students",
        "GT Counseling Center", "Other"]
CONTEXT_DIM = 25


# # reading JSON from file
def get_data_from_JSONfile(filepath):
    f = open(filepath)
    data = json.load(f)
    f.close()

    return data


# # reading JSON from a JSON string
def get_data_from_JSONstring(jstring):
    data = json.loads(jstring)

    return data


def get_prediction(input_context, alpha, input_A=None, input_b=None):
    '''
    Input:
        input_context: survey response data, a 1D CONTEXT_DIM dimensional array
        alpha: exloration parameter
        input_A: input A from previous training sessions
        input_b: input b from previous training sessions
    
    Output:
        prediction: the arm that should be pulled, a string name 
    '''
    # convert input context to an np array
    context = np.array(input_context)

    # load input A and b
    A = {arm: np.identity(CONTEXT_DIM) for arm in ARMS}
    if(input_A is not None):
        A = input_A

    b = {arm: np.zeros(CONTEXT_DIM) for arm in ARMS}
    if(input_b is not None):
        b = input_b

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


def update_model_parameters(input_context, prediction, ground_truth, input_A, input_b):
    '''
    Input:
        input_context: survey response data, a 1D CONTEXT_DIM dimensional array
        alpha: exloration parameter
        input_A: input A from previous training sessions
        input_b: input b from previous training sessions
    
    Output:
        output_A_arm: updated A for chosen arm (prediction) given new validation
        output_b_arm: updated b for chosen arm (prediction) given new validation
    '''
    # convert input context to an np array
    context = np.array(input_context)

    # generate reward given prediction and ground truth (true arm)
    r = generate_reward(prediction, ground_truth)

    output_A_arm = input_A[prediction] + ( context.reshape((CONTEXT_DIM,1)) @ context.reshape((1,CONTEXT_DIM)) )
    output_b_arm = input_b[prediction] + (r * context)
    # Note: these are for the pulled arm (so need to set A[prediction] = output_A_arm, and
    # b[prediction] = output_b_arm to actually update the values)

    return output_A_arm, output_b_arm


def generate_reward(prediction, ground_truth):
    #TODO: figure out how to calculate reward
    return None