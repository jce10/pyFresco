"""
 Module to house the FRESCO input card for ADWA calculations. 

"""

def build_adwa_input(shared, state, deuteron_pot, proton_pot, config) -> str:

    # get all the variables from the config file and the state dictionary to fill in the FRESCO input card template
    Z_fmt = shared["Z_fmt"]
    mass_in = shared["mass_in"]
    mass_out = shared["mass_out"]
    gs_spin_fmt = shared["gs_spin_fmt"]
    gs_parity_fmt = shared["gs_parity_fmt"]
    th_min = shared["th_min"]
    th_max = shared["th_max"]
    th_step = shared["th_step"]
    at = shared["at"]
    residual_mass = shared["residual_mass"]
    beam_energy = shared["beam_energy"]

    q = state["q"]
    e = state["e"]
    be = state["be"]
    n = state["n"]
    l_letter = state["l_letter"]
    l_value = state["l_value"]
    js_transfer = state["js_transfer"]
    js_finalstate = state["js_finalstate"]
    final_parity = state["final_parity"]


    fri = f"""{config['reaction']}, {js_finalstate}{final_parity} {e} MeV {n}{l_letter}{js_transfer}
0.10    55.0    0.20    0.20    30.0    -6.0
 00. 20.  +.00   F F
0  {th_min}     {th_max}  {th_step}  1
0.0    0 1   1 1  48          .000    0.   0.001
 1 1 0 0 2 3 0 0-3 1 0 0 1
2H      2.0141  1.0        1  {config['label_in']:<8}{mass_in} {Z_fmt}    0.0000
1.0   +1 0.0               1 {gs_spin_fmt}   {gs_parity_fmt} 0.000
1H      1.0078  1.0        1  {config['label_out']:<8}{mass_out} {Z_fmt}    {q}
0.5   +1 0.0               2  {js_finalstate}   {final_parity} {e}

  1 0  0    {at}     0.0   {deuteron_pot['rc0']:5.3f}
  1 1  0   {deuteron_pot['V']:5.2f}   {deuteron_pot['r0']:5.3f}   {deuteron_pot['a']:5.3f}   {deuteron_pot['Vi']:5.3f}   {deuteron_pot['ri0']:5.3f}   {deuteron_pot['ai']:5.3f}
  1 2  0                           {deuteron_pot['Vsi']:5.2f}   {deuteron_pot['rsi0']:5.3f}   {deuteron_pot['asi']:5.3f}
  1 3  0   {deuteron_pot['Vso']:5.2f}   {deuteron_pot['rso0']:5.3f}   {deuteron_pot['aso']:5.3f}   {deuteron_pot['Vsoi']:5.2f}   {deuteron_pot['rsoi0']:5.3f}   {deuteron_pot['asoi']:5.3f}
  2 0  0    {residual_mass}     0.0   {proton_pot['rc0']:5.3f}
  2 1  0   {proton_pot['V']:5.2f}   {proton_pot['r0']:5.3f}   {proton_pot['a']:5.3f}   {proton_pot['Vi']:5.3f}   {proton_pot['ri0']:5.3f}   {proton_pot['ai']:5.3f}
  2 2  0                           {proton_pot['Vsi']:5.2f}   {proton_pot['rsi0']:5.3f}   {proton_pot['asi']:5.3f}
  2 3  0   {proton_pot['Vso']:5.2f}   {proton_pot['rso0']:5.3f}   {proton_pot['aso']:5.3f}   {proton_pot['Vsoi']:5.2f}   {proton_pot['rsoi0']:5.3f}   {proton_pot['asoi']:5.3f}
  3 0  0    1.00            1.25
  3 1  5    1.00            1.00
  3 3  5    1.00            1.00
  3 4  5    1.00            1.00
  3 7  5    1.00            1.00
  4 0  0    {residual_mass}     0.0    1.25
  4 1  0    50.0    1.25    0.65
  4 3  0     6.0    1.25    0.65
0
  1  2 1 2-1 3   1 0 2 0.5 1 1.5 1  3  0  2.2260  0  3  0
  3    1 2-2 0   {n} {l_value}   0.5   {js_transfer}    4  0  {be}  1  1  0

  -2   1   7 0-1 0
       1   1   1   1  1.0000
       2   1   1   3  1.0000
0
   0   1   1
{beam_energy}
EOF
"""
    return fri