import maya.cmds as cmds
import maya.mel as mel
import time
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtUiTools, QtCore, QtGui, QtWidgets
import sys
import os


class MayaUITemplate(QtWidgets.QWidget):
    """
    Create a default tool window.
    """
    window = None

    def __init__(self, parent=None):
        """
        Initialize class.
        """
        super(MayaUITemplate, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.base_geometry = None
        self.new_geometry = None
        
        # Remove all mesh objects in the scene
        all_meshes = cmds.ls(type='mesh')
        if all_meshes:
            for mesh in all_meshes:
                transform_node = cmds.listRelatives(mesh, parent=True)[0]
                cmds.delete(transform_node)

        # Set the widget path dynamically
        current_script_dir = os.path.dirname(os.path.realpath(__file__))
        self.widgetPath = os.path.join(current_script_dir, 'UIs')

        self.widget = QtUiTools.QUiLoader().load(os.path.join(self.widgetPath, 'FaceGenUI.ui'))
        self.widget.setParent(self)
        
        #Hard set Path if can't set dynamically
        """
        self.widgetPath = ('G:\\xiao_Desktop_Mergicians_workspace\\Tools\\Maya\\UIs\\')
        self.widget = QtUiTools.QUiLoader().load(self.widgetPath + 'FaceGenUI.ui')
        self.widget.setParent(self)
        """
        
        # set initial window size
        self.resize(400, 200)  # Set the desired width and height    
        # locate UI widgets
        self.btn_Submit = self.widget.findChild(QtWidgets.QPushButton, 'btn_Submit')
        self.btn_Browse = self.widget.findChild(QtWidgets.QPushButton, 'btn_Bro')
        self.radBtn_Cube = self.widget.findChild(QtWidgets.QRadioButton, 'radBtn_Cube')
        self.radBtn_Cylinder = self.widget.findChild(QtWidgets.QRadioButton, 'radBtn_Cylinder')
        self.spinBox_MeshW = self.widget.findChild(QtWidgets.QDoubleSpinBox, 'spinBox_MeshW')
        self.spinBox_IntrudeMax = self.widget.findChild(QtWidgets.QDoubleSpinBox, 'spinBox_IntrudeMax')
        self.lineEdit_ImagePath = self.widget.findChild(QtWidgets.QLineEdit, 'lineEdit_ImagePath')
        # assign functionality to buttons
        self.btn_Submit.clicked.connect(self.submit)
        # Connect the clicked signal of toolBtn_Browse to the browse_image method
        self.btn_Browse.clicked.connect(self.browse_image)

    def browse_image(self):
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, 'Select Image File', QtCore.QDir.homePath(), 'Image Files (*.png *.jpg *.jpeg)'
        )
        if file_path:
            self.lineEdit_ImagePath.setText(file_path)

    def submit(self):
        file_path = self.widget.lineEdit_ImagePath.text()
        if not file_path:
            cmds.confirmDialog(title='Error', message='No image selected', button='OK')
            return

        mesh_width = self.spinBox_MeshW.value()
        is_cube = self.radBtn_Cube.isChecked()

        # Create the base geometry
        if is_cube:
            self.base_geometry = cmds.polyPlane(width=mesh_width, height=mesh_width)[0]
        else:
            self.base_geometry = cmds.polyDisc(radius=mesh_width / 2.0)[0]
        
        cmds.select(self.base_geometry)
        
        # Add a delay
        #time.sleep(2)
        
        # Check if base_geometry is selected
        selected_objects = cmds.ls(selection=True)
        if self.base_geometry not in selected_objects:
            cmds.confirmDialog(title='Error', message='Base geometry not selected', button='OK')
            return
        
        # Open Texture to Geometry window
        #mel.eval('performTextureToGeom 1')
        cmds.optionVar(stringValue=('textureToGeomInputFileOV', file_path))
        # Use MEL function directly
        mel.eval('performTextureToGeom 0')  # Try to perform the action

        # Add deferred command to deparent selection and delete base_geometry
        cmds.evalDeferred(self.post_process)

    def post_process(self):
        cmds.parent(world=True)
        cmds.move(0, 1, 0, relative=True)

        # Get the selected transform
        selected_transforms = cmds.ls(selection=True, type='transform')
        if not selected_transforms:
            print('No transform is selected.')
        else:
            transform = selected_transforms[0]

        # Get the selected transform
        selected_transforms = cmds.ls(selection=True, type='transform')
        if not selected_transforms:
            print('No transform is selected.')
        else:
            transform = selected_transforms[0]
        
            # Get the shape node of the transform
            shape_node = cmds.listRelatives(transform, shapes=True, fullPath=True)
            if not shape_node:
                print('The selected transform does not have a shape node.')
            else:
                shape_node = shape_node[0]
        
                # Get all shading nodes connected to the shape node
                shading_nodes = cmds.listConnections(shape_node, type='shadingEngine')
                processed_shaders = set()  # Set to keep track of processed shading nodes
        
                if not shading_nodes:
                    print('No shading nodes found on the selected transform.')
                else:
                    for shading_node in shading_nodes:
                        # Check if the shading node has already been processed
                        if shading_node in processed_shaders:
                            continue
        
                        # Get the surface shader connected to the shading node
                        surface_shader = cmds.listConnections(shading_node + '.surfaceShader')
                        if not surface_shader:
                            print('No surface shader found for shading node:', shading_node)
                        else:
                            # Set the transparency attribute of the surface shader to (1, 1, 1)
                            cmds.setAttr(surface_shader[0] + '.transparency', 0, 0, 0, type='double3')
        
                            print('Shader:', shading_node)
        
                        # Add the shading node to the processed set
                        processed_shaders.add(shading_node)

    def resizeEvent(self, event):
        """
        Called on automatically generated resize event
        """
        self.widget.resize(self.width(), self.height())

    def closeWindow(self):
        """
        Close window.
        """
        print('closing window')
        self.destroy()


def openWindow():
    """
    ID Maya and attach tool window.
    """
    # Maya uses this so it should always return True
    if QtWidgets.QApplication.instance():
        # Id any current instances of tool and destroy
        for win in (QtWidgets.QApplication.allWindows()):
            if 'myToolWindowName' in win.objectName():  # update this name to match name below
                win.destroy()

    # QtWidgets.QApplication(sys.argv)
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)
    MayaUITemplate.window = MayaUITemplate(parent=mayaMainWindow)
    MayaUITemplate.window.setObjectName('myToolWindowName')  # code above uses this to ID any existing windows
    MayaUITemplate.window.setWindowTitle('Dice Fce Generation Tool')
    MayaUITemplate.window.show()


openWindow()