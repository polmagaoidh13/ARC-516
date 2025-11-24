import io
import numpy as np
import open3d as o3d
import laspy

def load_point_cloud(fobj: io.BytesIO, filename: str) -> np.ndarray:
    name = filename.lower()
    if name.endswith(".ply") or name.endswith(".pcd"):
        fobj.seek(0)
        with open("/tmp/_scan.bin", "wb") as tmp:
            tmp.write(fobj.read())
        pcd = o3d.io.read_point_cloud("/tmp/_scan.bin")
        pts = np.asarray(pcd.points, dtype=float)
        return pts
    if name.endswith(".las") or name.endswith(".laz"):
        fobj.seek(0)
        with open("/tmp/_scan.las", "wb") as tmp:
            tmp.write(fobj.read())
        with laspy.open("/tmp/_scan.las") as reader:
            arr = np.vstack([reader.x, reader.y, reader.z]).T.astype(float)
        return arr
    raise ValueError("Unsupported file type. Use PLY or LAS")
