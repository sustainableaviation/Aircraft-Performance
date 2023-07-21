import numpy as np
# Formulas from Junzi Sun
def calculate(altitude, mach):
    # Constants
    R = 287
    gamma = 1.4
    # Calculate Temperature, Air Density and Velocity
    T = np.maximum(288.15 - 0.0065 * altitude, 216.65)
    rhotrop = 1.225 * (T / 288.15) ** 4.256848030018761
    dhstrat = np.maximum(0.0, altitude - 11000.0)
    rho = rhotrop * np.exp(-dhstrat / 6341.552161)
    flight_vel = mach * np.sqrt(gamma*R*T)

    return rho, flight_vel, T