import numpy as np
import os

# Room dimensions (in meters)
room_length = 5.0  # Length of the room (X-axis)
room_width = 4.0   # Width of the room (Y-axis)
room_height = 3.0  # Height of the room (Z-axis)

# Define room corners (vertices)
vertices = [
    [0, 0, 0],  # Corner 1 (floor corner)
    [room_length, 0, 0],  # Corner 2 (floor corner)
    [room_length, room_width, 0],  # Corner 3 (floor corner)
    [0, room_width, 0],  # Corner 4 (floor corner)
    [0, 0, room_height],  # Corner 5 (ceiling corner)
    [room_length, 0, room_height],  # Corner 6 (ceiling corner)
    [room_length, room_width, room_height],  # Corner 7 (ceiling corner)
    [0, room_width, room_height]  # Corner 8 (ceiling corner)
]

# Faces of the room (each face is defined by 3 or more vertices)
faces = [
    [0, 1, 2, 3],  # Floor (base)
    [4, 5, 6, 7],  # Ceiling
    [0, 1, 5, 4],  # Wall 1 (X direction)
    [1, 2, 6, 5],  # Wall 2 (Y direction)
    [2, 3, 7, 6],  # Wall 3 (X direction)
    [3, 0, 4, 7]   # Wall 4 (Y direction)
]

# Path to save the file
home = os.path.expanduser("~")
out = os.path.join(home, "Desktop", "simple_room.ply")

# Write the PLY file
with open(out, "w", encoding="utf-8") as f:
    # Write PLY header
    f.write("ply\n")
    f.write("format ascii 1.0\n")
    f.write(f"element vertex {len(vertices)}\n")
    f.write("property float x\nproperty float y\nproperty float z\n")
    f.write(f"element face {len(faces)}\n")
    f.write("property list uchar int vertex_indices\n")
    f.write("end_header\n")

    # Write vertices (coordinates)
    for vertex in vertices:
        f.write(f"{vertex[0]} {vertex[1]} {vertex[2]}\n")

    # Write faces (indices of the vertices forming each face)
    for face in faces:
        f.write(f"{len(face)} {' '.join(map(str, face))}\n")

print(f"✅ Simple room PLY file saved at: {out}")
