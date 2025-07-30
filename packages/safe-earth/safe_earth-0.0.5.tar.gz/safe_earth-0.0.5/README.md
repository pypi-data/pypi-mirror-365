# SAFE
Stratified Assessment of Forecasts over Earth

[Preprint](https://n-masi.github.io/papers/safe_masi.pdf) and [Website](https://n-masi.github.io/safe)

### Installation

`pip install safe-earth`

To build from source: `git clone git@github.com:N-Masi/safe.git`

After building from source, create a dev environment with the following steps

```
conda create -n safe.env
conda activate safe.env
pip install --file requirements.txt
conda install --channel conda-forge pygmt plotly typing_extensions
```

<!-- When running directly from the source repository, run files with `python -m safe_earth.<directory>.<file_without_extension>` while in the `src/` subdirectory. -->

### Example

An example of using the package to collect metrics on 6 AIWP models across the territory, subregion, and income 
attributes is availabe in `demos/wb2_240x121.py`. It assesses the models using 2020 ERA5 data.

### Data Notes

To unify the coordinate system across all integrated data sources, latitude ranges [-90, 90] with index 0 at -90, and longitude [-180, 180) but with index 0 at 0 and a wraparound from 180 to -180 in the middle. This is because metadata sourced from pygeoboundaries_geolab follows this coordinate system, and it is easiest to bring tabular data into conformance.

### Testing

Run `pytest` in the of the source repository directory.
