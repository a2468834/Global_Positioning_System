'''
    Programming Assignment #6
    
    Course: Global Positioning System
    Writer_ID: 0416047
    Writer_Name: Chuan-Chun, Wang
    Compiler: Python 3.8.3 [MSC v.1916 64 bit (AMD64)]
    Environment: Windows 10(1903) on Intel Core i5-5200U
'''
import sys
import math
import re
import numpy
import csv


class CONST:
    # GRS80 pre-defined constants
    a_e         = lambda : 6378137
    f           = lambda : 0.00335281068118
    w_e         = lambda : 7292115*(10**(-11))
    mu_e        = lambda : 3986005*(10**8)
    

# Input longitude, latitude, and ellipsoidal height
obs_phi     = float(input("Enter latitude: (in decimal degrees)\n"))
obs_lambda  = float(input("Enter longitude: (in decimal degrees)\n"))
obs_h       = float(input("Enter ellipsoidal height: (in meters)\n"))
print("\n")

# Convert degrees into radians
obs_phi    = math.radians(obs_phi)
obs_lambda = math.radians(obs_lambda)


# Step 1 : Convert ECEF LLH coordinates into XYZ coordinates (in meters)
# LLH := longitude, latitude, and ellipsoidal height
e_square = (2 * CONST.f()) - (CONST.f() * CONST.f())
N = CONST.a_e() / math.sqrt(1 - e_square * math.sin(obs_phi)**2)

obs_X = (N + obs_h) * math.cos(obs_phi) * math.cos(obs_lambda)
obs_Y = (N + obs_h) * math.cos(obs_phi) * math.sin(obs_lambda)
obs_Z = (N * (1-e_square) + obs_h) * math.sin(obs_phi)


# Step 2 : Reversely convert ECEF XYZ into LLH coordinates in order to check correctness
check_obs_lambda = math.atan2(obs_Y, obs_X)
# Iterative method
X2Y2          = math.sqrt(obs_X**2 + obs_Y**2)
check_obs_h   = 0
check_obs_phi = math.atan2(obs_Z, X2Y2*(1-e_square)) # ppi
for i in range(0, 1000):
    temp_N        = CONST.a_e() / math.sqrt(1 - e_square * math.sin(check_obs_phi)**2)
    check_obs_h   = (X2Y2 / math.cos(check_obs_phi)) - temp_N
    check_obs_phi = math.atan2(obs_Z, (X2Y2 * (1 - e_square * (temp_N / (temp_N + check_obs_h)))))
# Convert into degrees
check_obs_phi    = round(math.degrees(check_obs_phi), 4)
check_obs_lambda = round(math.degrees(check_obs_lambda), 4)
check_obs_h      = round(check_obs_h, 4)


# Print results
print("ECEF XYZ coordinates are:")
print("(using GRS80 reference ellipsoid)")
print("X : %.4f"%obs_X)
print("Y : %.4f"%obs_Y)
print("Z : %.4f"%obs_Z)
print("\n")
print("Reversely conversion for checking correctness:")
print("Latitude  : %.4f"%check_obs_phi)
print("Longitude : %.4f"%check_obs_lambda)
print("Height    : %.4f"%check_obs_h)
