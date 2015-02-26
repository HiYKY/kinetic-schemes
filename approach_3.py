"""
Kinetic solution based on initial wood density and reaction rates, for example
pw = pwi + rww*dt. Plots conversion of wood as a normalized concentration such
as pw/rhow, pc/rhow, etc.

Requirements:
Python 3, Numpy, Matplotlib

References:
1) Papadikis 2010a
2) Chan 1985 and Blasi 1993b
"""

# Modules
#------------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as py

# Parameters from Papadikis 2010a
#------------------------------------------------------------------------------

rhow = 700  # density of wood, kg/m^3
Tinf = 773  # ambient temp, K

# Kinetic parameters from Chan 1985 and Blasi 1993b
#------------------------------------------------------------------------------

# A = pre-exponential factor, 1/s and E = activation energy, kJ/mol
A1 = 1.3e8;  E1 = 140    # wood -> gas
A2 = 2e8;    E2 = 133    # wood -> tar
A3 = 1.08e7; E3 = 121    # wood -> char
A4 = 4.28e6; E4 = 108    # tar -> gas
A5 = 1e6;    E5 = 108    # tar -> char

R = 0.008314    # universal gas constant, kJ/mol*K

# Initial Calculations
#------------------------------------------------------------------------------

dt = 0.01   # time step, delta t
tmax = 25   # max time, s
t = np.linspace(0, tmax, num=tmax/dt)   # time vector
p = len(t)  # total number of time steps

# Calculate Kinetic Reactions and Concentrations
#------------------------------------------------------------------------------

T = Tinf
K1 = A1 * np.exp(-E1 / (R * T))   # wood -> gas
K2 = A2 * np.exp(-E2 / (R * T))   # wood -> tar
K3 = A3 * np.exp(-E3 / (R * T))   # wood -> char
K4 = A4 * np.exp(-E4 / (R * T))   # tar -> gas
K5 = A5 * np.exp(-E5 / (R * T))   # tar -> char

# initial wood, gas, tar, char concentrations as density, kg/m^3
pw = [rhow] # wood
pg = [0]    # gas
pt = [0]    # tar
pc = [0]    # char

rww = [-(K1 + K2 + K3) * pw[0]] # rate of wood consumption
rwg = [K1 * pw[0]]              # rate of gas production from wood
rwt = [K2 * pw[0]]              # rate of tar production from wood
rwc = [K3 * pw[0]]              # rate of char production from wood
rtg = [K4 * pt[0]]              # rate of gas production from tar
rtc = [K5 * pt[0]]              # rate of char production from tar

# kinetics for primary and secondary reactions
for i in range(1, p):
    rww.append(-(K1 + K2 + K3) * pw[i-1])
    rwg.append(K1 * pw[i-1])
    rwt.append(K2 * pw[i-1])
    rwc.append(K3 * pw[i-1])
    rtg.append(K4 * pt[i-1])
    rtc.append(K5 * pt[i-1])
    pw.append(pw[i-1] + rww[i]*dt)
    pg.append(pg[i-1] + (rwg[i] + rtg[i])*dt)
    pt.append(pt[i-1] + (rwt[i] - rtg[i] - rtc[i])*dt)
    pc.append(pc[i-1] + (rwc[i] + rtc[i])*dt)

# normalize units
pwn = [x/rhow for x in pw]
pgn = [x/rhow for x in pg]
ptn = [x/rhow for x in pt]
pcn = [x/rhow for x in pc]
    
# Plot Results
#------------------------------------------------------------------------------

py.rcParams['xtick.major.pad'] = 8
py.rcParams['ytick.major.pad'] = 8
py.rcParams['lines.linewidth'] = 2

py.figure(3)
py.plot(t, pwn, label='wood')
py.plot(t, pgn, label='gas')
py.plot(t, ptn, label='tar')
py.plot(t, pcn, label='char')
py.legend(loc='best', numpoints=1)
py.title('Reactions at T = %.f K' % Tinf)
py.xlabel('Time (s)')
py.ylabel('Concentration (-)')
py.grid()
py.show()