import matplotlib.pyplot as plt
import numpy as np
import sys

# check for command line input
if len(sys.argv) < 2:
    print("Usage: python3 plot_fresco.py <filename>")
    sys.exit(1)

input_filename = sys.argv[1]

# read data from the user-supplied file
try:
    data = np.loadtxt(input_filename)
    plt.plot(data[:,0], data[:,1], label=input_filename)
except Exception as e:
    print(f"Error reading or plotting file '{input_filename}': {e}")
    sys.exit(1)

# plot settings
plt.yscale('log')
plt.xlabel('Center of Mass Angle (degrees)')
plt.ylabel('Cross Section (Arb Units)')
plt.legend()
plt.show()
