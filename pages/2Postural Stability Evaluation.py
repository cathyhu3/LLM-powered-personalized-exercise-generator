import streamlit as st

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# KMEANS INPUTS:
# data points of COP avg vel from literature
df = pd.read_csv('newCOP_from_matlab.csv', header=None)
x = df.values.flatten().tolist()

# initializing session state variable
if 'PSscore' not in st.session_state:  
    st.session_state['PSscore'] = 0

# form for the participant's COP avg velocity
with st.form('form1'):
    st.markdown('<p style="color:LightGreen; font-size: 20px;">Postural Stability score</p>',unsafe_allow_html=True)
    in_x = st.text_input("input individual's COP average velocity")
    submitted_1 = st.form_submit_button(label = "Submit")
    

# KMEANS FUNCTION
def classification_of_ind(x,in_x):
    y = [0]*len(x)

    # k-means implementation
    data = list(zip(x, y))
    kmeans = KMeans(n_clusters=3, init='k-means++', random_state=1)
    kmeans.fit(data)

    # find the cluster centers
    pos_of_c = kmeans.cluster_centers_ # numpy array version of cluster centers
    pos_of_c = sorted(pos_of_c[:, 0].tolist()) # pos_of_c = a list of the positions of the cluster centers

    # setting up a data point from user input
    data_pt = np.array([[in_x,0]])
    c_label = kmeans.predict(data_pt) # cluster_label = using predict function to classify in_x to a cluster 

    # Separating Clusters
    data_labels = kmeans.labels_
    data_labels_np = np.array([data_labels])

    c_1 = np.array([]) # cluster 1
    c_2 = np.array([]) # cluster 2
    c_3 = np.array([]) # cluster 3
    for i in range(len(data_labels)):
        if data_labels[i] == 2:
            c_3 = np.append(c_3, (x[i])) # if point is labeled 2, then append to 3rd cluster
        if data_labels[i] == 1:
            c_2 = np.append(c_2, (x[i])) # if point is labeled 1, then append to 2nd cluster
        else:
            c_1 = np.append(c_1, (x[i])) # if point is labeled 0, then append to 1st cluster

    c_1 = list(zip(c_1,[0]*len(c_1)))
    c_2 = list(zip(c_2,[0]*len(c_2)))
    c_3 = list(zip(c_3,[0]*len(c_3)))

    # Z-score threshold
    z_thresh = 2.5

    # Normalize Clusters
    norm_c1 = StandardScaler()
    norm_c1.fit(c_1)

    norm_c2 = StandardScaler()
    norm_c2.fit(c_2)

    norm_c3 = StandardScaler()
    norm_c3.fit(c_3)

    # Find Z-score of data point relative to which cluster it's in
    if c_label == 2:
        dp_zscore = norm_c3.transform(data_pt) # z-score of the data point
        dp_zscore = np.abs(dp_zscore[:,0].tolist())
    if c_label == 1:
        dp_zscore = norm_c2.transform(data_pt)
        dp_zscore = np.abs(dp_zscore[:,0].tolist())
    else:
        dp_zscore = norm_c1.transform(data_pt) # z-score of the data point
        dp_zscore = np.abs(dp_zscore[:,0].tolist())

    # Outlier test: results --> inclonclusive if data point is an outlier of its cluster
    if dp_zscore >= z_thresh:
        if c_label == 0:
            message = '**Very Weak** Postural Stability'
            return message
        if c_label == 1:
            message = '**Very Strong** Postural Stability'
            return message
        else:
            message = 'Normal Postural Stability'
            return message
    else:
        return c_label
    
# KMEANS RESULTS
with st.expander('Grouping details'):
    st.write("The graph shows the k means clustered COP average velocities of 42 individuals from Kei Masani's 2014 study: 'Center of pressure velocity reflects body acceleration rather than body velocity during quiet standing'")
    st.image('grouped_COP.png')
    st.write("Link: https://www.sciencedirect.com/science/article/pii/S0966636213007030?via%3Dihub")
# the classification of the individual
if submitted_1:
    in_x = float(in_x)
    group = classification_of_ind(x,in_x)

    if group == 0:
        st.write("**Weak** Postural Stability")
        PS_score = 'weak postural stability'
    elif group == 1:
        st.write("**Strong** Postural Stability")
        PS_score = 'strong postural stability'
    elif group == 2:
        st.write("**Normal** Postural Stability")
        PS_score = 'normal postural stability'
    else:
        st.write(group)
        PS_score = group
    st.session_state['PSscore'] = PS_score