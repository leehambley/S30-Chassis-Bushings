import os, re
import FreeCAD, Mesh, MeshPart

# Use the current directory (relative to the script)
directory = os.path.abspath(".")

# Regex pattern to skip bodies named "pin", "bolt", or starting with "washer"
skip_pattern = re.compile(r'^(pin|bolt|washer.*)$', re.IGNORECASE)

# Iterate through all FCStd files in the current directory
for fname in os.listdir(directory):
    if fname.endswith('.FCStd'):
        fpath = os.path.join(directory, fname)
        print("\nProcessing file:", fname)
        doc = FreeCAD.openDocument(fpath)
        bodies_to_export = []
        
        # Collect PartDesign bodies (filter out those matching the skip pattern)
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
            # Create a mesh for each body
            for body in bodies_to_export:
                shape = body.Shape
                print(f"\nCreating mesh for body: {body.Label}")
                try:
                    m = MeshPart.meshFromShape(Shape=shape, 
                                               LinearDeflection=0.1, 
                                               AngularDeflection=0.523599)
                    if m and len(m.Facets) > 0:
                        valid_meshes.append(m)
                        print(f"Mesh created for {body.Label} with {len(m.Facets)} facets")
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
                    print(f"\nMerged {len(valid_meshes)} meshes into one with {len(merged.Facets)} facets")
                else:
                    mesh_to_export = valid_meshes[0]
                
                # Create a temporary document and add a Mesh::Feature object
                tempDoc = FreeCAD.newDocument("TempMeshDoc")
                mesh_obj = tempDoc.addObject("Mesh::Feature", "Mesh")
                mesh_obj.Mesh = mesh_to_export
                tempDoc.recompute()
                
                # Export the Mesh::Feature object
                out_name = os.path.splitext(fname)[0] + ".stl"  # Change extension to .3mf if supported
                out_path = os.path.join(directory, out_name)
                try:
                    Mesh.export([mesh_obj], out_path)
                    print("\nExported to", out_path)
                except Exception as e:
                    print("\nError exporting mesh:", e)
                    
                # Clean up the temporary document
                FreeCAD.closeDocument(tempDoc.Name)
            else:
                print("\nNo valid meshes to export in document", fname)
        else:
            print("\nNo bodies to export in document", fname)
        
        FreeCAD.closeDocument(doc.Name)
