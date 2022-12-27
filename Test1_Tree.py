import bpy, bmesh
from mathutils.bvhtree import BVHTree
import mathutils
import time
import random

class The_Branch:
    # Stores a branch data
    def __init__(self, bm, root_num, id, root_loop):
        self.verts = [ v.index for v in bm.verts if v.select ]
        self.faces = [ f.index for f in bm.faces if f.select ]
        self.root_num = root_num
        self.id = id
        self.root_loop = root_loop
    def __str__(self):
        return "I am a branch"
            

def deselect_all(bm):
    # Deselect all
    for i in bm.faces:
        i.select = False
    for i in bm.edges:
        i.select = False
    for i in bm.verts:
        i.select = False


def is_inside(bvhtree, bvh_co):
    # Checks if a given point is inside of the mesh
    loc, norm, _, dist = bvhtree.find_nearest(bvh_co, 100.0)
    dir = loc - bvh_co
    dot = dir.dot(norm)
    if dot > 0:
        return True
    else:
        print("Not inside, check:")
        print(f"dot {dot}, dist {dist}")
        print(f"bpy.ops.mesh.primitive_uv_sphere_add(location=({bvh_co.x}, {bvh_co.y}, {bvh_co.z}), radius=0.05)")
        print(f"bpy.ops.mesh.primitive_uv_sphere_add(location=({loc.x}, {loc.y}, {loc.z}), radius=0.1)")
        return False


def rec(root_loop, bm, e_list_groups, root_num, branch_list):
    # ======================================================================
    # Searching for a branch cylinder faces
    for idx in root_loop:
        bm.edges[idx].select = True
    print("Root_loop", root_loop)
    print("Total edges selected", bpy.context.object.data.total_edge_sel)
    # ======================================================================
    # Selecting adjacent till no increment to selected edges number
    edge_sel_num = bpy.context.object.data.total_edge_sel
    while True:
        bpy.ops.mesh.select_more()
        edge_sel_num_curr = bpy.context.object.data.total_edge_sel
        if edge_sel_num != edge_sel_num_curr:
            edge_sel_num = edge_sel_num_curr
        else:
            break
    print("Total faces selected", bpy.context.object.data.total_face_sel)
    # ======================================================================
    # Adding the found items to the object
    branch = The_Branch(bm, root_num, len(branch_list)+1, root_loop)
    branch_list.append(branch)
    
    # ======================================================================
    # Removing the second loop of the branch
    for e_loop in e_list_groups:
        # It is enough to ensure that one edge in the loop is selected
        idx = e_loop[0]
        if bm.edges[idx].select:
            e_list_groups.remove(e_loop)
            # print(e_loop)
            break
    # print(e_list_groups)
    # ======================================================================
    # Initialization of BVH tree
    mw = bpy.context.object.matrix_world      # Active object's world matrix
    vertices_glob = [ mw @ v.co for v in bm.verts ] # Global coordinates

    # bvh_list_verts = [ (v.co.x, v.co.y, v.co.z) for v in bm.verts ]
    bvh_list_verts = [ (co.x, co.y, co.z) for co in vertices_glob  ]
    bvh_list_faces = [ tuple([v.index for v in f.verts]) for f in bm.faces if f.select ]
    bvhtree = BVHTree.FromPolygons(bvh_list_verts, bvh_list_faces, all_triangles=False, epsilon=0.0)
    
    deselect_all(bm)
    
    # test if inside
    # if a vector from a vertex to the closest face and a normal are in the same direction, 
    # the vertex is inside of the volume. For simplicity, the only vertex from the loop is 
    # checked.
    print("------------------------------------")
    print("Root number is {:}".format(root_num))
    root_num += 1
    print("e_list_groups length is {:}".format(len(e_list_groups)))
#    print(bvhtree)
    for e_loop in list(e_list_groups): # !!!
        idx = e_loop[0]
        # print(idx)
        bvh_co = mw @ bm.edges[idx].verts[0].co
#        print(bvh_co)
        if is_inside(bvhtree, bvh_co):
            e_list_groups.remove(e_loop)
