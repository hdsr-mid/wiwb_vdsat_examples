from datetime import date
from datetime import datetime
from geopandas import GeoSeries
from pathlib import Path
from shapely.geometry import box
from shapely.geometry import Point
from wiwb.api import Api
from wiwb.api_calls.get_grids import GetGrids
from wiwb.auth import Auth

import logging


logger = logging.getLogger(__name__)


def run_example():
    logger.info("start wiwb example")

    _now = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"wiwb_{_now}"
    DATA_OUTPUT_DIR = Path(f"./data_output/{dir_name}")
    DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=False)

    wiwb_client_id = "api-wiwb-hdsr-tollenaar-tmp"
    wiwb_client_secret = "Yz8Rrmc36TJ21FTLnKpVb6AMEY3oJUzS"
    auth = Auth(client_id=wiwb_client_id, client_secret=wiwb_client_secret)
    api = Api(auth=auth)

    data_sources = api.get_data_sources()
    logger.info("WIWB data sources:")
    for ds in sorted(data_sources.keys()):
        logger.info(f"    {ds}")
    # [
    # 'Knmi.International.Radar.Composite',
    # 'Knmi.International.Radar.Composite.Combined',
    # 'Knmi.International.Radar.Composite.Early.Reanalysis',
    # 'Knmi.International.Radar.Composite.Early.Reanalysis.Test',
    # 'Knmi.International.Radar.Composite.Final.Reanalysis',
    # 'Knmi.International.Radar.Composite.Final.Reanalysis.Test',
    # 'Knmi.International.Radar.Composite.Near.Realtime.Test',
    # 'Knmi.Radar.CorrectedB',
    # 'Knmi.Radar.CorrectedC2',
    # 'Knmi.Radar.CorrectedD2',
    # 'Knmi.Radar.Uncorrected',
    # 'Meteobase.Evaporation.Makkink',
    # 'Meteobase.Evaporation.PennmanMonteith',
    # 'Meteobase.Precipitation',
    # 'Satdata.Evapotranspiration.Reanalysis',
    # 'Satdata.Evapotranspiration.Reanalysis.V2'
    # ]

    data_source_code = "Meteobase.Precipitation"
    assert data_source_code in data_sources, "this example is outdated, unexpected data_sources"
    variables = api.get_variables(data_source_codes=[data_source_code])
    logger.info(f"datasource '{data_source_code}' has variables: {variables}")
    # {'P': {'Name': 'Precipitation', 'Code': 'P', 'Description': 'Neerslag', 'UnitCode': 'MM', 'State': 1}}
    assert "P" in variables, f"this example is outdated, unexpected variables for data_source {data_source_code}"

    logger.info("Download data (NetCDF = .nc) to disk: Precipitation between 1 jan 2018 - 2 jan 2018")
    grids = GetGrids(
        auth=auth,
        base_url=api.base_url,
        data_source_code=data_source_code,
        variable_code="P",
        start_date=date(2018, 1, 1),
        end_date=date(2018, 1, 2),
        data_format_code="netcdf4.cf1p6",
    )
    grids.run()
    grids.to_directory(output_dir=DATA_OUTPUT_DIR.as_posix())  # .nc in DATA_OUTPUT_DIR van 49 kb

    logger.info("Create points and polygon where we want to sample timeseries")
    LL_POINT = Point(119865, 449665)
    UR_POINT = Point(127325, 453565)
    OTHER_POINT = Point(135125, 453394)
    POLYGON = box(LL_POINT.x, LL_POINT.y, UR_POINT.x, UR_POINT.y)
    GEOSERIES = GeoSeries(
        [LL_POINT, UR_POINT, OTHER_POINT, POLYGON], index=["ll_point", "ur_point", "other_point", "polygon"], crs=28992
    )

    logger.info("Do the actual sampling and save timeseries to .csv")
    grids.set_geometries(GEOSERIES)
    df = grids.sample()
    csv_file_path = DATA_OUTPUT_DIR / f"samples_{_now}.csv"
    df.to_csv(csv_file_path.as_posix())

    logger.info("wiwb example finished")
