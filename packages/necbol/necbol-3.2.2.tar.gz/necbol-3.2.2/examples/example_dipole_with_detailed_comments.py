
"""
  This is a minimal example of how to use the NECBOL library to model an antenna,
  with comments explaining how the NECBOL interface works.
"""

#-------------------------------------------------------------------------------------------------------------------
# Import NECBOL 
#-------------------------------------------------------------------------------------------------------------------
from necbol import *

#-------------------------------------------------------------------------------------------------------------------
# Start an antenna model called model (it can be called anything acceptable as a Python variable),
# specifying where the working folder should be made, and where the nec executable is on your system
#-------------------------------------------------------------------------------------------------------------------
model = NECModel(working_dir="nec_wkg",
                 model_name = "Vertical Dipole",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

#-------------------------------------------------------------------------------------------------------------------
# These lines set the basic parameters for the model
#-------------------------------------------------------------------------------------------------------------------
# Wire conductivity. Can be omitted if perfect conductivity is OK to assume
model.set_wire_conductivity(sigma = 58000000)

# Frequency in MHz
model.set_frequency(MHz = 144.2)

# Azimuth and elevation of the gain point (leave at 0,0 if you only want vswr)
model.set_gain_point(azimuth_deg = 0, elevation_deg = 0)

model.set_angular_resolution(az_step_deg = 1, el_step_deg = 1)

# Ground type. Currently limited to simple choices. If eps_r = 1, or if you omit this line,
# nec is told to use no ground. Othewise you should set the origin height so that the antenna reference
# point X,Y,Z = (0,0,0) is set to be the specified distance above ground.
# You can specify this in m, mm, cm, in, or ft (e.g. origin_height_ft = 30.33)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0) 

#-------------------------------------------------------------------------------------------------------------------
# Now we define the antenna geometry
#-------------------------------------------------------------------------------------------------------------------

# Get a 'copy' of the geometry builder class called antenna_components (again, you can change this name if desired)
antenna_components = components ()

# Define your antenna structure. Here you must use named arguments (length =, wire_diameter =)
# but the _mm can be replaced by _m, _cm, _ft, _in if you want to work in other unit systems,
# and you can mix and match if needed (length_ft = 13.5, wire_diameter_cm = 1.3)
# NOTE - although it seems like a lot of work to get to this point, you've now defined a lot of
# parameters that won't change as your antenna definition grows from the single line below
# into some complicated antenna definitions, and the idea is that that is as easy as doing this next line:
dipole = antenna_components.wire_Z(length_mm = 1040, wire_diameter_mm = 10)

# Now tell the nec interface where you're going to feed the antenna from
# This example line below says you want to feed on the geometry object called dipole,
# on the first wire in that structure, and halfway along that wire
# If you know about nec segmentation, this automatically inserts a segment
# to contain the feed, resulting in the previously 1-wire geometry object becoming a
# three wire object with all wires segmentes using the same segment length (currently hard coded to lambda / 40
# If you *don't* know about nec segmentation, one goal of this project is that you shouldn't *need* to know.
model.place_feed(dipole, feed_wire_index=0, feed_alpha_wire=0.5)

# Add the dipole (and its feed definition) to the model - in a sense this says
# "I've done defining the dipole, please add it to the model"
model.add(dipole)

#-------------------------------------------------------------------------------------------------------------------
# Time to run NEC and extract some basic parameters from the results file
#-------------------------------------------------------------------------------------------------------------------

# now write all of the above definitions into the nec input file
model.write_nec()
# now ask nec to analyse the nec input file and produce a nec output file
model.run_nec()

#-------------------------------------------------------------------------------------------------------------------
# And now a very minimal way of returning the extracted results for you to see
#-------------------------------------------------------------------------------------------------------------------

# simple printout of gains and vswr. note that get_gains_at_gain_point() also returns the
# azimuth and elevation of the gain point for confirmation and to keep the data together
gains = get_gains_at_gain_point(model)
vswr = vswr(model)

print(f"vswr:{vswr:.2f}")
print("\nFull set of info from nec output for the gain point:")
print(gains)
v_gain = gains['vert_gain_dBi']
print(f"\nExample: extract vertical gain from gains = {v_gain}")

#plot_pattern_gains(model, elevation_deg = model.el_datum_deg)
plot_pattern_gains(model, azimuth_deg = 0)

# show the geometry (if desired, you can do this immediately following model.write_nec(),
# but you'll have to close the geometry window if you want anything to happen afterwards). Also
# you don't *have* to call this at all, if you're happy that the antenna geometry is correct and you're just
# optimising parameters or doing frequency sweeps (there's no harm in putting a big loop around all of the above,
# apart from the import statements, and stepping through frequency as you wish and printing the results).
show_wires_from_file(model)



#-------------------------------------------------------------------------------------------------------------------
# That's it!
#-------------------------------------------------------------------------------------------------------------------

print(f"\n\nEnd of example {model.model_name}")

