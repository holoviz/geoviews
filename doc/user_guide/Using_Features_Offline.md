# Using Features Offline

## Creating Environment

Under the hood, GeoViews features simply wrap ``cartopy`` features, so it's a matter of properly
configuring ``cartopy`` ahead of time.

1. Create a new cartopy environment (or use an existing one):

    ```bash
    conda create -n cartopy_env python=3.10
    ```

2. Install the required packages:

    ```bash
    conda install -c conda-forge geoviews cartopy cartopy_offlinedata
    ```

    Or if you have an environment already, you may just need [`cartopy_offlinedata`](https://anaconda.org/conda-forge/cartopy_offlinedata):

    ```bash
    conda install -c conda-forge cartopy_offlinedata
    ```

## Verifying Setup

Now, we will verify that the shapefiles are available offline.

1. Ensure offline shapefiles were downloaded:

    ```python
    from pathlib import Path
    import cartopy

    data_dir = Path(cartopy.config["pre_existing_data_dir"])
    shapefiles = data_dir / "shapefiles" / "natural_earth" / "cultural"
    list(shapefiles.glob("*"))
    ```

2. Test GeoViews offline (toggle internet off):

    ```python
    import geoviews as gv
    from bokeh.resources import INLINE

    gv.extension("bokeh")

    coastline = gv.feature.coastline()
    borders = gv.feature.borders()
    world = (coastline * borders).opts(global_extent=True)

    gv.save(world, "world.html", resources=INLINE)
    ```

    Please ensure to set [`resources=INLINE`](https://docs.bokeh.org/en/latest/docs/reference/resources.html#bokeh.resources.INLINE) if the machine you're using is completely
    offline and you intend to view the output on that machine.
    Failure to do so will result in the HTML file appearing empty when opened.

## Changing Directory

If you wish to change the default data directory, follow these steps.

1. Create a new directory and move the data:

    ```python
    from pathlib import Path
    import cartopy

    new_data_dir = Path("~/.cartopy").expanduser()
    new_data_dir.mkdir(exist_ok=True)

    data_dir = Path(cartopy.config["pre_existing_data_dir"])
    data_dir.rename(new_data_dir / "cartopy")
    ```

2. Point to the new data directory within the script:

    ```python
    from pathlib import Path

    import cartopy
    import geoviews as gv
    from bokeh.resources import INLINE

    cartopy.config["pre_existing_data_dir"] = str(Path("~/.cartopy/cartopy").expanduser())

    gv.extension("bokeh")

    coastline = gv.feature.coastline()
    borders = gv.feature.borders()
    world = (coastline * borders).opts(global_extent=True)

    gv.save(world, "world.html", resources=INLINE)
    ```

3. Or set an environment variable ``CARTOPY_DATA_DIR``:

    For sh:
    ```bash
    export CARTOPY_DATA_DIR="$HOME/.cartopy/cartopy"
    ```

    For powershell:
    ```powershell
    $env:CARTOPY_DATA_DIR = "$HOME/.cartopy/cartopy"
    ```

    For cmd:
    ```cmd
    set CARTOPY_DATA_DIR=%USERPROFILE%\.cartopy\cartopy
    ```

    Please note using tilde (``~``) in the environment variable will not work.
