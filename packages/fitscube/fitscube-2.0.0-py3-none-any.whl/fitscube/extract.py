"""Extract a plane out of a larger fits cube"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path

import astropy.units as u
import numpy as np
from astropy.io import fits
from radio_beam import Beam, Beams

from fitscube.exceptions import ChannelMissingException, FREQMissingException
from fitscube.logging import logger, set_verbosity


@dataclass
class ExtractOptions:
    """Basic options to extract a plane of data"""

    hdu_index: int = 0
    """The HDU in the fits cube to access (e.g. for header and data)"""
    channel_index: int = 0
    """The channel of the cube to extract"""
    overwrite: bool = False
    """overwrite the output file, if it exists"""
    output_path: Path | None = None
    """The output path of the new file. If None it is generated from the name of base fits cube."""


@dataclass
class FreqWCS:
    """Exxtract of frequency information in the WCS taken straight from
    the fits header."""

    axis: int
    """The axis count that the frequency corresponds to"""
    ctype: str
    """The FITS WCS key name"""
    crpix: int
    """The reference index position"""
    crval: float
    """The reference value stored in the header"""
    cdelt: float
    """The step between planes"""
    cunit: str
    """the unit of the frequency information"""


def get_output_path(input_path: Path, channel_index: int) -> Path:
    """Create the output path to write the plane to

    Args:
        input_path (Path): The base input path name
        channel_index (int): The channel index to extract

    Returns:
        Path: New output path for the plane-only fits image
    """
    # The input_path suffix returns a string with a period
    channel_suffix = f".channel-{channel_index}{input_path.suffix}"
    output_path = input_path.with_suffix(channel_suffix)

    logger.debug(f"The formed {output_path=}")

    return output_path


def fits_file_contains_beam_table(header: fits.header.Header | Path) -> bool:
    """Consider whether a fits file contains a beam table

    Args:
        header (fits.header.Header | Path): Header to examine. If a Path load the first HDU list

    Returns:
        bool: Whether the fits header indicates a beam table
    """
    loaded_header: fits.header.Header = (
        fits.getheader(header) if isinstance(header, Path) else header
    )

    if "CASAMBM" not in loaded_header:
        return False

    return bool(loaded_header["CASAMBM"])


def extract_beam_from_beam_table(fits_path: Path, channel_index: int) -> Beam:
    """Extract the beam that corresponds to the channel requested. The beam
    is drawn from a beam table that is inserted into the FITS cube. It is
    expected that the beam table exists.

    Args:
        fits_path (Path): The fits table to inspect for a beam table, and return the channel beam
        channel_index (int): The channel to extract the beam for

    Raises:
        ValueError: Raised when a beam table can not be found

    Returns:
        Beam: The beam that corresponds to a desired channel
    """
    logger.info(f"Searching for a beam table in {fits_path=}")
    with fits.open(fits_path) as open_fits:
        beams: Beams | None = None

        if "BEAMS" not in open_fits:
            msg = "Beam table was not found"
            raise ValueError(msg)

        beam_hdu = open_fits["BEAMS"]

        logger.info("Found the beams binary table")
        beams = Beams.from_fits_bintable(beam_hdu)

        assert beams is not None, "beams is empty, which should not happen"

    return beams[channel_index]


def find_freq_axis(header: fits.header.Header) -> FreqWCS:
    """Attempt to find the axies of the channel in the data
    cube that corresponds to frequency/channels.

    Args:
        header (fits.header.Header): The header from the fits cube

    Returns:
        FreqWCS: The information in the FITS header describing the frequency of the cube
    """

    naxis = header["NAXIS"]
    # Remember that range upper limit is exclusive
    for axis in range(1, naxis + 1):
        if "FREQ" in header[f"CTYPE{axis}"]:
            logger.info(f"Found FREQ at {axis=}")
            return FreqWCS(
                axis=axis,
                ctype=header[f"CTYPE{axis}"],
                crpix=header[f"CRPIX{axis}"],
                crval=header[f"CRVAL{axis}"],
                cdelt=header[f"CDELT{axis}"],
                cunit=header[f"CUNIT{axis}"],
            )

    msg = "Did not find the frequency axis"
    raise FREQMissingException(msg)


def create_plane_freq_wcs(original_freq_wcs: FreqWCS, channel_index: int) -> FreqWCS:
    """Create the frequency fields appropriate for a extracted channel

    Args:
        original_freq_wcs (FreqWCS): The frequency information describing the spectral axis
        channel_index (int): The channel to extract

    Returns:
        FreqWCS: The frequency information for a channel
    """
    channel_freq = original_freq_wcs.crval + (channel_index * original_freq_wcs.cdelt)
    return FreqWCS(
        axis=original_freq_wcs.axis,
        ctype=original_freq_wcs.ctype,
        crpix=1,
        crval=channel_freq,
        cdelt=original_freq_wcs.cdelt,
        cunit=original_freq_wcs.cunit,
    )


def update_header_for_frequency(
    header: fits.header.Header,
    freq_wcs: FreqWCS,
    channel_index: int,
    extract_beam_from_file: Path | None = None,
) -> fits.header.Header:
    # Get the new wcs items for the channels
    plane_freq_wcs = create_plane_freq_wcs(
        original_freq_wcs=freq_wcs, channel_index=channel_index
    )
    _idx = freq_wcs.axis
    out_header = header.copy()
    out_header[f"CTYPE{_idx}"] = plane_freq_wcs.ctype
    out_header[f"CRPIX{_idx}"] = plane_freq_wcs.crpix
    out_header[f"CRVAL{_idx}"] = plane_freq_wcs.crval
    out_header[f"CDELT{_idx}"] = plane_freq_wcs.cdelt
    out_header[f"CUNIT{_idx}"] = plane_freq_wcs.cunit

    if extract_beam_from_file and fits_file_contains_beam_table(
        header=extract_beam_from_file
    ):
        try:
            channel_beam: Beam = extract_beam_from_beam_table(
                fits_path=extract_beam_from_file, channel_index=channel_index
            )

            out_header["BMAJ"] = channel_beam.major.to(u.deg).value
            out_header["BMIN"] = channel_beam.minor.to(u.deg).value
            out_header["BPA"] = channel_beam.pa.to(u.deg).value
        except ValueError:
            logger.info("Unable to find beam table, continuing anyway.")
            # A single beam could still be defined as the BMAJ/BMIN/BPA
            # and would have been copied to output_header from the outset

        out_header.pop("CASAMBM", None)

    return out_header


def extract_plane_from_cube(fits_cube: Path, extract_options: ExtractOptions) -> Path:
    """Extract the channel image from a cube, and output it as a new
    fits file. The dimensionality of the data will be the same as the
    input cube.

    Args:
        fits_cube (Path): The base fits cube to draw from
        extract_options (ExtractOptions): Options to drive the extraction

    Returns:
        Path: The output file
    """
    output_path: Path = (
        extract_options.output_path
        if extract_options.output_path
        else get_output_path(
            input_path=fits_cube, channel_index=extract_options.channel_index
        )
    )

    logger.info(f"Opening {fits_cube=}")
    with fits.open(
        name=fits_cube, mode="readonly", memmap=True, lazy_load_hdus=True
    ) as open_fits:
        logger.info(
            f"Extracting header and data for hdu_index={extract_options.hdu_index}"
        )
        header = open_fits[extract_options.hdu_index].header
        data = open_fits[extract_options.hdu_index].data

    logger.info("Extracted header and data")

    logger.info(f"Data shape: {data.shape}")
    freq_axis_wcs = find_freq_axis(header=header)
    freq_cube_index = len(data.shape) - freq_axis_wcs.axis

    if extract_options.channel_index > data.shape[freq_axis_wcs.axis] - 1:
        msg = f"{extract_options.channel_index=} outside of channel cube {data.shape=}"
        raise ChannelMissingException(msg)

    # Get the channel index requested
    freq_plane_data = np.take(data, extract_options.channel_index, axis=freq_cube_index)
    # and pad it back so dimensions match
    freq_plane_data = np.expand_dims(freq_plane_data, axis=freq_cube_index)
    freq_plane_header = update_header_for_frequency(
        header=header,
        freq_wcs=freq_axis_wcs,
        channel_index=extract_options.channel_index,
        extract_beam_from_file=fits_cube
        if fits_file_contains_beam_table(header)  # replace with "BEAMS" in opened fits?
        else None,
    )

    logger.info(f"Writing to {output_path=}")
    fits.writeto(
        output_path,
        data=freq_plane_data,
        header=freq_plane_header,
        overwrite=extract_options.overwrite,
    )

    return output_path


def get_parser(parser: ArgumentParser | None = None) -> ArgumentParser:
    parser = (
        parser
        if parser
        else ArgumentParser(description="Extract a plane from a fits cube")
    )

    parser.add_argument("fits_cube", type=Path, help="The cube to extract a plane from")
    parser.add_argument(
        "--channel-index", type=int, default=0, help="The channel to extract"
    )
    parser.add_argument(
        "--hdu-index",
        type=int,
        default=0,
        help="The HDU index of the data card containing the cube data",
    )
    parser.add_argument(
        "-v", "--verbosity", default=0, action="count", help="Increase output verbosity"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite the output file, if it exists.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=None,
        help="The name of the new output file. If not specified it is generated from the fits cube name",
    )

    return parser


def cli(args: Namespace | None = None) -> None:
    if args is None:
        parser = get_parser()
        args = parser.parse_args()

    extract_options = ExtractOptions(
        hdu_index=args.hdu_index,
        channel_index=args.channel_index,
        overwrite=args.overwrite,
        output_path=args.output_path,
    )
    set_verbosity(
        verbosity=args.verbosity,
    )
    extract_plane_from_cube(fits_cube=args.fits_cube, extract_options=extract_options)


if __name__ == "__main__":
    cli()
