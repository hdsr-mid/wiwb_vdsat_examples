from datetime import date
from datetime import datetime
from geopandas import GeoSeries
from pathlib import Path
from shapely.geometry import box
from shapely.geometry import Point
from wiwb.sample import sample_nc_dir
from wiwb.sample import sample_netcdfs

import logging


logger = logging.getLogger(__name__)


def run_example():
    """VdSat has soil moisture (bodemvocht) .nc files three products:
        10cm below surface = DRZSM-SMAP-LN-DESC-T10_V003_100
        20cm below surface = DRZSM-SMAP-LN-DESC-T20_V003_100
        SM-SMAP-LN-DESC_V003_100
    However, vdSat api does not exist anymore. Therefore, we have downloaded whole history (till April 30th, 2024)
    and stored it here: H:DATA/WIWB_grids/.

    No token/password is required to sample vdsat .nc files
    """
    _now = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"vdsat{_now}"
    DATA_OUTPUT_DIR = Path(f"./data_output/{dir_name}")
    DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=False)

    H_DRIVE = Path("H:/")
    dir_path_vdsat = H_DRIVE / "DATA/WIWB_grids/VanderSat_Bodemvocht_HDSR"

    dir_source_vd_sat_drzsm_t10 = dir_path_vdsat / "DRZSM-SMAP-LN-DESC-T10_V003_100" / "Complete_files"
    dir_source_vd_sat_drzsm_t20 = dir_path_vdsat / "DRZSM-SMAP-LN-DESC-T20_V003_100" / "Complete_files"
    dir_source_vd_sat_sm = dir_path_vdsat / "SM-SMAP-LN-DESC_V003_100" / "Complete_files"
    assert dir_source_vd_sat_drzsm_t10.is_dir()
    assert dir_source_vd_sat_drzsm_t20.is_dir()
    assert dir_source_vd_sat_sm.is_dir()

    logger.info("Create points and polygon where we want to sample timeseries")
    LL_POINT = Point(119865, 449665)
    UR_POINT = Point(127325, 453565)
    OTHER_POINT = Point(135125, 453394)
    POLYGON = box(LL_POINT.x, LL_POINT.y, UR_POINT.x, UR_POINT.y)
    GEOSERIES = GeoSeries(
        [LL_POINT, UR_POINT, OTHER_POINT, POLYGON], index=["ll_point", "ur_point", "other_point", "polygon"], crs=28992
    )

    logger.info("Sample .nc files between 1 and 10 April 2015 (get p95 value and aggregate to point and polygon)")
    df1 = sample_nc_dir(
        dir_path=dir_source_vd_sat_drzsm_t20,
        variable_code=dir_source_vd_sat_drzsm_t20.parent.name,  # "DRZSM-SMAP-LN-DESC-T20_V003_100",
        geometries=GEOSERIES,
        stats="percentile_95",  # mean, min, max, percentile_x (eg. percentile_21)
        start_date=date(year=2015, month=4, day=1),
        end_date=date(year=2015, month=4, day=10),
    )
    csv_file_path = DATA_OUTPUT_DIR / f"samples_all_nc_agg_p95{_now}.csv"
    df1.to_csv(csv_file_path.as_posix())

    msg = "Sample subset of .nc files (get min value and aggregate to point and polygon), and save timeseries to .csv"
    logger.info(msg)
    first_three_files = [x for x in dir_source_vd_sat_sm.iterdir()][0:2]
    df2 = sample_netcdfs(
        nc_files=first_three_files,
        variable_code=dir_source_vd_sat_sm.parent.name,  # "SM-SMAP-LN-DESC_V003_100",
        geometries=GEOSERIES,
        stats="min",  # mean, min, max, percentile_x (eg. percentile_21)
        start_date=None,
        end_date=None,
    )
    csv_file_path = DATA_OUTPUT_DIR / f"samples_3_ncs_agg_min{_now}.csv"
    df2.to_csv(csv_file_path.as_posix())
