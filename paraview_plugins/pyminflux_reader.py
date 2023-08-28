from pathlib import Path

import h5py
import pandas as pd
from paraview.simple import (
    CreateLayout,
    CreateView,
    Delete,
    FindSource,
    GetActiveViewOrCreate,
    GetColorTransferFunction,
    GetLayouts,
    GetMaterialLibrary,
    GetOpacityTransferFunction,
    Hide,
    RemoveLayout,
    RenameSource,
    Render,
    ResetCamera,
    SetActiveView,
    Show,
    TableToPoints,
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
from vtkmodules.vtkCommonCore import vtkFloatArray, vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkTable


@smproxy.reader(
    name="pyMINFLUXReader",
    label="pyMINFLUX reader",
    file_description="pyMINFLUX files",
    extensions="pmx",
)
class pyMINFLUXReader(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(
            self, nInputPorts=0, nOutputPorts=1, outputType="vtkPolyData"
        )
        self._filename = ""
        self._x_column = "x"
        self._y_column = "y"
        self._z_column = "z"
        self._message = ""

    @smproperty.stringvector(name="FileName", panel_visibility="never")
    @smdomain.filelist()
    @smhint.filechooser(extensions="pmx", file_description="pyMINFLUX files")
    def SetFileName(self, name):
        """Specify filename for the file to read."""
        if self._filename != name:
            self._filename = name
            self.Modified()

    def RequestData(self, request, inInfo, outInfo):

        # Create a new "pyMINFLUX" layout
        layout, render_view = self.create_new_layout()

        # Read the file into a table compatible with TableToPoints
        table = self.file_to_table(self._filename)
        if table is None:
            # Inform ParaView that opening the file failed.
            raise RuntimeError(
                f"Could not open {self._filename}: error was {self._message}"
            )

        # Rename the table object
        RenameSource("Dataframe", proxy=table)

        # Convert the table to points
        table_to_points = TableToPoints(Input=table)
        table_to_points.XColumn = self._x_column
        table_to_points.YColumn = self._y_column
        table_to_points.ZColumn = self._z_column

        # Rename the points object
        RenameSource("Localizations", proxy=table_to_points)

        # Show the points in the render view
        point_display = Show(table_to_points, render_view)
        Render(render_view)

        # Set the display properties of the render view
        self.set_render_view_display_properties(point_display, table_to_points)

        # Update the pipeline
        UpdatePipeline(proxy=point_display)

        # Focus on the render view
        SetActiveView(render_view)

        # Reset the camera
        ResetCamera()

        # Output the poly data to the pipeline
        output = vtkPolyData.GetData(outInfo)
        output.ShallowCopy(table_to_points.GetClientSideObject().GetOutputDataObject(0))

        # Hide the rendering of the reader itself
        source = FindSource(Path(self._filename).name)
        Hide(source)

        # Return success
        return 1

    def file_to_table(self, filename):
        """Read the file and convert it to a vtkTable."""

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

        # Create a new column loc_z (that can be used for coloring)
        df["loc z"] = df["z"]

        # Populate the vtkTable
        table = vtkTable()

        for column_name in df.columns:
            array = vtkFloatArray()
            array.SetName(column_name)
            array.SetNumberOfComponents(1)
            array.SetNumberOfTuples(len(df))

            for i, value in enumerate(df[column_name]):
                array.SetValue(i, float(value))

            table.AddColumn(array)

        # Now wrap it to be compatible with TableToPoints()
        producer = TrivialProducer()
        producer.GetClientSideObject().SetOutput(table)

        return producer

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
