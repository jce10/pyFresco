pyFresco is a python wrapper script that calculates optical model potential parameters and creates FRESCO input cards, which are then run using the FRESCO program.

**The current usage of pyFresco calculates proton & neutron optical potentials from Koning and Delaroche, and calculates deuteron optical potentials under the Adiabatic Distorted Wave Approximation, used for (d,p) reactions. Further generalization to other reactions & potentials can be done, but currently is not employed**

Create & edit the reaction_config.json file which is shown as such:
'''
{
  "reaction": "49Ti(d,p)50Ti",
  "beam_energy": 16.0,
  "Z": 22,
  "AT": 49,
  "residual_mass": 50,
  "mass_in": 48.9478,
  "mass_out": 49.9447,
  "label_in": "49Ti",
  "label_out": "50Ti",
  "Q_value": 8.7146,
  "binding_energy": 10.939,
  "gs_spin": 3.5,
  "gs_parity": "-1",
  "angle_min": 15.0,
  "angle_max": 65.0,
  "angle_step": 0.1,
  "executable_path": "./bin/fresco"
}
'''

The other file that is used when running the pyfresco.py code is the input_generator.inp file, which contains information about the Excitation energy, spin (J), and transfer configuration (n,l,j) to the state of interest. The program will be ran for every state of interest in the .inp file, create a fresco input and output card (.fri and .fro files) as well as the outputted angular distribution with the naming scheme {nucleus}_{excitation_energy}_{transfer_config}_{JPi}.txt, which contains the elastic and inelastic cross-sections for the channels.

An example for the 49Ti(d,p)50Ti reaction to a 3+ 4.172 MeV state is loaded as default for the reaction_config.json and input_generator.inp files.

Run pyfresco.py by simply:
python pyfresco.py

Once ran, there are two additional .py files that will allow for extraction of the cross-sections in a simple text file and then for that data to be plotted.

Usage:
Run getFresco_output.py by:
python getFresco_output.py <{nucleus}_{excitation_energy}_{transfer_config}_{JPi}.txt>

This will generate a file with the same naming convetion, suffixed by .sorted -- such as {nucleus}_{excitation_energy}_{transfer_config}_{JPi}.sorted

Then, run the plot_fresco.py file by:

python plot_fresco.py {nucleus}_{excitation_energy}_{transfer_config}_{JPi}.sorted

Which will plot the angular distribution outputted by FRESCO and allow it be visualized.
