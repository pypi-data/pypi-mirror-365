- [MetGenC](#metgenc)
  * [Level of Support](#level-of-support)
  * [Requirements](#requirements)
  * [Installing MetGenC](#installing-metgenc)
  * [AWS Credentials](#aws-credentials)
    + [Option 1: Manually Create Configuration Files](#option-1-manually-create-configuration-files)
    + [Option 2: Use the AWS CLI to Create Configuration Files](#option-2-use-the-aws-cli-to-create-configuration-files)
  * [CMR Authentication and use of Collection Metadata](#cmr-authentication-and-use-of-collection-metadata)
  * [Before Running MetGenC: Tips and Assumptions](#before-running-metgenc-tips-and-assumptions)
    + [Assumptions for netCDF files for MetGenC](#assumptions-for-netcdf-files-for-metgenc)
    + [MetGenC .ini File Assumtions](#metgenc-ini-file-assumtions)
    + [NetCDF Attributes MetGenC Relies upon to generate UMM-G json files](#netcdf-attributes-metgenc-relies-upon-to-generate-umm-g-json-files)
    + [Attribute Reference links](#attribute-reference-links)
    + [Geometry Logic](#geometry-logic)
      - [Geometry Logic and Expectations Table](#geometry-logic-and-expectations-table)
  * [Running MetGenC: Its Commands In-depth](#running-metgenc-its-commands-in-depth)
    + [help](#help)
    + [init](#init)
      - [Optional Configuration Elements](#optional-configuration-elements)
      - [Granule and Browse regex](#granule-and-browse-regex)
        * [Example: Use of granule_regex](#example-use-of-granule_regex)
      - [Using Premet and Spatial Files](#using-premet-and-spatial-files)
      - [Setting Collection Spatial Extent as Granule Spatial Extent](#setting-collection-spatial-extent-as-granule-spatial-extent)
      - [Setting Collection Temporal Extent as Granule Temporal Extent](#setting-collection-temporal-extent-as-granule-temporal-extent)
      - [Spatial Polygon Generation](#spatial-polygon-generation)
        * [Example Spatial Polygon Generation Configuration](#example-spatial-polygon-generation-configuration)
    + [info](#info)
      - [Example running info](#example-running-info)
    + [process](#process)
      - [Examples running process](#examples-running-process)
      - [Troubleshooting metgenc process command runs](#troubleshooting-metgenc-process-command-runs)
    + [validate](#validate)
      - [Example running validate](#example-running-validate)
    + [Pretty-print a json file in your shell](#pretty-print-a-json-file-in-your-shell)
  * [Troubleshooting](#troubleshooting)
  * [For Developers](#for-developers)
    + [Contributing](#contributing)
      - [Requirements](#requirements-1)
      - [Installing Dependencies](#installing-dependencies)
      - [Run tests](#run-tests)
      - [Run tests when source changes](#run-tests-when-source-changes)
      - [Running the linter for code style issues](#running-the-linter-for-code-style-issues)
      - [Running the code formatter](#running-the-code-formatter)
      - [Ruff integration with your editor](#ruff-integration-with-your-editor)
      - [Spatial Polygon Diagnostic Tool](#spatial-polygon-diagnostic-tool)
      - [Releasing](#releasing)

<p align="center">
  <img alt="NSIDC logo" src="https://nsidc.org/themes/custom/nsidc/logo.svg" width="150" />
</p>

# MetGenC

![build & test workflow](https://github.com/nsidc/granule-metgen/actions/workflows/build-test.yml/badge.svg)
![publish workflow](https://github.com/nsidc/granule-metgen/actions/workflows/publish.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/granule-metgen/badge/?version=latest)](https://granule-metgen.readthedocs.io/en/latest/?badge=latest)
[![Documentation Status](https://readthedocs.org/projects/granule-metgen/badge/?version=stable)](https://granule-metgen.readthedocs.io/en/stable/?badge=stable)

The `MetGenC` toolkit enables Operations staff and data
producers to create metadata files conforming to NASA's Common Metadata Repository UMM-G
specification and ingest data directly to NASA EOSDIS’s Cumulus archive. Cumulus is an
open source cloud-based data ingest, archive, distribution, and management framework
developed for NASA's Earth Science data.

## Level of Support

This repository is fully supported by NSIDC. If you discover any problems or bugs,
please submit an Issue. If you would like to contribute to this repository, you may fork
the repository and submit a pull request.

See the [LICENSE](LICENSE.md) for details on permissions and warranties. Please contact
nsidc@nsidc.org for more information.

## Requirements

To use the `nsidc-metgen` command-line tool, `metgenc`, you must have
Python version 3.12 installed. To determine the version of Python you have, run
this at the command-line:

    $ python --version

or

    $ python3 --version

## Installing MetGenC

MetGenC can be installed from [PyPI](https://pypi.org/). First, create a
Python virtual environment (venv) in a directory of your choice, then activate it. To do this...

On a Mac, open Terminal and run:

    $ python -m venv /Users/afitzger/metgenc (i.e. provide the path and name of the venv where you'll house MetGenC)
    $ source ~/metgenc/bin/activate (i.e., activates your newly created metgenc venv)

On a Windows machine, open a command prompt, navigate to the desired project directory in which
you wish to create your venv, then run:

    > python -m venv metgenc (i.e., in this case, a venv named "metgenc" is created within the current directory)
    > .\<path to venv>\Scripts\activate (i.e., activates your newly created metgenc venv)

cd into the venv directory (e.g., `$ cd metgenc`)

Now install MetGenC into the virtual environment using `pip` (this command _should_ be OS-agnostic):

    $ pip install nsidc-metgenc

## AWS Credentials

In order to process science data and stage it for Cumulus, you must create & setup AWS
credentials. There are two options to do this:

### Option 1: Manually Create Configuration Files

First, create a directory in your user's home directory to store the AWS configuration:

    $ mkdir -p ~/.aws

In the `~/.aws` directory, create a file named `config` with the contents:

    [profile cumulus-uat]
    region = us-west-2
    output = json

In the `~/.aws` directory, create a file named `credentials` with the contents:

    [cumulus-uat]
    aws_access_key_id = TBD
    aws_secret_access_key = TBD

The examples above create a [cumulus-uat AWS profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-format-profile).
If you require access to multiple AWS accounts, each with their own configuration--for example, different accounts for CUAT vs. CPROD--you
can use the [AWS CLI 'profile' feature to manage settings for each account](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-using-profiles), 
or you can edit the config and credentials files and just add `profile cumulus-prod` and `cumulus-prod` details, respectively.


Finally, restrict the permissions of the directory and files:

    $ chmod -R go-rwx ~/.aws

**Instructions for obtaining an AWS key pair are [covered here](https://github.com/nsidc/granule-metgen/wiki/MetGenC-Ancillary-Resources#22-generate-aws-long-term-access-key).**
Once generated edit your `~/.aws/credentials` file and replace `TBD` with the public and secret key values.

### Option 2: Use the AWS CLI to Create Configuration Files

You may install (or already have it installed) the AWS Command Line Interface on the
machine where you are running the tool. Follow the
[AWS CLI Install instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
for the platform on which you are running.

Once you have the AWS CLI, you can use it to create the `~/.aws` directory and the
`config` and `credentials` files:

    $ aws configure

You will be prompted to enter your AWS public access and secret key values, along with
the AWS region and CLI output format. The AWS CLI will create and populate the directory
and files with your values.

## CMR Authentication and use of Collection Metadata

MetGenC will attempt to authenticate with Earthdata Login (EDL) credentials
to retrieve collection metadata. If authentication fails,
collection metadata will not be accessible to help compensate for metadata elements
missing from science files or a data set's configuration (.ini) file.

Always export the following variables to your environment before running
`metgenc process` (there's more on what this entails to come):

    $ export EARTHDATA_USERNAME=your-EDL-user-name
    $ export EARTHDATA_PASSWORD=your-EDL-password

If you have a different user name/password combo for UAT from that of the PROD
environment, be sure to set the values appropriate for the environment you're
ingesting to.

If collection metadata are unavailable either due to an authentication failure
or because the collection information doesn't yet exist in CMR, MetGenC will
continue processing with the information available from the .ini file and the
science files.

## Before Running MetGenC: Tips and Assumptions

* Activate your venv:

        $ source ~/<name of your venv>/bin/activate

* Verify the application version:

        $ metgenc --version
        metgenc, version 1.3.0

* Before you run end-to-end ingest, be sure to source your AWS credentials:

        $ source metgenc-env.sh cumulus-uat

  * If you think you've already run it but can't remember, run the following:

            $ aws configure list

and will either indicate that you need to source your credentials by returning:

```
Name                    Value             Type    Location
----                    -----             ----    --------
profile               <not set>           None    None
access_key            <not set>           None    None
secret_key            <not set>           None    None
region                <not set>           None    None
```
or it'll show that you're all set (AWS comms-wise) for ingesting to Cumulus by
returning the following:

```
      Name                    Value             Type    Location
      ----                    -----             ----    --------
   profile              cumulus-uat              env    ['AWS_PROFILE', 'AWS_DEFAULT_PROFILE']
access_key     ****************SQXY              env
secret_key     ****************cJ+5              env
    region                us-west-2              env    ['AWS_REGION', 'AWS_DEFAULT_REGION']
```

### Assumptions for netCDF files for MetGenC

* NetCDF files have an extension of `.nc` (per CF conventions).
* Projected spatial information is available in coordinate variables having
  a `standard_name` attribute value of `projection_x_coordinate` or
  `projection_y_coordinate` attribute.
* (y[0],x[0]) represents the upper left corner of the spatial coverage.
* Spatial coordinate values represent the center of the area covered by a measurement.
* Only one coordinate system is used by all data variables in all science files
  (i.e. only one grid mapping variable is present in a file, and the content of
  that variable is the same in every science file).

### MetGenC .ini File Assumtions
* A `pixel_size` attribute is needed in a data set's .ini file when gridded science files don't include a GeoTransform attribute in the grid mapping variable. The value specified should be just a number—no units (m, km) need to be specified since they're assumed to be the same as the units of those defined by the spatial coordinate variables in the data set's science files.
  * e.g., `pixel_size = 25`
* Date/time strings can be parsed using `datetime.fromisoformat`
* The checksum_type must be SHA256

### NetCDF Attributes MetGenC Relies upon to Generate UMM-G json Files

- **Required** required
- **RequiredC** conditionally required
- **R+** highly or strongly recommended
- **R** recommended
- **S** suggested

| Attribute used by MetGenC (location in netCDF file)   | ACDD | CF Conventions | NSIDC Guidelines | Notes   |
| ----------------------------- | ---- | -------------- | ---------------- | ------- |
| date_modified (global)        | S    |                | R                | 1, OC   |
| time_coverage_start (global)  | R    |                | R                | 2, OC, P   |
| time_coverage_end (global)    | R    |                | R                | 2, OC, P   |
| grid_mapping_name (variable)  |      | RequiredC      | R+               | 3       |
| crs_wkt (variable with `grid_mapping_name` attribute)      |  |  | R     | 4       |
| GeoTransform (variable with `grid_mapping_name` attribute) |  |  | R     | 5, OC   |
| standard_name, `projection_x_coordinate` (variable) |  | RequiredC  |    | 6       |
| standard_name, `projection_y_coordinate` (variable) |  | RequiredC  |    | 7       |

Notes column key:

 OC = Optional configuration attributes (or elements of them) that may be represented
   in an .ini file in order to allow "nearly" compliant netCDF files to be run with MetGenC
   without premet/spatial files. See [Optional Configuration Elements](#optional-configuration-elements)

 P = Premet file attributes that may be specified in a premet file; when used, a
  `premet_dir`path must be defined in the .ini file.
  
 1 = Used to populate the production date and time values in UMM-G output; OC .ini
  attribte remains `date_modified` = \<value\>.
  
 2 = Used to populate the time begin and end UMM-G values; OC .ini attribute for
  time_coverage_start is `time_start_regex` = \<value\>, and for time_coverage_end the
  .ini attribute is `time_coverage_duration` = \<value\>.
 
 3 = A grid mapping variable is required if the horizontal spatial coordinates are not
   longitude and latitude and the intent of the data provider is to geolocate
   the data. `grid_mapping` and `grid_mapping_name` allow programmatic identification of
   the variable holding information about the horizontal coordinate reference system.
   
 4 = The `crs_wkt` ("coordinate referenc system well known text") value is handed to the
   `CRS` and `Transformer` modules in `pyproj` to conveniently deal
   with the reprojection of (y,x) values to EPSG 4326 (lon, lat) values.

 5 = The `GeoTransform` value provides the pixel size per data value, which is then used
   to calculate the padding added to x and y values to create a GPolygon enclosing all
   of the data; OC .ini attribute is `pixel_size` = <value>.
   
 6 = The values of the coordinate variable identified by the `standard_name` attribute
   with a value of `projection_x_coordinate` are reprojected and thinned to create a
   GPolygon, bounding rectangle, etc.
   
 7 = The values of the coordinate variable identified by the `standard_name` attribute
   with a value of `projection_y_coordinate` are reprojected and thinned to create a
   GPolygon, bounding rectangle, etc.
   

| netCDF file attributes not currently used by MetGenC | ACDD | CF Conventions | NSIDC Guidelines |
| ----------------------------- | ---- | -------------- | ---------------- |
| Conventions (global)          | R+   | Required       | R                |
| standard_name (data variable) | R+   | R+             |                  |
| grid_mapping (data variable)  |      | RequiredC      | R+               |
| axis (variable)               |      | R              |                  |
| geospatial_bounds (global)    | R    |                | R                |
| geospatial_bounds_crs (global)| R    |                | R                |
| geospatial_lat_min (global)   | R    |                | R                |
| geospatial_lat_max (global)   | R    |                | R                |
| geospatial_lat_units (global) | R    |                | R                |
| geospatial_lon_min (global)   | R    |                | R                |
| geospatial_lon_max (global)   | R    |                | R                |
| geospatial_lon_units (global) | R    |                | R                |

### Attribute Reference links
* https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3
* https://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html
* https://nsidc.org/sites/default/files/documents/other/nsidc-guidelines-netcdf-attributes.pdf

### Geometry Logic

The geometry behind the granule-level spatial representation (point, gpolygon, or bounding 
rectangle) required for a data set can be implemented by MetGenC via either: file-level metadata
(such as a CF/NSIDC Compliant netCDF file), `.spatial` / `.spo` files, or 
its collection-level spatial representation. 

When MetGenC is run with netCDF files that are
both CF and NSIDC Compliant (for those requirements, refer to the table:
[NetCDF Attributes Used to Populate the UMM-G files generated by MetGenC](#netcdf-attributes-used-to-populate-the-umm-g-files-generated-by-metgenc))
information from within the file's metadata will be used to generate an appropriate 
gpolygon or bounding rectangle for each granule.

In some cases, non-netCDF files, and/or netCDF files that are non-CF or non-NSIDC
compliant will require an operator to define or modify data set details expressed through
attributes in an .ini file, in other cases an operator will need to further modify the 
.ini file to specify paths to where premet and spatial files are stored for MetGenC to use
as input files.

For granules suited to using the spatial extent defined for its collection, 
a `collection_geometry_override=True` attribute/value pair can be added to the .ini file
(as long as it's a single bounding rectangle, and not two or more bounding rectangles).
Setting `collection_geometry_override=False` in the .ini file will make MetGenC look to the
science files or premet/spatial files for the granule-level spatial representation geometry
to use.

### Geometry Rules
|Granule Spatial Representation Geometry | Granule Spatial Representation Coordinate System (GSRCS) |
|--------------------------------------- | -------------------------------------------------------- |
| GPolygon (GPoly) | Geodetic |
| Bounding Rectangle (BR) | Cartesian |
| Points | Geodetic | 

### Geometry Logic and Expectations Table
```
.spo = .spo file associated with each granule science file defining GPoly vertices
.spatial = .spatial file associated with each granule science file to define: BR, Point, or data coordinates parsed from a science file (all of which are to be encompassed by a detailed GPoly generated by MetGenC)
```

| source | num points | GSRCS | error? | expected output | comments |
| ------ | ------------ | ---- | ------ | ------- | --- |
| .spo  |   any | cartesian | yes | | `.spo` inherently defines GPoly vertices; GPolys cannot be cartesian. |
| .spo   | <= 2 | geodetic | yes | | At least three points are required to define a GPoly. |
| .spo  | > 2 | geodetic | no | GPoly as described by `.spo` file contents. | |
| .spatial | 1 | cartesian | yes | | NSIDC data curators always associate a `GEODETIC` granule spatial representation with point data. |
| .spatial | 1 | geodetic | no | Point as defined by spatial file. | |
| .spatial | 2 | cartesian | no | BR as defined by spatial file. | |
| .spatial | >= 2 | geodetic | no | GPoly(s) calculated to enclose all points. | If `spatial_polygon_enabled=true` (default) and ≥3 points, uses optimized polygon generation with target coverage and vertex limits. |
| .spatial | > 2 | cartesian | yes | | There is no cartesian-associated geometry for GPolys. |
| science file (NSIDC/CF-compliant netCDF) | NA | cartesian | no | BR | min/max lon/lat points for BR expected to be included in global attributes. |
| science file (NSIDC/CF-compliant) | 1 or > 2 | geodetic | no | | Error if only two points. GPoly calculated from grid perimeter. |
| science file, non-NSIDC/CF-compliant netCDF or other format | NA | either | no | As specified by .ini file. | Configuration file must include a `spatial_dir` value (a path to the directory with valid `.spatial` or `.spo` files), or `collection_geometry_override=True` entry (which must be defined as a single point or a single bounding rectangle). |
| collection spatial metadata geometry = cartesian with one BR | NA | cartesian | no | BR as described in collection metadata. | |
| collection spatial metadata geometry = cartesian with one BR | NA | geodetic | yes | | Collection geometry and GSRCS must both be cartesian. |
| collection spatial metadata geometry = cartesian with two or more BR | NA | cartesian | yes | | Two-part bounding rectangle is not a valid granule-level geometry. |
| collection spatial metadata geometry specifying one or more points | NA | NA |  | | Not a known use case  |

## Running MetGenC: Its Commands In-depth

### help
Show MetGenC's help text:

        $ metgenc --help
        Usage: metgenc [OPTIONS] COMMAND [ARGS]...

          The metgenc utility allows users to create granule-level metadata, stage
          granule files and their associated metadata to Cumulus, and post CNM
          messages.

        Options:
          --help  Show this message and exit.

        Commands:
          info     Summarizes the contents of a configuration file.
          init     Populates a configuration file based on user input.
          process  Processes science files based on configuration file...
          validate Validates the contents of local JSON files.

* For detailed help on each command, run: `metgenc <command name> --help`:

        $ metgenc process --help

### init

The **init** command can be used to generate a metgenc configuration (i.e., .ini) file for
your data set, or edit an existing .ini file.
* You can skip this step if you've already acquired or made an .ini file and prefer editing it
  manually (any text editor will work).
* An existing configuration file can also be copied, renamed, and used with a different
  data set, just be sure to update paths, regex values, etc that are data set-specific!
* The .ini file's checksum_type should always be set to SHA256.
* If creating a new .ini, remember to include .ini trailing the name you choose.

```
metgenc init --help
Usage: metgenc init [OPTIONS]

  Populates a configuration file based on user input.

Options:
  -c, --config TEXT  Path to configuration file to create or replace
  --help             Show this message and exit
```

Example running **init**

    $ metgenc init -c ./init/<name of config file to create or modify>.ini

#### Optional Configuration Elements
Some attribute values may be read from the .ini file if the values
can't be gleaned from—or don't exist in—the science file(s), but whose 
values are known for the data set. Use of these elements can be typical 
for data sets comprising non-CF/non-NSIDC-compliant netCDF science files,
as well as non-netCDF data sets comprising .tif, .csv, .h5, etc. This  
approach assumes the attribute values are the same for all granules considering  
there's only one .ini file for a given data set. The element values must 
be manually added to the .ini file, as none of them are prompted for in the
`metgenc init` functionality.

See this project's GitHub file, `fixtures/test.ini` for examples.

| .ini element          | .ini section | (NetCDF) Attribute  | Note |
| -----------------------|-------------- | ------------------- | ---- |
| date_modified          | Collection    | date_modified       | 1    |
| time_start_regex       | Collection    | time_coverage_start | 2    |
| time_coverage_duration | Collection    | time_coverage_end   | 3    |
| pixel_size             | Collection    | GeoTransform        | 4    |

1. For ease, set this to be the year-month-day MetGenC is run (e.g., date_modified =
2025-07-22); including a precise time value is unnecessary (we're breaking from how SIPSMetgen
rolled here!).
2. Matched against file name to determine time coverage start value. Must match using
the named group `(?P<time_coverage_start>)`.
3. Duration value applied to `time_coverage_start` to determine `time_coverage_end`. Must
be a valid [ISO duration value](https://en.wikipedia.org/wiki/ISO_8601#Durations).
4. Rarely applicable for science files that aren't netCDF (.txt, .csv, .jpg, .tif, etc.). 

#### Granule and Browse regex
To identify browse files and declare a file name pattern when necessary
for grouping files in a granule and/or browse with files in a granule, two 
further .ini elements are available: 
| .ini element | .ini section | Note |
| ------------- | ------------- | ---- |
| browse_regex  | Collection    | 1    |
| granule_regex | Collection    | 2    |

Note column:
1. The file name pattern identifying a browse file. The default is `_brws`. This element is
 prompted for as one of the `metgenc init` prompts.
2. The file name pattern identifying related files. Must  capture all text
 comprising the granule name in UMM-G and CNM output, and must provide a match
 using the named group `(?P<granuleid>)`. This value must be added manually; it
 is **not** included in the `metgenc init` prompts.

##### Example: Use of `granule_regex` 
Given the `granule_regex`:
```
granule_regex = (NSIDC0081_SEAICE_PS_)(?P<granuleid>[NS]{1}\d{2}km_\d{8})(_v2.0_)(?:F\d{2}_)?(DUCk)
```
And two granules and their browse files:
```
NSIDC0081_SEAICE_PS_N25km_20211101_v2.0_DUCk.nc
NSIDC0081_SEAICE_PS_N25km_20211101_v2.0_F16_DUCk_brws.png
NSIDC0081_SEAICE_PS_N25km_20211101_v2.0_F17_DUCk_brws.png
NSIDC0081_SEAICE_PS_N25km_20211101_v2.0_F18_DUCk_brws.png
NSIDC0081_SEAICE_PS_S25km_20211102_v2.0_DUCk.nc
NSIDC0081_SEAICE_PS_S25km_20211102_v2.0_F16_DUCk_brws.png
NSIDC0081_SEAICE_PS_S25km_20211102_v2.0_F17_DUCk_brws.png
NSIDC0081_SEAICE_PS_S25km_20211102_v2.0_F18_DUCk_brws.png
```

- `(?:F\d{2}_)?` will match the `F16_`, `F17_` and `F18_` strings in the browse
file names, but the match will not be captured due to to the `?:` elements, and will
not appear in the granule name recorded in the UMM-G and CNM output.
- `N25km_20211101` and `S25km_20211102` will match the named capture group `granuleid`.
Each of those strings uniquely identify all files associated with a given granule.
- `NSIDC0081_SEAICE_PS_`, `_v2.0_` and `DUCk` will be combined with the `granuleid`
text to form the granule name recorded in the UMM-G and CNM output (in the case of
single-file granules, the file extension will be added to the granule name).

#### Using Premet and Spatial files
When necessary, the following two .ini elements can be used to define paths
to the directories containing `premet` and `spatial` files. The user will be
prompted for these values when running `metgenc init`.
| .ini element | .ini section |
| ------------- | ------------- |
| premet_dir    | Source        |
| spatial_dir   | Source        |

#### Setting Collection Spatial Extent as Granule Spatial Extent
In cases of data sets where granule spatial information is not available
by interrogating the data or via `spatial` or `.spo` files, the operator 
may set a flag to force the metadata representing each granule's spatial 
extents to be set to that of the collection. The user will be prompted 
for the `collection_geometry_override` value when running `metgenc init`.
The default value is `False`; setting it to `True` signals MetGenC to 
use the collection's spatial extent for each granule.
| .ini element                | .ini section |
| ---------------------------- | ------------- |
| collection_geometry_override | Source        |

#### Setting Collection Temporal Extent as Granule Temporal Extent
RARELY APPLICABLE (if ever)!! An operator may set an .ini flag to indicate
that a collection's temporal extent should be used to populate every granule
via granule-level ummg json to be the same TemporalExtent (SingleDateTime or 
BeginningDateTime and EndingDateTime) as what's defined for the collection. 
In other words, every granule in a collection would display the same start 
and end times in EDSC. In most collections, this is likely ill-advised use case.
The operator will be prompted for a `collection_temporal_override` 
value when running `metgenc init`. The default value is `False` and should likely
always be accepted; setting it to `True` is what would signal MetGenC to set each
granule to the collection's TemporalExtent.

| .ini element                 | .ini section |
| ----------------------------- | --------------|
| collection_temporal_override  | Source        |

#### Spatial Polygon Generation
MetGenC includes optimized polygon generation capabilities for creating spatial coverage polygons from point data, particularly useful for LIDAR flightline data. 

When a granule has an associated `.spatial` file containing geodetic point data (≥3 points), MetGenC will automatically generate an optimized polygon to enclose the data points instead of using the basic point-to-point polygon method. This results in more accurate spatial coverage with fewer vertices.

**This feature is optional but enabled by default within MetGenC. To disable or to change values**, edit the .ini file for the collection and add any or all of the following parameters and the values you'd like them to be. Largely the values shouldn't need to be altered, but should ingest fail for GPolygonSpatial errors, the attribute to add to the .ini file would be the `spatial_polygon_cartesian_tolerance`, and decreasing the coordinate precision (e.g., .0001 => .01).

**Configuration Parameters:**

| .ini section | .ini element                    | Type    | Default | Description |
| ------------- | -------------------------------- | ------- | ------- | ----------- |
| Spatial       | spatial_polygon_enabled          | boolean | true    | Enable/disable polygon generation for .spatial files |
| Spatial       | spatial_polygon_target_coverage  | float   | 0.98    | Target data coverage percentage (0.80-1.0) |
| Spatial       | spatial_polygon_max_vertices     | integer | 100     | Maximum vertices in generated polygon (10-1000) |
| Spatial       | spatial_polygon_cartesian_tolerance | float | 0.0001  | Minimum distance between polygon points in degrees (0.00001-0.01) |



##### Example Spatial Polygon Generation Configuration
Example showing content added to an .ini file, having edited the CMR default vertex tolerance (distance between two vertices) to decrease the precision of the GPoly coordinate pairs listed in the ummg json files MetGenC generates:
```ini
[Spatial]
spatial_polygon_enabled = true
spatial_polygon_target_coverage = 0.98
spatial_polygon_max_vertices = 100
spatial_polygon_cartesian_tolerance = .01
```
Example showing the key pair added to an .ini file to disable spatial polygon generation:
```ini
[Spatial]
spatial_polygon_enabled = false
```

**When Polygon Generation is Applied:**
- ✅ Granule has a `.spatial` file with ≥3 geodetic points
- ✅ `spatial_polygon_enabled = true` (default)
- ✅ Granule spatial representation is `GEODETIC`

**When Original Behavior is Used:**
- ❌ No `.spatial` file present (data from other sources)
- ❌ `spatial_polygon_enabled = false`
- ❌ Granule spatial representation is `CARTESIAN`
- ❌ Insufficient points (<3) for polygon generation
- ❌ Polygon generation fails (automatic fallback)

**Tolerance Requirements:**
The `spatial_polygon_cartesian_tolerance` parameter ensures that generated polygons meet NASA CMR validation requirements. The CMR system requires that each point in a polygon must have a unique spatial location - if two points are closer than the tolerance threshold in both latitude and longitude, they are considered the same point and the polygon becomes invalid. MetGenC automatically filters points during polygon generation to ensure this requirement is met.

This enhancement is backward compatible - existing workflows continue unchanged, and polygon generation only activates for appropriate `.spatial` file scenarios.

---

### info

The **info** command can be used to display the information within the configuration file as well as MetGenC system default values for data ingest.

```
metgenc info --help
Usage: metgenc info [OPTIONS]

  Summarizes the contents of a configuration file.

Options:
  -c, --config TEXT  Path to configuration file to display  [required]
  --help             Show this message and exit.
```

#### Example running info

```
metgenc info -c init/0081DUCkBRWS.ini
                   __
   ____ ___  ___  / /_____ ____  ____  _____
  / __ `__ \/ _ \/ __/ __ `/ _ \/ __ \/ ___/
 / / / / / /  __/ /_/ /_/ /  __/ / / / /__
/_/ /_/ /_/\___/\__/\__, /\___/_/ /_/\___/
                   /____/
Using configuration:
  + environment: uat
  + data_dir: ./data/0081DUCk
  + auth_id: NSIDC-0081DUCk
  + version: 2
  + provider: DPT
  + local_output_dir: output
  + ummg_dir: ummg
  + kinesis_stream_name: nsidc-cumulus-uat-external_notification
  + staging_bucket_name: nsidc-cumulus-uat-ingest-staging
  + write_cnm_file: True
  + overwrite_ummg: True
  + checksum_type: SHA256
  + number: 1000000
  + dry_run: False
  + premet_dir: None
  + spatial_dir: None
  + collection_geometry_override: False
  + collection_temporal_override: False
  + time_start_regex: None
  + time_coverage_duration: None
  + pixel_size: None
  + date_modified: None
  + browse_regex: _brws
  + granule_regex: (NSIDC0081_SEAICE_PS_)(?P<granuleid>[NS]{1}\d{2}km_\d{8})(_v2.0_)(?:F\d{2}_)?(DUCk)
```

* environment: reflects `uat` as this is the default environment. This can be changed on the command line when `metgenc process` is run by adding the `-e` / `--env` option (e.g., metgenc process -e prod).
* data_dir:, auth_id:, version:, provider:, local_output_dir:, and ummg_dir: (which is relative to the local_output_dir) are set by the operator in the config file.
* kinesis_stream_name: and staging_bucket_name: could be changed by the operator in the config file, but should be left as-is!
* write_cnm_file:, and overwrite_ummg: are editable by operators in the config file
  * write_cnm_file: can be set here as `true` or `false`. Setting this to `true` when testing allows you to visually qc cnm content as well as run `metgenc validate` to assure they're valid for ingest. Once known to be valid, and you're ready to ingest data end-to-end, this can be edited to `false` to prevent cnm files from being written locally if desired. They'll always be sent to AWS regardless of the value being `true` or `false`.
  * overwrite_ummg: when set to `true` will overwrite any existing UMM-G files for a data set present in the vm's MetGenC venv output/ummg directory. If set to `false` any existing files would be preserved, and only new files would be written.
* checksum_type: is another config file entry that could be changed by the operator, but should be left as-is!
* number: 1000000 is the default max granule count for ingest. This value is not found in the config file, thus it can only be changed by a DUCk developer if necessary.
* dry_run: reflects the option included (or not) by the operator in the command line when `metgenc process` is run.
* premet_dir:, spatial_dir:, collection_geometry_override:, collection_temporal_override:, time_start_regex:, time_coverage_duration:, pixel_size:, date_modified:, browse_regex:, and granule_regex: are all optional as they're data set dependent and should be set when necessary by operators within the config file.
---

### process
```
metgenc process --help

Usage: metgenc process [OPTIONS]

  Processes science files based on configuration file contents.

Options:
  -c, --config TEXT   Path to configuration file  [required]
  -d, --dry-run       Don't stage files on S3 or publish messages to Kinesis
  -e, --env TEXT      environment  [default: uat]
  -n, --number count  Process at most 'count' granules.
  -wc, --write-cnm    Write CNM messages to files.
  -o, --overwrite     Overwrite existing UMM-G files.
  --help              Show this message and exit.
```
The **process** command can be run either with or without specifying the `-d` / `--dry-run` option.
* When the dry run option is specified _and_ the `-wc` / `--write-cnm` option is invoked, or your config
file contains `write_cnm_file = true` (instead of `= false`), CNM files will be written locally to the output/cnm
directory. This promotes operators having the ability to validate and visually QC their content before letting them guide ingest to CUAT.
* When run without the dry run option, metgenc will transfer cnm messages to AWS, kicking off end-to-end ingest of
data and UMM-G files to CUAT.

When MetGenC is run on the VM, it must be run at the root of the vm's virtual environment, `metgenc`.

If running `metgenc process` fails, check for an error message in the metgenc.log to begin troubleshooting.

#### Examples running process
The following is an example of using the dry run option (-d) to generate UMM-G and write cnm as files (-wc) for three granules (-n 3):

    $ metgenc process -c ./init/test.ini -d -n 3 -wc

This next example would run end-to-end ingest of all granules (assuming < 1000000 granules) in the data directory specified in the test.ini config file
and their UMM-G files into the CUAT environment:

    $ metgenc process -c ./init/test.ini -e uat
Note: Before running **process** to ingest granules to CUAT (i.e., you've not set it to dry run mode),
**as a courtesy to Cumulus devs and ops folks, post Slack messages to NSIDC's `#Cumulus` and `cloud-ingest-ops`
channels, and post a quick "done" note when you're done ingest testing.**


#### Troubleshooting metgenc process command runs
* You'll need to have sourced (or source before you run it), your AWS profile by running `source metgenc-env.sh cumulus-uat`
  where `cumulus-uat` reflects the profile name specified in your AWS credential and config files.
  If you can't remember whether you've sourced your AWS profile, run `aws configure list` at the prompt.

If you run `$ metgenc process -c ./init/<some .ini file>` to test end-to-end ingest, but you get a flurry of errors,
see if sourcing your AWS credentials (`source metgenc-env.sh cumulus-uat`) solves the problem! Forgetting
to set up communications between MetGenC and AWS is easy to do, but thankfully, easy to fix.

* When MetGenC is run on the VM, it must be run at the root of the vm's virtual environment, `metgenc`.

* If running `metgenc process` fails, check for an error message in the metgenc.log (metgenc/metgenc.log) to aid your troubleshooting.

---

### validate

The **validate** command lets you review the JSON cnm or UMM-G output files created by
running `process`.

```
metgenc validate --help

Usage: metgenc validate [OPTIONS]

  Validates the contents of local JSON files.

Options:
  -c, --config TEXT  Path to configuration file  [required]
  -t, --type TEXT    JSON content type  [default: cnm]
  --help             Show this message and exit.
```

#### Example running validate

    $ metgenc validate -c init/modscg.ini -t ummg (adding the -t ummg option will validate all UMM-G files; -t cnm will validate all cnm files that have been written locally)
    $ metgenc validate -c init/modscg.ini (without the -t option specified, just all locally written cnm files will be validated)

The package `check-jsonschema` is also installed by MetGenC and can be used to validate a single file at a time:

    $ check-jsonschema --schemafile <path to schema file> <path to cnm or UMM-G file to check>

### Pretty-print a json file in your shell
This is not a MetGenC command, but it's a handy way to `cat` a file and omit having
to wade through unformatted json chaos:
`cat <UMM-G or cnm file name> | jq "."`

e.g., `cat NSIDC0081_SEAICE_PS_S25km_20211104_v2.0_DUCk.nc.cnm.json | jq "."` will
pretty-print the contents of that json file in your shell!

If running `metgenc validate` fails, check for an error message in the metgenc.log to begin troubleshooting.

## For Developers
### Contributing

#### Requirements

* [Python](https://www.python.org/) v3.12+
* [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)

You can install [Poetry](https://python-poetry.org/) either by using the [official
installer](https://python-poetry.org/docs/#installing-with-the-official-installer)
if you’re comfortable following the instructions, or by using a package
manager (like Homebrew) if this is more familiar to you. When successfully
installed, you should be able to run:

    $ poetry --version
    Poetry (version 1.8.3)

#### Installing Dependencies

* Use Poetry to create and activate a virtual environment

      $ poetry shell

* Install dependencies

      $ poetry install

#### Run tests

    $ poetry run pytest

#### Run tests when source changes
This uses [pytest-watcher](https://github.com/olzhasar/pytest-watcher)

    $ poetry run ptw . --now --clear

#### Running the linter for code style issues

    $ poetry run ruff check

[The `ruff` tool](https://docs.astral.sh/ruff/linter/) will check
the source code for conformity with various style rules. Some of
these can be fixed by `ruff` itself, and if so, the output will
describe how to automatically fix these issues.

The CI/CD pipeline will run these checks whenever new commits are
pushed to GitHub, and the results will be available in the GitHub
Actions output.

#### Running the code formatter

    $ poetry run ruff format

[The `ruff` tool](https://docs.astral.sh/ruff/formatter/) will check
the source code for conformity with source code formatting rules. It
will also fix any issues it finds and leave the changes uncommitted
so you can review the changes prior to adding them to the codebase.

As with the linter, the CI/CD pipeline will run the formatter when
commits are pushed to GitHub.

#### Ruff integration with your editor

Rather than running `ruff` manually from the commandline, it can be
integrated with the editor of your choice. See the
[ruff editor integration](https://docs.astral.sh/ruff/editors/) guide.

#### Spatial Polygon Diagnostic Tool

The `metgenc-polygons` command-line tool is a diagnostic utility for developers to investigate and validate the flightline polygons that MetGenC generates for collections. This tool is particularly useful for analyzing polygon quality, comparing generated polygons against CMR reference data, and debugging spatial processing issues.

**Installation:**
The diagnostic tool is automatically available after installing MetGenC:

    $ poetry install
    # or
    $ pip install nsidc-metgenc

**Usage:**

    $ metgenc-polygons --help

**Available Commands:**

* **`compare`** - Compare generated polygons with CMR polygons for collections
* **`validate`** - Validate polygon files and check data coverage
* **`info`** - Display tool information and usage

**Examples:**

Compare 10 random granules from LVISF2 collection:

    $ metgenc-polygons compare LVISF2 -n 10 --provider NSIDC_CPRD

Compare a specific granule with authentication:

    $ metgenc-polygons compare LVISF2 --granule "GRANULE_NAME" --token-file ~/.edl_token

Validate a polygon file and check data coverage:

    $ metgenc-polygons validate polygon.geojson --check-coverage --points-file points.csv

**Output:**
The tool generates comparison reports including:
- Visual plots comparing generated vs CMR polygons
- Coverage statistics and polygon quality metrics
- GeoJSON files of generated polygons for further analysis
- Summary reports with processing metadata

All output files are saved to the specified output directory (default: `polygon_comparisons/`).

#### Releasing

* Update `CHANGELOG.md` according to its representation of the current version:
  * If the current "version" in `CHANGELOG.md` is `UNRELEASED`, add an
    entry describing your new changes to the existing change summary list.

  * If the current version in `CHANGELOG.md` is **not** a release candidate,
    add a new line at the top of `CHANGELOG.md` with a "version" consisting of
    the string literal `UNRELEASED` (no quotes surrounding the string).  It will
    be replaced with the release candidate form of an actual version number
    after the `major`, `minor`, or `patch` version is bumped (see below). Add a
    list summarizing the changes (thus far) in this new version below the
    `UNRELEASED` version entry.

  * If the current version in `CHANGELOG.md`  **is** a release candidate, add
    an entry describing your new changes to the existing change summary list for
    this release candidate version. The release candidate version will be
    automatically updated when the `rc` version is bumped (see below).

* Commit `CHANGELOG.md` so the working directory is clean.

* Show the current version and the possible next versions:

        $ bump-my-version show-bump
        1.4.0 ── bump ─┬─ major ─── 2.0.0rc0
                       ├─ minor ─── 1.5.0rc0
                       ├─ patch ─── 1.4.1rc0
                       ├─ release ─ invalid: The part has already the maximum value among ['rc', 'release'] and cannot be bumped.
                       ╰─ rc ────── 1.4.0release1

* If the currently released version of `metgenc` is not a release candidate
  and the goal is to start work on a new version, the first step is to create a
  pre-release version. As an example, if the current version is `1.4.0` and
  you'd like to release `1.5.0`, first create a pre-release for testing:

        $ bump-my-version bump minor

  Now the project version will be `1.5.0rc0` -- Release Candidate 0. As testing
  for this release-candidate proceeds, you can create more release-candidates by:

        $ bump-my-version bump rc

  And the version will now be `1.5.0rc1`. You can create as many release candidates as needed.

* When you are ready to do a final release, you can:

        $ bump-my-version bump release

  Which will update the version to `1.5.0`. After doing any kind of release, you will see
  the latest commit and tag by looking at `git log`. You can then push these to GitHub
  (`git push --follow-tags`) to trigger the CI/CD workflow.

* On the [GitHub repository](https://github.com/nsidc/granule-metgen), click
  'Releases' and follow the steps documented on the
  [GitHub Releases page](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release).
  Draft a new Release using the version tag created above. By default, the 'Set
  as the latest release' checkbox will be selected. To publish a pre-release
  from a release candidate version, be sure to select the 'Set as a pre-release'
  checkbox. After you have published the (pre-)release in GitHub, the MetGenC
  Publish GHA workflow will be started.  Check that the workflow succeeds on the
  [MetGenC Actions page](https://github.com/nsidc/granule-metgen/actions),
  and verify that the
  [new MetGenC (pre-)release is available on PyPI](https://pypi.org/project/nsidc-metgenc/).

## Credit

This content was developed by the National Snow and Ice Data Center with funding from
multiple sources.
