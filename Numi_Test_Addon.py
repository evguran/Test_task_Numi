# Hello

bl_info = {
    "name": "Addon Numi test",
    "description": "Test scripts from Numi",
    "author": "Evgeny Kuzmin",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "location": "View 3D > My Addon Tab",
    "doc_url": "https://docs.google.com/document/d/1EH3hfptDFxUvL4XHqw_9vA7dsg2ag9qzVg8k5viNgGE/edit?usp=sharing",
    "tracker_url": "https://github.com/evguran/Test_task_Numi",
    "support": "COMMUNITY",
    "category": "3D View",
    }

import sys
import os
import bpy


class OBJECT_OT_Test1_Tree(bpy.types.Operator):
    bl_idname = "object.test1_tree"
    bl_label = "Numi Test #1 Script"
    def execute(self, context):
        
        blend_dir = os.path.dirname(bpy.data.filepath)
        if blend_dir not in sys.path:
           sys.path.append(blend_dir)

        import Test1_Tree
        import importlib
        importlib.reload(Test1_Tree)
        
        Test1_Tree.main()
        return {'FINISHED'}


class MyAddonPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "My Addon Panel"
    bl_idname = "OBJECT_PT_addon"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "My Addon"
#    bl_context = "object"
    

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.test1_tree")


# Register
def register():
    bpy.utils.register_class(OBJECT_OT_Test1_Tree)
    bpy.utils.register_class(MyAddonPanel)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_Test1_Tree)
    bpy.utils.unregister_class(MyAddonPanel)


if __name__ == "__main__":
    register()
