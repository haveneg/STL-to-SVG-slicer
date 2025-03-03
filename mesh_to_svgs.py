import numpy as np
from stl import mesh
import svgwrite
from svgwrite import cm, mm
import sys

def line_plane_intersection(v, b, n, p):
    return (np.dot(n, p - b) / np.dot(n, v)) * v + b # maintain the same dimensions, 3

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

def create_svg(slice_faces, z_level, filename="output.svg"):
    dwg = svgwrite.Drawing(filename, profile='tiny')
    b_lines = dwg.add(dwg.g(id="border", debug=True))
    for face in slice_faces:
        # Complex way to solve to contract 3D faces to 2D plane: solve for intersection of scan plane and the two edges of each plane that pass through it
        # Each intersecting edge of each plane is defined by two of its points

        # Initialize array of eventually 2 points to draw between on the svg:
        trace_pts = []
        
        for i in range(3): # loops through each pair of points, (p1, p2), (p2, p3), (p3, p1)
            p1, p2 = face[i], face[(i+1) % 3]

            # Checks if the two points are on opposite sides of the scan plane before finding their intersection with the plane
            if np.sign(p1[2] - z_level) != np.sign(p2[2] - z_level):
                v = p1 - p2 
                b = p2 
                n = [0, 0, 1] # normal vector of scan plane 
                p = [0, 0, z_level] 
                intersect = line_plane_intersection(v, b, n, p)
                if intersect[2] != z_level:
                    raise ValueError(f"The apparent intersection point {intersect} does not contain {z_level} as its z value")
                trace_pts.append(intersect[0:2])
        if trace_pts:
            b_lines.add(dwg.line(start= trace_pts[0] * mm, end= trace_pts[1] * mm, stroke=svgwrite.rgb(0, 0, 0, '%'), stroke_width=0.25 * mm))
    dwg.save()

def main(stl_filename, z_interval, output_dir):
    model = mesh.Mesh.from_file(stl_filename)
    z_min, z_max = np.min(model.vectors[:, :, 2]), np.max(model.vectors[:, :, 2])
    
    # Iterate over the Z-range in steps of z_interval
    for z_level in np.arange(z_min, z_max, z_interval):
        slice_faces = slice_stl(model, z_level)
        if slice_faces:
            create_svg(slice_faces, z_level, filename=f"{output_dir}/slice_{z_level:.2f}.svg")

if __name__ == "__main__":
    # if len(sys.argv) < 4:
    #     raise ValueError("Not enough arguments. Requires stl_filename, height_interval, output_directory")
    # stl_filename = sys.argv[1]
    # z_interval = float(sys.argv[2])  # Height of each slice in Z-direction
    # output_dir = sys.argv[3]
    main("portland_temple_resized.stl", 5, "./slices")
