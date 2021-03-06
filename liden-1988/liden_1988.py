import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp


def dcdt_liden(t, y):
    """
    System of ODEs representing the biomass pyrolysis kinetic reactions from
    Liden 1988. Reactions in the kinetic scheme are

        Reaction 1: wood -> tar
        Reaction 2: tar -> gas
        Reaction 3: wood -> (gas + char)

    Parameters
    ----------
    t : scalar
        Time [s] at which reactions are evaluated
    y : ndarray
        Solution state for mass fractions [-] where
            wood = y[0]
            gas = y[1]
            tar = y[2]
            gaschar = y[3]

    Returns
    -------
    sol : object
        Solution containing mass fractions at each time step. Time vector is
        sol.t and corresponding mass fraction array is sol.y where
            wood = sol.y[0]
            gas = sol.y[1]
            tar = sol.y[2]
            gaschar = sol.y[3]

    References
    ----------
    A.G. Liden, F. Berruti and D.S. Scott. A Kinetic Model for the Production
    of Liquids from the Flash Pyrolysis of Biomass. Chemical Engineering
    Communications, vol. 65, pp. 207-221, 1988.
    """

    wood = y[0]         # mass fraction of wood [-]
    tar = y[2]          # mass fraction of tar [-]
    temp = 773.15       # temperture [K]
    rgas = 0.008314     # universal gas constant [kJ/(mol K)]
    phistar = 0.703     # maximum theoretical tar yield [-]

    # reaction rate constants for each pathway
    # note that 𝝓 = k1 / k and k = k1 + k3
    #
    # k = a exp(-e / rt) is form of the rate constant equation where
    #   k = reaction rate constant [1/s]
    #   a = pre-factor [1/s]
    #   e = activation energy [kJ/mol]
    k = 1.0e13 * np.exp(-183.3 / (rgas * temp))     # wood -> tar and wood -> (gas + char)
    k1 = k * phistar                                # wood -> tar
    k2 = 4.28e6 * np.exp(-107.5 / (rgas * temp))    # tar -> gas
    k3 = k - k1                                     # wood -> (gas + char)

    # reaction rate equations as system of ODEs to solve
    dwood_dt = -k * wood
    dgas_dt = k2 * tar
    dtar_dt = k1 * wood - k2 * tar
    dgaschar_dt = k3 * wood

    return dwood_dt, dgas_dt, dtar_dt, dgaschar_dt


# Parameters
# ----------------------------------------------------------------------------

t_span = (0, 25)        # time span to evaluate solution [s]
y0 = [1, 0, 0, 0]       # initial mass fractions, start with all wood [-]

# Calculate mass fractions as batch reactor
# ----------------------------------------------------------------------------

# solve for mass fractions at each time point
sol = solve_ivp(dcdt_liden, t_span, y0)

# total mass fractions should equal one
tot1 = sol.y[0] + sol.y[1] + sol.y[2] + sol.y[3]

# assume a fixed carbon to estimate individual char and gas yields
phistar = 0.703             # maximum theoretical tar yield [-]
fc = 0.14                   # weight fraction of fixed carbon in wood
c3 = fc / (1 - phistar)     # char fraction for wood -> (gas+char)
g3 = 1 - c3                 # gas fraction for wood -> (gas+char)

# mass fractions for each component
wood = sol.y[0]
gas = sol.y[1] + g3 * sol.y[3]
tar = sol.y[2]
char = c3 * sol.y[3]

# total mass fractions should equal one
tot2 = wood + gas + tar + char

# Plot
# ----------------------------------------------------------------------------

fig, ax = plt.subplots(tight_layout=True)
ax.plot(sol.t, sol.y[0], label='wood')
ax.plot(sol.t, sol.y[1], label='gas')
ax.plot(sol.t, sol.y[2], label='tar')
ax.plot(sol.t, sol.y[3], label='gaschar')
ax.plot(sol.t, tot1, 'k:', label='total')
ax.grid(color='0.9')
ax.legend(loc='best')
ax.set_frame_on(False)
ax.set_xlabel('Time [s]')
ax.set_ylabel('Mass fraction [-]')
ax.tick_params(color='0.9')

fig, ax = plt.subplots(tight_layout=True)
ax.plot(sol.t, wood, label='wood')
ax.plot(sol.t, gas, label='gas')
ax.plot(sol.t, tar, label='tar')
ax.plot(sol.t, char, label='char')
ax.plot(sol.t, tot2, 'k:', label='total')
ax.grid(color='0.9')
ax.legend(loc='best')
ax.set_frame_on(False)
ax.set_xlabel('Time [s]')
ax.set_ylabel('Mass fraction [-]')
ax.tick_params(color='0.9')

plt.show()
