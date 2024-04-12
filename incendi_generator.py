import pandas as pd 
import numpy as np
import random
from scipy.ndimage import gaussian_filter

def generate_incendi_data(n,name,sigma = 1,lakes = 0):
    
    dades = {}
    dades["file title"]=name
    humitat = np.random.rand(n,n)
    df = gaussian_filter(humitat, sigma=sigma)
    for i in range(lakes):
        df = add_lake(df, random.randint(0,n//8), 16)
    dades["max"] = max(df.flatten())*100
    dades["min"] = min(df.flatten())*100
    df = df.flatten()
    df = pd.DataFrame(df)
    df = df*100
    df = df.round(0)
    df.to_csv(name+".csv", index=False)
    dades["rows"]=n
    dades["columns"]=1
    df2 = pd.DataFrame(dades, index = ["file title","rows","columns","max","min"])
    df2.to_csv(name+"_dades.csv", index=False)

def add_lake(data_matrix, r, humidity,deformation_factor_inc=15):
    rows, cols = data_matrix.shape
    # Randomly choose starting point of the river
    start_i = np.random.randint(0, rows)
    start_j = np.random.randint(0, cols)
    #generate a circular lake
    deformation_factor = 0
    for i in range(rows):
        for j in range(cols):
            # Introduce randomness to the lake boundary
            if (i - start_i)**2 + (j - start_j)**2 < r**2 + deformation_factor:
                data_matrix[i, j] = humidity
            deformation_factor += random.randint(-deformation_factor_inc, deformation_factor_inc)
    
    # now generate a circular lake with deformations
    
    return data_matrix
    
    
    

generate_incendi_data(200,"humitat",1,2)
generate_incendi_data(200,"combustible")

