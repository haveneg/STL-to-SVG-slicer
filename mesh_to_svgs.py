import numpy as np
from stl import mesh
import svgwrite
from svgwrite import cm, mm
import sys

def slice_stl(model, z_level):
    # Extract faces where z-coordinate is close to z_level
    z_faces = []
    for i, v in enumerate(model.vectors):
        # Check if the face is crossing the z_level plane
        z_min = min(v[:, 2])
        z_max = max(v[:, 2])
        if z_min <= z_level <= z_max:
            z_faces.append(v)
    return z_faces

def create_svg(slice_faces, filename="output.svg"):
    dwg = svgwrite.Drawing(filename, profile='tiny')
    b_lines = dwg.add(dwg.g(id="border", debug=True))
    for face in slice_faces:
        # Simple way to project the 3D face to 2D (ignoring the Z-coordinate)
        
        for i in range(3):
            p1, p2 = face[i], face[(i+1) % 3]
            b_lines.add(dwg.line(start=(p1[0].astype(float) * mm, p1[1].astype(float)) * mm, end=(p2[0].astype(float) * mm, p2[1].astype(float)) * mm, stroke=svgwrite.rgb(0, 0, 0, '%'), stroke_width=0.25 * mm))
    dwg.save()

def main(stl_filename, z_interval, output_dir):
    model = mesh.Mesh.from_file(stl_filename)
    z_min, z_max = np.min(model.vectors[:, :, 2]), np.max(model.vectors[:, :, 2])
    
    # Iterate over the Z-range in steps of z_interval
    for z_level in np.arange(z_min, z_max, z_interval):
        slice_faces = slice_stl(model, z_level)
        if slice_faces:
            create_svg(slice_faces, filename=f"{output_dir}/slice_{z_level:.2f}.svg")

if __name__ == "__main__":
    # if len(sys.argv) < 4:
    #     raise ValueError("Not enough arguments. Requires stl_filename, height_interval, output_directory")
    # stl_filename = sys.argv[1]
    # z_interval = float(sys.argv[2])  # Height of each slice in Z-direction
    # output_dir = sys.argv[3]
    main("portland_temple_resized.stl", 5, "./slices")
