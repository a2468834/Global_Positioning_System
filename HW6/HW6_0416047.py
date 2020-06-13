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

fptr    = open('out.csv', 'w', newline='')

class CONST:
    # WGS84 pre-defined constants
    a_e         = lambda : 6378137
    f_inv       = lambda : 298.257223563
    w_e         = lambda : 72.92115*pow(10, -6)
    mu_e        = lambda : 3986004.418*pow(10, 8)
    
    # Observer's longitude (121°35′00"), latitude (25°45′00"), and ellipsoidal height
    obs_phi     = lambda : math.radians(25+(45/60))    # latitude (in rad)
    obs_lambda  = lambda : math.radians(121+(35/60))   # longitude (in rad)
    obs_h       = lambda : 100.0                       # in meters


# Python reading file handler
if len(sys.argv) < 2:
    print("Missing arguments: input file name.\n")

try:
    sp3_ephm = open(sys.argv[1], 'r')
except:
    print("Read file error. ", sys.argv[1])
    sys.exit()


# Deal with some issues related to RINEX header
line_handler = sp3_ephm.readline()
if line_handler[1] != "c":
    print("Incompatible SP3 version, please use SP3-c.")                # Check RINEX version number
    sys.exit()
if line_handler[2] != "P":
    print("Incompatible SP3 file type, please use position SP3 file.")          # Check type of file
    sys.exit()


# Skip all of SP3 header
for i in range(0, 21):
    line_handler = sp3_ephm.readline()

# Header of first epoch
line_handler = sp3_ephm.readline()

# Main function
pattern = re.compile(r'(P)(?P<PRN>G\d{2})(?P<X_coord> *[-]?\d+\.\d+)(?P<Y_coord> *[-]?\d+\.\d+)(?P<Z_coord> *[-]?\d+\.\d+)')      # Split strings into 'mantissa' and 'exponent'

# Step 1 : Prepare satellites' ECEF XYZ coordinates (in km)
# Read first epoch record into a list of dictionaries
sat_position = []
for i in range(0, 32):
    line_handler = sp3_ephm.readline()
    line_handler = list(re.finditer(pattern, line_handler))        # Parsing with regular expression
    temp = {
             'PRN'  : line_handler[0].group('PRN'),
             'X'    : float(line_handler[0].group('X_coord')),
             'Y'    : float(line_handler[0].group('Y_coord')),
             'Z'    : float(line_handler[0].group('Z_coord'))
           }
    sat_position.append(temp)


# Step 2 : Prepare observer's ECEF XYZ coordinates (in km)
e_square = (2 / CONST.f_inv()) - (1 / CONST.f_inv() / CONST.f_inv())
N = CONST.a_e() / math.sqrt(1 - e_square * math.sin(CONST.obs_phi()) * math.sin(CONST.obs_phi()))

obs_position = {
                 'X' : (N + CONST.obs_h()) * math.cos(CONST.obs_phi()) * math.cos(CONST.obs_lambda()) / 1000,
                 'Y' : (N + CONST.obs_h()) * math.cos(CONST.obs_phi()) * math.sin(CONST.obs_lambda()) / 1000,
                 'Z' : (N * (1-e_square) + CONST.obs_h()) * math.sin(CONST.obs_phi()) / 1000
               }


# Step 3 : Calculate ${\Delta}\overline{X}$
Delta_X_bar = []
for i in range(0, 32):
    temp = {
             'PRN'  : sat_position[i]['PRN'],
             'coord': numpy.array([sat_position[i]['X']-obs_position['X'], sat_position[i]['Y']-obs_position['Y'], sat_position[i]['Z']-obs_position['Z']])
           }
    Delta_X_bar.append(temp)


# Step 4 : Convert ${\Delta}\overline{X}$ from ECEF to horizontal coordinate system
trans_matrix = numpy.zeros((3, 3))
trans_matrix[0][0] = -math.sin(CONST.obs_phi())*math.cos(CONST.obs_lambda())
trans_matrix[0][1] = -math.sin(CONST.obs_lambda())
trans_matrix[0][2] = math.cos(CONST.obs_phi())*math.cos(CONST.obs_lambda())
trans_matrix[1][0] = -math.sin(CONST.obs_phi())*math.sin(CONST.obs_lambda())
trans_matrix[1][1] = math.cos(CONST.obs_lambda())
trans_matrix[1][2] = math.cos(CONST.obs_phi())*math.sin(CONST.obs_lambda())
trans_matrix[2][0] = math.cos(CONST.obs_phi())
trans_matrix[2][1] = 0
trans_matrix[2][2] = math.sin(CONST.obs_phi())
trans_matrix = numpy.transpose(trans_matrix)                      # inverse matrix of 'trans_matrix'

for i in range(0, 32):
    Delta_X_bar[i]['coord'] = numpy.matmul(trans_matrix, Delta_X_bar[i]['coord'])


# Step 5 : Calculate satellites' horizontal (A, beta, r) coordinates (in degrees)
sat_direction = []
for i in range(0, 32):
    temp = {
             'PRN'  : sat_position[i]['PRN'],
             'A'    : round(180 + math.degrees(math.atan2(Delta_X_bar[i]['coord'][1], Delta_X_bar[i]['coord'][0])), 3),
             'beta' : round(math.degrees(math.atan2(Delta_X_bar[i]['coord'][2], math.sqrt(Delta_X_bar[i]['coord'][0]**2 + Delta_X_bar[i]['coord'][1]**2))), 3),
             'r'    : round(math.sqrt(Delta_X_bar[i]['coord'][0]**2 + Delta_X_bar[i]['coord'][1]**2 + Delta_X_bar[i]['coord'][2]**2), 3)
           }
    sat_direction.append(temp)


# Print results
keys    = sat_direction[0].keys()
writer  = csv.DictWriter(fptr, keys)
writer.writeheader()
writer.writerows(sat_direction)
