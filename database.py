import os
import streamlit as st

from deta import Deta
from dotenv import load_dotenv

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from io import StringIO
from typing import List, Union

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate, StringPromptTemplate
from langchain.chains import LLMChain

# Load environmental variables
load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

# Initialize project key
deta = Deta(DETA_KEY)

#connecting to the base
db = deta.Base("user_information")

## MIGHT HAVE TO DEFINE PUT and GET FUNCTIONS HERE az
def insert_user(username: dict, name, password, email, gender, num_ex, biom_dict, injuries, ratings, exlist):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return db.put({"key": username, "name": name, "password": password, "email": email, "gender": gender, "num_ex": num_ex, "biom_dict": biom_dict, "injuries":injuries, "ratings": ratings, "ex_list": exlist})

def fetch_all_users():
    """Returns a dict of all users"""
    res = db.fetch()
    return res.items

def get_user_dict(username):
    """If not found, the function will return None"""
    return db.get(username)


def update_user(username, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    return db.update(updates, username)


def delete_user(username):
    """Always returns None, even if the key does not exist"""
    return db.delete(username)

def get_injuries(username):
    user_dict = db.get(username)
    injuries = user_dict['injuries']
    return injuries

def get_ratings(username):
    user_dict = db.get(username)
    ratings = user_dict['ratings']
    return ratings

def put():
    return db.put()

def get_num_ex(username):
    user_dict = db.get(username)
    num_ex = user_dict['num_ex']
    return num_ex

def get_ex_list(username):
    user_dict = db.get(username)
    ex_list = user_dict['ex_list']
    return ex_list

def delete_inj(username, del_inj):
    user_dict = db.get(username)
    str_inj = user_dict['injuries']
    str_ratings = user_dict['ratings']
    # making a list of injuries and ratings
    injuries = str_inj.split(', ')
    ratings = str_ratings.split(', ')
    # deleting the injury from the list
    try:
        ind = injuries.index(del_inj)
        injuries.pop(ind)
        ratings.pop(ind)
    except:
        print("The injury is not in your list of injuries.")
    u_str_inj = ', '.join(injuries)
    u_str_ratings = ', '.join(map(str, ratings))
    return update_user(username, {"injuries": u_str_inj, "ratings": u_str_ratings})

def add_inj(username, added_inj, added_rating):
    user_dict = db.get(username)
    str_inj = user_dict['injuries']
    str_ratings = user_dict['ratings']
    # making a list of injuries and ratings
    injuries = str_inj.split(', ')
    ratings = str_ratings.split(', ')
    # deleting the injury from the list
    for i in range(len(added_inj)):
        injuries.append(added_inj[i])
        ratings.append(added_rating[i])
    u_str_inj = ', '.join(injuries)
    u_str_ratings = ', '.join(map(str, ratings))
    return update_user(username, {"injuries": u_str_inj, "ratings": u_str_ratings})