#            print("e_list_groups length is {:}".format(len(e_list_groups)))
            if e_list_groups:
                rec(e_loop, bm, e_list_groups, root_num, branch_list)
                print("After return length is {:}".format(len(e_list_groups)))
            else:
                print("Groups is empty")
        else:
            print(f"BVHTree - {bvhtree}")
            print("--------------------")
    return 0
            

# ==========================================================================

def main():
    # ======================================================================
    # Initiation
    print()
    print("================== SCRIPT STARTED ===================")
    bpy.ops.object.mode_set(mode='EDIT')
    # bpy.ops.object.editmode_toggle()
    obj = bpy.context.edit_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    
    # This is to make sure tables are up to date
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    
    # Deselect if something selected
    deselect_all(bm)
    
    # ======================================================================
    # Searching for boundary edges and it vertices
    e_list = [];
    for e in bm.edges:
        if e.is_boundary:
            e_list.append(e.index)
            
    # ======================================================================
    # Searching for loops
    e_list_groups = []
    while e_list:
        e_loop = []
        idx = e_list[0]
        bm.edges[idx].select = True
        bpy.ops.mesh.loop_multi_select(ring=False)
        for idx in e_list:
            e = bm.edges[idx]
            if e.select:
                e_loop.append(idx)
                e.select = False
        for idx in e_loop:
            e_list.remove(idx)
        e_list_groups.append(e_loop)
    # print(len(e_list_groups))
    # print("ok")
    
    for e_loop in e_list_groups:
        for idx in e_loop:
            bm.edges[idx].select = True
    
    # ======================================================================
    # Searching the root vertex
    vertices = bm.verts
    mw = bpy.context.object.matrix_world      # Active object's world matrix

    vertices_glob = [ mw @ v.co for v in vertices ] # Global coordinates

    # Find the lowest Z value amongst the object's verts
    minZ = min( [ co.z for co in vertices_glob ] ) 

    # Select all the vertices that are on the lowest Z
    for v in vertices:
        if (mw @ v.co).z == minZ: 
            minZVertex = v.index
            break

    # ======================================================================
    # Searching for a root loop
    for e_loop in e_list_groups:
        for idx in e_loop:
            if bm.edges[idx].verts[0].index == minZVertex:
                root_loop = e_loop
                e_list_groups.remove(e_loop)
                break
    
    # ======================================================================
    # Run a recursive function
    branch_list = []
    deselect_all(bm)
    rec(root_loop, bm, e_list_groups, root_num=0, branch_list=branch_list)
    
    # ======================================================================
    # release bmesh object and go to object mode, then get an object
    bm.free()
    bpy.ops.object.mode_set(mode='OBJECT')
    obj = bpy.context.object
    
    # ======================================================================
    # Coloring vertices
    branch_num = 0
    for branch in branch_list:
        if branch_num < branch.root_num:
            branch_num = branch.root_num
    
    for i in range(branch_num + 1):
        print(i)
        verts_ids = []
#        r, g, b = random.randint(0,255),random.randint(0,255),random.randint(0,255)
        
        colattr = obj.data.color_attributes.get(str(i))
        if colattr is None:
            colattr = obj.data.color_attributes.new(
                name=str(i),
                type='FLOAT_COLOR',
                domain='POINT',
            )
        
        for branch in branch_list:
            if i == branch.root_num:
                verts_ids.extend(branch.verts)
        # print(verts_ids)
        for v_index in range(len(obj.data.vertices)):
            if v_index in verts_ids:
#                colattr.data[v_index].color = [r / 255, g / 255, b / 255, 1]
                colattr.data[v_index].color = [255. / 255, 165. / 255, 0. / 255, 1]
            else:
                colattr.data[v_index].color = [1, 1, 1, 1]
    
    # ======================================================================
    # Report status
    for branch in branch_list:
        id = branch.id
        root_num = branch.root_num
        verts_ids = branch.verts
        faces_ids = branch.faces
        
        print
        print(f"id = {id}")
        print(f"root_num = {root_num}")
        print(f"Number of vertices: {len(verts_ids)}")
        print(f"Number of polygons: {len(faces_ids)}")
        print

    print("done")

if __name__ == "__main__":
    main()

