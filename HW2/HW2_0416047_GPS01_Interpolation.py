'''
    Programming Assignment #2
    
    Course: Global Positioning System
    Writer_ID: 0416047
    Writer_Name: Chuan-Chun, Wang
    Compiler: Python 3.7.5 [MSC v.1916 64 bit (AMD64)]
    Environment: Windows 10(1903) on Intel Core i5-5200U
'''
import sys
import math


# WGS84 defining constants
class CONST:
    a_e   = lambda : 6378137
    f_inv = lambda : (1/298.257223563)
    w_e   = lambda : 72.92115*pow(10, -6)
    mu_e  = lambda : 3986004.418*pow(10, 8)


# Iterative method of Kepler's laws
# Source: Applied GPS for Engineers and Project Managers, Clement A. Ogaja(2011)
def iterKepler(iterNum, M, ecnt):
    currE = M
    nextE = 0
    for i in range(0, iterNum):
        nextE = M + ecnt*math.sin(currE)
        currE = nextE
    return nextE
''' 
# Source: lecture slide "廣播星曆說明-20151007.ppt"
def iterKepler(iterNum, M, ecnt):
    currE = M
    nextE = 0
    for i in range(0, iterNum):
        numerator   = currE - ecnt*math.sin(currE) - M
        denominator = 1 - ecnt*math.cos(currE)
        nextE = currE - (numerator/denominator)
        currE = nextE
    return nextE
'''


# Binary search within a list
def binSearch(input_list, target):
    low, up = 0, len(input_list)-1
    
    while low <= up:
        mid = (low+up)//2
        if input_list[mid][0] == float(target):
            return mid
        elif target > input_list[mid][0]:
            low = mid+1
        else:
            up = mid-1

    if low > len(input_list)-1:
            low = len(input_list)-1

    if abs((input_list[low][0]-target)) < abs((target-input_list[up][0])):
        return low
    else:
        return up


# Python reading file handler
if len(sys.argv) < 2:
    print("Without argument: input file name.")

try:
    brdc_ephm = open(sys.argv[1], 'r')
except:
    print("Read file error. ", sys.argv[1])
    sys.exit()


# Deal with some issues related to RINEX header
line_handler = brdc_ephm.readline().split()
if line_handler[0] != "2":
    print("Incompatible RINEX version, please use RINEX 2.")            # Check RINEX version number
    sys.exit()
if line_handler[1][0] != "N":
    print("Incompatible RINEX file type, please use Navigation file.")          # Check type of file
    sys.exit()


# Skip all of RINEX header
while True:
    line_handler = brdc_ephm.readline().split()
    if line_handler[0] == "END":
        break
fp_to_end_of_header = brdc_ephm.tell()


# Element format in 'GPS01_epoch_fp_list': second_offset, file_pointer
# time_offset = hour*3600 + minute*60 + second
GPS01_epoch_fp_list = []
while True:
    file_pointer = brdc_ephm.tell()
    line_handler = brdc_ephm.readline()

    if line_handler == "":
        break
    elif line_handler[ 0: 0+2] == " 1":
        second_offset = float(line_handler[12:12+2])*3600 + float(line_handler[15:15+2])*60 + float(line_handler[17:17+5])
        GPS01_epoch_fp_list.append(tuple([second_offset, file_pointer]))
    
    for i in range(0, 7):                                                             # Skip 7 lines
        brdc_ephm.readline()


# Main function
print("\nGPS01's position (X, Y, Z) at 2020/02/05 for every 15 minutes")
print("Unit: km, Coordinate system: WGS84\n")

