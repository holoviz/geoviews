# GitHub Copilot Instructions for GeoViews

## About GeoViews

GeoViews is a Python library that makes it easy to explore and visualize geographical, meteorological, and oceanographic datasets. It's built on top of HoloViews and uses Cartopy for geographic projections, with support for both Matplotlib and Bokeh plotting backends.

## Development Environment Setup

### Prerequisites
- **Python**: 3.10, 3.11, 3.12, or 3.13
- **Pixi**: Package and environment manager (install from https://pixi.sh/)
- **Git**: For version control
- **Node.js**: >=20 (for building JavaScript/TypeScript components)

### Getting Started
1. Clone the repository: `git clone https://github.com/holoviz/geoviews`
2. Install dependencies: `pixi install`
3. Download test data: `pixi run -e download-data download-data`
4. Sync git tags (for forked repos): `pixi run sync-git-tags`
5. Install in editable mode: `pixi run install`
6. Set up pre-commit hooks: `pixi run lint-install`

## Repository Structure

```
geoviews/
├── geoviews/          # Main Python package
│   ├── element/       # Geographic element types (Points, Polygons, etc.)
│   ├── operation/     # Geographic operations and transformations
│   ├── plotting/      # Plotting backend implementations
│   ├── models/        # Bokeh custom models and TypeScript code
│   ├── tests/         # Unit tests
│   └── data/          # Sample data files
├── examples/          # Jupyter notebooks with examples and user guide
├── doc/               # Sphinx documentation
└── scripts/           # Build and utility scripts
```

## Code Style and Linting

### Python
- Uses **Ruff** for linting and formatting
- Follows **NumPy docstring convention**
- Code style is enforced via pre-commit hooks
- Run linting: `pixi run lint`
- Install pre-commit: `pixi run lint-install`

### TypeScript/JavaScript
- Uses **ESLint** with TypeScript support
- Configuration in `geoviews/.eslintrc.js`
- Follows TypeScript strict mode practices

### Key Style Rules
- Line length: Flexible (E501 ignored)
- Imports: Use `isort` style with combined as-imports
- Docstrings: NumPy convention, but many docs rules are relaxed (D1, D200, D205, D400, D401, D404, D419 ignored)
- Type hints: Preferred but not strictly enforced everywhere

## Testing

### Test Environments
- `test-310`, `test-311`, `test-312`, `test-313`: Full test suite with different Python versions
- `test-core`: Core dependencies only
- `test-ui`: UI/browser tests with Playwright

### Running Tests
- Unit tests: `pixi run test-unit`
- Example tests (notebooks): `pixi run test-example`
- UI tests: `pixi run test-ui`

### Test Guidelines
- All PRs with code changes should include tests
- Tests are located in `geoviews/tests/`
- Example tests validate all Jupyter notebooks in `examples/`
- Use pytest fixtures and parametrization
- Run tests locally before pushing

## Dependencies

### Core Dependencies
- **bokeh** >=3.6.0: Interactive visualization library
- **cartopy** >=0.18.0: Cartographic projections and transformations
- **holoviews** >=1.16.0: Base visualization library
- **panel** >=1.0.0: Dashboard and app framework
- **numpy**, **pyproj**, **shapely**: Numerical and geometric operations

### Optional Dependencies
- **matplotlib**: Alternative plotting backend
- **geopandas**: GeoDataFrame support
- **xarray**, **iris**: Multi-dimensional array support
- **datashader**: Large dataset rendering

## Build Process

### Building the Package
- Python package: `pixi run build-pip`
- Conda package: `pixi run build-conda`
- NPM package: `pixi run build-npm`

### TypeScript/JavaScript Build
- Located in `geoviews/` directory
- Uses `tsconfig.json` for TypeScript configuration
- Outputs to `geoviews/dist/`

### Documentation
- Build docs: `pixi run docs-build` (takes ~1 hour)
- Uses **nbsite** for notebook-based documentation
- Uses **Sphinx** with **PyData theme**
- Dev docs available at https://dev.geoviews.org/

## Key Concepts

### Geographic Elements
- All elements have a `crs` (coordinate reference system) parameter
- Elements project data between coordinate systems automatically
- Common elements: `Points`, `Polygons`, `Path`, `Image`, `QuadMesh`, `Tiles`

### Plotting Backends
- **Bokeh**: Default, interactive plotting
- **Matplotlib**: Static plotting, better for publications
- Use `gv.extension('bokeh')` or `gv.extension('matplotlib')` to select

### Coordinate Reference Systems
- Uses **cartopy.crs** for projections
- `ccrs.PlateCarree()`: Standard lat/lon coordinates
- `ccrs.GOOGLE_MERCATOR`: Web Mercator (used by most tile services)

## Common Patterns

### Creating Geographic Visualizations
```python
import geoviews as gv
import cartopy.crs as ccrs
gv.extension('bokeh')

# Points with projection
points = gv.Points(data, crs=ccrs.PlateCarree())

# Overlaying with tiles
tiles = gv.tile_sources.OSM()
tiles * points
```

### Operations and Projections
```python
from geoviews.operation import project

# Project to different CRS
projected = project(element, projection=ccrs.GOOGLE_MERCATOR)
```

## Continuous Integration

### GitHub Actions Workflows
- **test.yaml**: Runs test suite on all PRs and main branch
- **docs.yaml**: Builds and deploys documentation
- **build.yaml**: Builds packages for releases
- **downstream_tests.yaml**: Tests dependent packages

### CI Best Practices
- Run tests locally before pushing
- Group commits into meaningful chunks
- CI runs on every push to main or PR branches
- Free CI resources are shared - be considerate

## Contributing Guidelines

### Pull Request Process
1. Fork the repository and create a feature branch
2. Make minimal, focused changes
3. Add or update tests as needed
4. Run linting: `pixi run lint`
5. Run relevant tests locally
6. Update documentation if needed
7. Submit PR with clear description

### Code Review Expectations
- Keep changes focused and minimal
- Include tests for new functionality
- Follow existing code style
- Update documentation for user-facing changes
- Respond to review feedback promptly

## Special Considerations

### Avoiding Common Pitfalls
- Don't modify `.pixi/` directory (auto-generated)
- Don't commit `node_modules/` or build artifacts
- Keep projection handling explicit with `crs` parameter
- Test with both Bokeh and Matplotlib backends when relevant
- Be careful with coordinate system transformations

### Performance
- Use **datashader** for large datasets
- Consider regridding operations for raster data
- Optimize projections to avoid unnecessary transformations

## Getting Help

- **Discord**: https://discord.gg/rb6gPXbdAr (`dev` channel)
- **Discourse**: https://discourse.holoviz.org/
- **Documentation**: https://geoviews.org
- **Issues**: https://github.com/holoviz/geoviews/issues

## Maintainers

- Philipp Rudiger (@philippjfr) - Project Director
- Simon Høxbro Hansen (@hoxbro) - Maintainer
- Andrew Huang (@ahuang11) - Maintainer

## Additional Resources

- Developer guide: `doc/developer_guide/index.md`
- Example notebooks: `examples/`
- HoloViz ecosystem: https://holoviz.org/
- Cartopy documentation: https://scitools.org.uk/cartopy/
