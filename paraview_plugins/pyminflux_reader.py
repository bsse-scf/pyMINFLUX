from pathlib import Path

import h5py
import pandas as pd
import paraview.vtk as vtk
import paraview.vtk.util.numpy_support as vnp
from paraview.simple import (
    CreateLayout,
    CreateView,
    FindSource,
    GetColorTransferFunction,
    GetMaterialLibrary,
    Hide,
    RenameSource,
    Render,
    ResetCamera,
    SetActiveView,
    Show,
    TrivialProducer,
    UpdatePipeline,
    _DisableFirstRenderCameraReset,
    servermanager,
)
from paraview.util.vtkAlgorithm import (
    VTKPythonAlgorithmBase,
    smdomain,
    smhint,
    smproperty,
    smproxy,
)
from paraview.vtk.numpy_interface import dataset_adapter as dsa
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkMultiBlockDataSet, vtkUnstructuredGrid


@smproxy.reader(
    name="pyMINFLUXReader",
    label="pyMINFLUX reader",
    file_description="pyMINFLUX files",
    extensions="pmx",
)
class pyMINFLUXReader(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(
            self, nInputPorts=0, nOutputPorts=1, outputType="vtkMultiBlockDataSet"
        )
        self._filename = ""
        self._x_column = "x"
        self._y_column = "y"
        self._z_column = "z"

    @smproperty.stringvector(name="FileName", panel_visibility="never")
    @smdomain.filelist()
    @smhint.filechooser(extensions="pmx", file_description="pyMINFLUX files")
    def SetFileName(self, name):
        """Specify filename for the file to read."""
        if self._filename != name:
            self._filename = name
            self.Modified()

    def RequestData(self, request, inInfo, outInfo):

        # Disable automatic camera reset on Show()
        _DisableFirstRenderCameraReset()

        # Create a new "pyMINFLUX" layout
        layout, render_view = self.create_new_layout()

        # Read the file
        data = self.load_data_to_grid(self._filename)

        # Wrap the data in a ParaView object to set its rendering options
        points = TrivialProducer()
        points.GetClientSideObject().SetOutput(data)

        # Rename the TrivialProducer
        RenameSource("Localizations", proxy=points)

        # Show the points in the render view
        point_display = Show(points, render_view)
        Render(render_view)

        # Set the display properties of the render view
        self.set_render_view_display_properties(point_display, points)

        # Update the pipeline
        UpdatePipeline(proxy=point_display)

        # Focus on the render view
        SetActiveView(render_view)

        # Reset the camera
        ResetCamera()

        # Output the poly data to the pipeline
        output = vtkMultiBlockDataSet.GetData(outInfo, 0)
        output.SetBlock(0, data)

        # Hide the rendering of the reader itself
        source = FindSource(Path(self._filename).name)
        Hide(source)

        # Return success
        return 1

    def load_data_to_grid(self, filename):
        """Read the file and convert it to a vtkUnstructuredGrid."""

        # Read the data frame
        df = self.read_dataframe_from_pmx(filename)

        # Create a new object
        points = vtkPoints()
        points.SetData(vnp.numpy_to_vtk(df[["x", "y", "z"]].values))
        mfx_data = vtkUnstructuredGrid()
        ugrid = dsa.WrapDataObject(mfx_data)
        ugrid.Points = points
        p = points.GetNumberOfPoints()
        ugrid.AllocateExact(p, p)

        for j in range(p):
            ids = vtk.vtkIdList()
            ids.SetNumberOfIds(1)
            ids.SetId(0, j)
            ugrid.InsertNextCell(vtk.VTK_VERTEX, ids)

        # Add additional columns as attributes
        for col in df.columns:
            if col in ["x", "y"]:  # We keep z for depth-coloring
                continue
            vtk_array = vnp.numpy_to_vtk(df[col].values)
            vtk_array.SetName(col)  # Sets the name of the attribute
            mfx_data.GetPointData().AddArray(vtk_array)

        return mfx_data

    def read_dataframe_from_pmx(self, filename):
        """Read the Pandas DataFrame from the `.pmx` file."""
        with h5py.File(filename, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]

            if file_version != "1.0":
                self._message = "Incompatible file version."
                return None

            # Read dataset
            dataset = f["/paraview/dataframe"]

            # Read the NumPy data
            data_array = dataset[:]

            # Read column names
            column_names = dataset.attrs["column_names"]

            # Read column data types
            column_types = dataset.attrs["column_types"]

            # Read the index
            index_data = f["/paraview/dataframe_index"][:]

            # Create DataFrame with specified columns
            df = pd.DataFrame(data_array, index=index_data, columns=column_names)

            # Apply column data types
            for col, dtype in zip(column_names, column_types):
                df[col] = df[col].astype(dtype)

        return df

    def create_new_layout(self):
        """Create a new layout with a render and a spreadsheet views."""

        # Create a new layout
        layout = CreateLayout("pyMINFLUX")

        # Create a render view
        render_view = CreateView("RenderView", "Localizations")
        render_view.AxesGrid = "GridAxes3DActor"
        render_view.Background = [0.0, 0.0, 0.0]
        render_view.UseColorPaletteForBackground = 0
        render_view.OSPRayMaterialLibrary = GetMaterialLibrary()

        # Assign the view to the new layout
        layout.AssignView(0, render_view)

        # Return the created objects
        return layout, render_view

    def set_render_view_display_properties(self, display, table_to_points):
        """Sets the display properties of passed view."""

        # Change the representation to "Point Gaussian"
        display.Representation = "Point Gaussian"

        # Change the Gaussian radius
        display.GaussianRadius = 3.0

        # Set the opacity
        display.Opacity = 0.4

        # Finally set the shader present
        display.ShaderPreset = "Plain circle"

        # Set the Coloring based on a specific attribute
        # Replace 'attribute_name' with the name of the attribute you want to use
        attribute_name = "tid"
        display.ColorArrayName = ("POINTS", attribute_name)

        # Create the lookup table
        lookup_table = GetColorTransferFunction(attribute_name)

        # Fetch the VTK dataset from the source
        vtk_data = servermanager.Fetch(table_to_points)

        # Get the range of the selected attribute
        data_range = vtk_data.GetPointData().GetArray(attribute_name).GetRange()

        # Rescale the lookup table to match the data range
        lookup_table.RescaleTransferFunction(data_range[0], data_range[1])

        # Assign the lookup table to the display properties
        display.LookupTable = lookup_table