for second_offset in range(0, 86400, 900):
    # Move brdc_ephm to first line of epoch
    brdc_ephm.seek(GPS01_epoch_fp_list[binSearch(GPS01_epoch_fp_list, second_offset)][1])

    # PRN / EPOCH / SV CLK
    line_input = brdc_ephm.readline()

    # BROADCAST ORBIT - 1
    line_input = brdc_ephm.readline()
    parameter_1st = line_input[ 3: 3+19].split('D')
    parameter_2nd = line_input[22:22+19].split('D')
    parameter_3rd = line_input[41:41+19].split('D')
    parameter_4th = line_input[60:60+19].split('D')

    IODE    = float(parameter_1st[0]) * pow(10, float(parameter_1st[1]))
    C_rs    = float(parameter_2nd[0]) * pow(10, float(parameter_2nd[1]))
    Delta_n = float(parameter_3rd[0]) * pow(10, float(parameter_3rd[1]))
    M_0     = float(parameter_4th[0]) * pow(10, float(parameter_4th[1]))

    # BROADCAST ORBIT - 2
    line_input = brdc_ephm.readline()
    parameter_1st = line_input[ 3: 3+19].split('D')
    parameter_2nd = line_input[22:22+19].split('D')
    parameter_3rd = line_input[41:41+19].split('D')
    parameter_4th = line_input[60:60+19].split('D')

    C_uc    = float(parameter_1st[0]) * pow(10, float(parameter_1st[1]))
    ecc     = float(parameter_2nd[0]) * pow(10, float(parameter_2nd[1]))
    C_us    = float(parameter_3rd[0]) * pow(10, float(parameter_3rd[1]))
    sqrt_a  = float(parameter_4th[0]) * pow(10, float(parameter_4th[1]))

    # BROADCAST ORBIT - 3
    line_input = brdc_ephm.readline()
    parameter_1st = line_input[ 3: 3+19].split('D')
    parameter_2nd = line_input[22:22+19].split('D')
    parameter_3rd = line_input[41:41+19].split('D')
    parameter_4th = line_input[60:60+19].split('D')

    TOE     = float(parameter_1st[0]) * pow(10, float(parameter_1st[1]))
    C_ic    = float(parameter_2nd[0]) * pow(10, float(parameter_2nd[1]))
    Omega_0 = float(parameter_3rd[0]) * pow(10, float(parameter_3rd[1]))
    C_is    = float(parameter_4th[0]) * pow(10, float(parameter_4th[1]))

    # BROADCAST ORBIT - 4
    line_input = brdc_ephm.readline()
    parameter_1st = line_input[ 3: 3+19].split('D')
    parameter_2nd = line_input[22:22+19].split('D')
    parameter_3rd = line_input[41:41+19].split('D')
    parameter_4th = line_input[60:60+19].split('D')

    i_0     = float(parameter_1st[0]) * pow(10, float(parameter_1st[1]))
    C_rc    = float(parameter_2nd[0]) * pow(10, float(parameter_2nd[1]))
    omega   = float(parameter_3rd[0]) * pow(10, float(parameter_3rd[1]))
    Omega_1 = float(parameter_4th[0]) * pow(10, float(parameter_4th[1]))

    # BROADCAST ORBIT - 5
    line_input = brdc_ephm.readline()
    parameter_1st = line_input[ 3: 3+19].split('D')
    parameter_2nd = line_input[22:22+19].split('D')
    parameter_3rd = line_input[41:41+19].split('D')
    parameter_4th = line_input[60:60+19].split('D')

    i_1 = float(parameter_1st[0]) * pow(10, float(parameter_1st[1]))

    # BROADCAST ORBIT - 6
    line_input = brdc_ephm.readline()

    # BROADCAST ORBIT - 7
    line_input = brdc_ephm.readline()

    # Calculate satellite position X, Y, Z
    # Step 1: WGS84 defining parameters

    # Step 2
    n_0 = math.sqrt( CONST.mu_e()/pow(sqrt_a, 6) )

    # Step 3
    # Broadcast ephemeris starts to count 0 second every Sunday.
    # 2020/02/05 is Wednesday, so its "0:0:0" should stand for 86400*3 seconds.
    t = second_offset + 86400*3
    t_k = t - TOE

    # Step 4
    n = n_0 + Delta_n

    # Step 5
    M = M_0 + n*t_k
    E = iterKepler(5, M, ecc)

    # Step 6 Calculate radius of f_k
    cos_f_k = (math.cos(E) - ecc) / (1 - ecc*math.cos(E))
    sin_f_k = (math.sqrt(1 - pow(ecc, 2)) * math.sin(E)) / (1 - ecc*math.cos(E))
    f_k = math.atan2(sin_f_k, cos_f_k)
    
    # Step 7
    temp = omega + f_k
    u_k = temp                                   + C_us*math.sin(2*temp) + C_uc*math.cos(2*temp)
    r_k = pow(sqrt_a, 2)*(1 - ecc*math.cos(E))   + C_rs*math.sin(2*temp) + C_rc*math.cos(2*temp)
    i_k = i_0 + i_1*t_k                          + C_is*math.sin(2*temp) + C_ic*math.cos(2*temp)

    # Step 8
    l_k = Omega_0 + (Omega_1 - CONST.w_e())*t_k - CONST.w_e()*TOE

    # Step 9
    x = r_k*math.cos(u_k)
    y = r_k*math.sin(u_k)

    # Step 10
    X = x*math.cos(l_k) - y*math.cos(i_k)*math.sin(l_k)
    Y = x*math.sin(l_k) + y*math.cos(i_k)*math.cos(l_k)
    Z = y*math.sin(i_k)
    print("(%.6f, %.6f, %.6f)"%(X/1000, Y/1000, Z/1000))
