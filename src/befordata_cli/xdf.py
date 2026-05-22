from pathlib import Path
from typing import List

import pyarrow as pa
import pyarrow.feather as feather
from befordata import xdf
from icecream import ic
from pyxdf import load_xdf

ic.configureOutput(prefix='', noColor=False)

def xdf_info(filepath: str, info_dict:bool = False, streams: List[str] | None = None) -> tuple:
    """
    Extract metadata from an xdf file

    Args:
        filepath: path to the xdf file
        info_dict: if True, return a dictionary containing the metadata extracted from the xdf file
        streams: the streams to extract information for
    Return:
        metadata: dict containing the metadata extracted from the xdf file
    """
    xdf_streams, header = load_xdf(filepath)
    if streams is None:
        channel_ids = None
    else:
        channel_ids = [xdf.get_channel_id(xdf_streams, ch) for ch in streams]

    print(f"Streams in {filepath}")
    for cnt, stream in enumerate(xdf_streams):
        name = stream['info']['name'][0]
        if channel_ids is None or cnt in channel_ids:
            shape = stream['time_series'].shape
            stream_time = stream['time_stamps'][-1] - stream['time_stamps'][0]
            print(f"  {cnt}: {name}   ---   shape: {shape[0]} x {shape[1]}, duration {stream_time:.2f} seconds")

    if info_dict:
        for cnt, stream in enumerate(xdf_streams):
            if channel_ids is None or cnt in channel_ids:
                ic(stream['info'])

    return xdf_streams, header

def convert_data(
    filepath: str | Path,
    streams: List[str] | None = None,
    arrow: bool = False,
    csv: bool = False,
    compression: str | None = None,
):
    """
    Convert xdf streams to Arrow and/or CSV format.

    Args:
        filepath: path to the xdf file
        streams: the streams to convert
        arrow: if True, convert to Arrow format
        csv: if True, convert to CSV format
        compression: compression method for CSV output (e.g., 'gz', 'bz2','xz')
    """
    compression_options = [None, 'gz', 'bz2','xz']
    if compression not in compression_options:
        raise ValueError(f"Invalid compression option: {compression}. Valid options are: {compression_options}")

    if not arrow and not csv:
        print("No conversion format specified.")
    else:
        print(f"Converting to {'Arrow' if arrow else ''}{' and ' if arrow and csv else ''}{'CSV' if csv else ''}")

    filepath = Path(filepath)
    xdf_streams, header = load_xdf(filepath)
    if streams is None:
        channel_ids = None
    else:
        channel_ids = [xdf.get_channel_id(xdf_streams, ch) for ch in streams]

    for cnt, stream in enumerate(xdf_streams):
        name = stream['info']['name'][0]
        if channel_ids is None or cnt in channel_ids:
            new_stem = filepath.stem + f"_{name}"
            new_stem = new_stem.replace(" ", "_")
            new_path = filepath.with_stem(new_stem)
            print(f"    stream {cnt}: {name}  ---   {new_stem}")
            dat = xdf.data(xdf_streams, cnt)
            if arrow:
                tbl = pa.Table.from_pandas(dat, preserve_index=False)
                fl = new_path.with_suffix('.arrow')
                print(f"    writing {fl}")
                feather.write_feather(tbl, fl, compression="lz4", compression_level=6)
            if csv:
                ic(compression)
                suffix = ".csv" if compression is None else f".csv.{compression}"
                fl = new_path.with_suffix(suffix)
                print(f"    writing {fl}")
                dat.to_csv(fl, index=False, compression='infer')
