import pandas as pd
from paraview.simple import (
    FindSource,
    GetActiveViewOrCreate,
    GetColorTransferFunction,
    Hide,
    Render,
    ResetCamera,
    Show,
    TableToPoints,
    TrivialProducer,
    UpdatePipeline,
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

    @smproperty.stringvector(name="FileName", panel_visibility="never")
    @smdomain.filelist()
    @smhint.filechooser(extensions="pmx", file_description="pyMINFLUX files")
    def SetFileName(self, name):
        """Specify filename for the file to read."""
        if self._filename != name:
            self._filename = name
            self.Modified()

    def RequestData(self, request, inInfo, outInfo):

        # Read the file into a table compatible with TableToPoints
        table = self.file_to_table(self._filename)

        # Convert the table to points
        table_to_points = TableToPoints(Input=table)
        table_to_points.XColumn = self._x_column
        table_to_points.YColumn = self._y_column
        table_to_points.ZColumn = self._z_column

        # Get the active render view
        render_view = GetActiveViewOrCreate("RenderView")

        # Show the points in the render view
        point_display = Show(table_to_points, render_view)

        # Change the representation to 'Points'
        point_display.Representation = "Points"

        # Change the point size
        point_display.PointSize = 5.0

        # Render points as spheres
        point_display.RenderPointsAsSpheres = 1

        # Set the Coloring based on a specific attribute
        # Replace 'attribute_name' with the name of the attribute you want to use
        attribute_name = "tid"
        point_display.ColorArrayName = ("POINTS", attribute_name)

        # Create the lookup table
        lookup_table = GetColorTransferFunction(attribute_name)

        # Fetch the VTK dataset from the source
        vtk_data = servermanager.Fetch(table_to_points)

        # Get the range of the selected attribute
        data_range = vtk_data.GetPointData().GetArray(attribute_name).GetRange()

        # Rescale the lookup table to match the data range
        lookup_table.RescaleTransferFunction(data_range[0], data_range[1])

        # Assign the lookup table to the display properties
        point_display.LookupTable = lookup_table

        # Update the pipeline
        UpdatePipeline(proxy=point_display)

        # Render the view
        Render(render_view)

        # Reset the camera
        ResetCamera()

        # Output the poly data to the pipeline
        output = vtkPolyData.GetData(outInfo)
        output.ShallowCopy(table_to_points.GetClientSideObject().GetOutputDataObject(0))

        return 1

    def file_to_table(self, filename):
        """Read the file and convert it to a vtkTable."""

        # Read the data frame
        df = pd.read_csv(filename)

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
