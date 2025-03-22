import os, re
import FreeCAD, Mesh, MeshPart

# Use current directory
directory = os.path.abspath("./FreeCAD/")
out_dir = os.path.abspath("./STL/")

# Skip bodies named starting with "pin", "bolt", or "washer"
skip_pattern = re.compile(r'^(pin.*|bolt.*|washer.*)$', re.IGNORECASE)

# Lower values yields smoother stls at the expense of processing time
LINEAR_DEFLECTION=0.01
ANGULAR_DEFLECTION=0.05

for fname in os.listdir(directory):
    if fname.endswith('.FCStd'):
        fpath = os.path.join(directory, fname)
        print("\nProcessing file:", fname)
        doc = FreeCAD.openDocument(fpath)
        bodies_to_export = []
        
        for obj in doc.Objects:
            if obj.TypeId == "PartDesign::Body":
                if skip_pattern.match(obj.Label):
                    print("Skipping body:", obj.Label)
                else:
                    print("Adding body:", obj.Label)
                    bodies_to_export.append(obj)
            else:
                print("Ignoring non-body object:", obj.Name, "of type", obj.TypeId)
        
        if bodies_to_export:
            valid_meshes = []
            for body in bodies_to_export:
                shape = body.Shape
                try:
                    m = MeshPart.meshFromShape(Shape=shape, 
                                               LinearDeflection=LINEAR_DEFLECTION, 
                                               AngularDeflection=ANGULAR_DEFLECTION)
                    
                    if m and len(m.Facets) > 0:
                        valid_meshes.append(m)
                        print("Mesh created for", body.Label, "with", len(m.Facets), "facets")
                    else:
                        print("Empty mesh for", body.Label)
                except Exception as e:
                    print("Error meshing", body.Label, ":", e)
            if valid_meshes:
                # Merge meshes if more than one exists
                if len(valid_meshes) > 1:
                    merged = Mesh.Mesh()
                    for m in valid_meshes:
                        merged.addMesh(m)
                    mesh_to_export = merged
                    print("Merged", len(valid_meshes), "meshes into one with", len(merged.Facets), "facets")
                else:
                    mesh_to_export = valid_meshes[0]
                out_name = os.path.splitext(fname)[0] + ".stl"
                out_path = os.path.join(out_dir, out_name)
                try:
                    Mesh.export([mesh_to_export], out_path)
                    print("Exported to", out_path)
                except Exception as e:
                    print("Error exporting mesh:", e)
            else:
                print("No valid meshes to export")
        else:
            print("No bodies to export")
        FreeCAD.closeDocument(doc.Name)
