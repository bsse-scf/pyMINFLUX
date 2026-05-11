# UI Workflows

pyMINFLUX has a shared UI shell and workflow-specific panels/actions. The shell owns loading, plotting, the DataViewer, common file actions, and generic menu wiring. A workflow owns domain-specific state, tools, and the dataframe adapter used by shared plotting.

## Core Contract

Implement a subclass of `pyminflux.ui.workflows.BaseWorkflow`.

Required:

- `name`: short workflow identifier.
- `create_panel(parent=None) -> QWidget`: build the left-panel workflow UI.
- `plot_dataframe() -> pd.DataFrame | None`: return the dataframe consumed by the shared plotter and DataViewer.

Usually override:

- `set_dataset(dataset)`: initialize workflow-native data structures.
- `color_columns(dataframe) -> list[str]`: return allowed dataframe columns for point coloring.
- `workflow_action_names() -> list[str]`: expose workflow-specific main-window actions.
- `stats_dataframe()`: provide exportable workflow statistics.
- `export_data_to_csv(file_name)`: customize data export.
- `select_by_index_labels(labels)` / `select_by_2d_range(...)`: customize plot selection behavior.

## Data Boundary

`plot_dataframe()` is the main adapter boundary. Shared UI code should not assume a `MinFluxProcessor`.

The dataframe should contain:

- numeric columns for X/Y plot axes
- optional `x`, `y`, `z` columns for spatial plotting
- optional `tid` column if track lines should connect points
- any workflow-specific columns needed for coloring, selection, DataViewer display, or export

For a real tracking workflow, keep the native track model internal and expose only a plotting/data-view adapter dataframe.

## Coloring

Coloring is column-based.

`color_columns(dataframe)` returns the columns that may appear in the color dropdown. The plotter then colors by the selected column from `plot_dataframe()`.

- integer or non-numeric columns use discrete colors
- float-like numeric columns use a continuous colormap and colorbar
- workflows decide which columns are valid; tracking should not inherit localization assumptions

Example:

```python
def color_columns(self, dataframe):
    return ["length"] if dataframe is not None and "length" in dataframe else []
```

## Workflow Panel

The workflow panel is only the workflow-specific body of the left dock. `Load` and `Load Zarr` are shared shell controls.

Panel buttons can mutate workflow state directly through signals. If the mutation changes plotted data, connect the panel signal to `MainWindow.full_update_ui()` or expose a workflow menu action that calls it after mutation.

## Menus

Common menu actions:

- Load
- Load Zarr
- Save
- Export data
- View/DataViewer/Console
- Help/About links

Workflow-specific menu actions are returned by `workflow_action_names()`. `MainWindow` rebuilds the Analysis menu from those action names when the active workflow changes.

If a new workflow needs a new menu action, add the `QAction` in `MainWindow`, connect it to a small method, and return its action name from the workflow.

## Selection And DataViewer

Plot selections are resolved through the active workflow, not the processor.

Defaults:

- click selection uses `select_by_index_labels()`
- rectangular selection uses `select_by_2d_range()`

The default implementation selects rows from `plot_dataframe()`. Override these methods if selected plot points need to map back to a richer native model.

## Save And Export

`can_save()` controls native Save. Localization supports this through `MinFluxProcessor`; tracking workflows usually should leave it disabled unless they define a native format.

`can_export_data()` and `export_data_to_csv()` control CSV export. The default exports `plot_dataframe()`.

`stats_dataframe()` controls stats export. Return `None` if the workflow has no stats.

## Implementing A Real Tracking Workflow

Recommended shape:

1. Store tracks in a workflow-native model, not in `MinFluxProcessor`.
2. Build a minimal workflow panel with tracking-specific commands.
3. Convert tracks to `plot_dataframe()` only at the UI boundary.
4. Expose only meaningful plot axes and color columns.
5. Keep workflow actions small: mutate model, clear cached dataframe, call `full_update_ui()`.
6. Override selection methods if plot rows are not one-to-one with native track objects.
7. Avoid adding tracking concepts to localization classes or global enums.

## Current Examples

- `LocalizationWorkflow`: wraps the existing `WizardDialog` and `MinFluxProcessor`.
- `TrackingWorkflow`: minimal processor-free example using a list of track dictionaries, a dataframe adapter, length calculation, CSV export, and remove-largest-track actions.
