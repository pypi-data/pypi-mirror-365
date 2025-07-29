
from necbol import *

def build_hentenna_yagi(model, h_m, w_m, fp_m, refl_sep_m, refl_scale, wd_mm):

    antenna_components = components()
    
    feed_rod = antenna_components.wire_Z(length_m = w_m,
                                           wire_diameter_mm = wd_mm)
    feed_rod.rotate_ZtoX()
    feed_rod.translate(dx_m = 0, dy_m = 0, dz_m = fp_m)
    
    hentenna_outer_loop = antenna_components.rect_loop_XZ(length_m = h_m,
                                   width_m = w_m,
                                   wire_diameter_mm = wd_mm)
    hentenna_outer_loop.translate(dx_m = 0, dy_m = 0, dz_m = h_m/2)


    reflector_loop = antenna_components.rect_loop_XZ(length_m = refl_scale*(h_m-fp_m),
                                   width_m = refl_scale*w_m,
                                   wire_diameter_mm = wd_mm)
    
    feed_rod.connect_ends(hentenna_outer_loop)
    reflector_loop.translate(dx_m = 0, dy_m = -refl_sep_m, dz_m = h_m/2 + fp_m/2)
    
    support_rod = antenna_components.connector(from_object = hentenna_outer_loop, from_wire_index=3, from_alpha_wire=0.5,
                                               to_object = reflector_loop, to_wire_index=3, to_alpha_wire=0.5)
    support_rod.connect_ends(hentenna_outer_loop)
    support_rod.connect_ends(reflector_loop)

    model.place_feed(feed_rod, feed_wire_index=0, feed_alpha_wire=0.5)
    
    model.add(feed_rod)
    model.add(reflector_loop)
    model.add(hentenna_outer_loop)
    model.add(support_rod)

    return model

model = NECModel(working_dir="nec_wkg",
                 model_name = "Hentenna with reflector rectangle and nearby metal sheet",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe")

model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth_deg = 90, elevation_deg = 5)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)
#model.set_ground(eps_r = 1, sigma = 0.0, origin_height_m = 0.0)

hen_height_m = 0.97
hen_width_m = 0.271
feed_height_m = 0.12
refl_scale = 0.985
refl_sep = 0.33
model = build_hentenna_yagi(model, hen_height_m, hen_width_m, feed_height_m, refl_sep, refl_scale, 5)
model.write_nec()
model.run_nec()
gains = get_gains_at_gain_point(model)
vswr = vswr(model)
print(f"{gains}, vswr:{vswr:.2f}")

show_wires_from_file(model)

print(f"\n\nEnd of example {model.model_name}")


