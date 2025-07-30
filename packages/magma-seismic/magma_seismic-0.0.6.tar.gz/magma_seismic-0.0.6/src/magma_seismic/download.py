import os
from datetime import datetime, timedelta
from typing import Self

import numpy as np
import pandas as pd
import requests
from obspy import Stream, UTCDateTime, read
from obspy.clients.earthworm import Client

from magma_seismic.const import HOST, PORT
from magma_seismic.magma_seismic import MagmaSeismic
from magma_seismic.plot import PlotSeismogram
from magma_seismic.utils import hours


class Download(MagmaSeismic):
    """Download seismic data to IDDS or SDS Format.

    Args:
        station (str): Station name.
        channel (str): Channel name.
        start_date (str): Start date.
        end_date (str): End date.
        channel_type (str, optional): Channel type. Defaults to "D".
        network (str, optional): Network name. Defaults to "VG".
        location (str, optional): Location. Defaults to "00".
        plot_seismogram (bool, optional): ONLY for SDS. Plot daily seismogram. Defaults to True.
        output_directory (str, optional): Output directory. Defaults to current directory.
        overwrite (bool, optional): Overwrite existing file. Defaults to False.
        verbose (bool, optional): To show detailed information. Defaults to False.
    """

    def __init__(
        self,
        station: str,
        channel: str,
        start_date: str,
        end_date: str,
        channel_type: str = "D",
        network: str = "VG",
        location: str = "00",
        plot_seismogram: bool = True,
        output_directory: str = None,
        overwrite: bool = False,
        verbose: bool = False,
    ):
        super().__init__(station, channel, channel_type, network, location, verbose)

        self.start_date_str = start_date
        self.end_date_str = end_date
        self.start_date: datetime = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date: datetime = datetime.strptime(end_date, "%Y-%m-%d")

        self.date_range: pd.DatetimeIndex = pd.date_range(
            start=self.start_date, end=self.end_date, freq="d"
        )

        if output_directory is None:
            output_directory = os.getcwd()
        self.output_directory = os.path.join(output_directory, "output")
        os.makedirs(self.output_directory, exist_ok=True)

        self.download_directory = os.path.join(self.output_directory, "download")
        os.makedirs(self.download_directory, exist_ok=True)

        self.plot_seismogram = plot_seismogram

        self.seismogram_dir = os.path.join(self.download_directory, "seismogram")
        if plot_seismogram:
            os.makedirs(self.seismogram_dir, exist_ok=True)

        self.overwrite = overwrite

        self.host = HOST
        self.port = PORT
        self.client = Client(host=HOST, port=PORT, timeout=5)

        self.failed = []
        self.success = []

        if verbose:
            print("=" * 50)
            print("Station: " + self.station)
            print("Channel: " + self.channel)
            print("Network: " + self.network)
            print("Location: " + self.location)
            print("=" * 50)
            print("Start date: " + self.start_date_str)
            print("End date: " + self.end_date_str)
            print("Output directory: " + self.output_directory)
            print("Download directory: " + self.download_directory)
            print("Overwrite file: " + str(self.overwrite))
            print("=" * 50)
            print("Client host: " + HOST)
            print("Client port: " + str(PORT))
            print("Timeout: " + str(5))
            print("=" * 50)

        print("Checking connection... ", end="")
        if Download.check_connection(HOST, PORT):
            print("✅ Ok!")

    @staticmethod
    def check_connection(host: str, port: int) -> bool:
        """Check connection to host and port.

        Args:
            host (str): Host.
            port (int): Port.

        Returns:
            bool: True if connection is established. False otherwise.

        Raises:
            ConnectionError: If host is unreachable.
        """
        if "http" not in host:
            host = f"http://{host}:{port}"

        response = requests.get(url=host, timeout=5)
        if not response.ok:
            raise ConnectionError(f"Cannot connect to {host}:{port}")

        return True

    def set_client(self, host: str, port: int, timeout: int) -> Self:
        """Set Winston Client.

        Args:
            host (str): Winston host
            port (int): Winston port
            timeout (int): Winston timeout

        Returns:
            Self
        """
        if Download.check_connection(host=host, port=port):
            host = host.replace("https://", "")
            host = host.replace("http://", "")
            self.host = host
            self.port = port

        self.client = Client(host=host, port=port, timeout=timeout)

        if self.verbose:
            print(f"ℹ️ Client using {host}:{port} with timeout {timeout}")

        return self

    def _idds(self, date: datetime, period: int, use_merge: bool = False) -> None:
        """Private method to download IDDS

        Args:
            date (datetime): Date to download
            period (int): Period to download
            use_merge (bool, optional): Whether to use merged traces. Defaults to False.

        Returns:
            None
        """
        year = date.year
        julian_day = date.strftime("%j")

        idds_directory = self.idds_dir(str(year), julian_day)

        start_date_str = date.strftime("%Y-%m-%d")

        end_date = date + timedelta(days=1) - timedelta(milliseconds=1)
        hour_ranges = pd.date_range(start=date, end=end_date, freq=f"{str(period)}min")
        for hour in hours(hour_ranges, period):
            hour_index = hour["index"]
            start_hour = hour["start_hour"]
            end_hour = hour["end_hour"]
            start_hour_str = hour["start_hour"].strftime("%H:%M:%S")
            end_hour_str = hour["end_hour"].strftime("%H:%M:%S")
            nslc: str = (
                f"{self.nslc}.{self.channel_type}.{str(year)}.{julian_day}.{hour_index}"
            )
            mseed_path: str = os.path.join(idds_directory, nslc)

            info = {
                "nslc": self.nslc,
                "date": start_date_str,
                "start_time": start_hour_str,
                "end_time": end_hour_str,
                "filename": mseed_path,
                "error": None,
            }

            if os.path.isfile(mseed_path) and not self.overwrite:
                print(
                    f"ℹ️ {start_date_str} {start_hour_str} to {end_hour_str} exists. Skipping"
                )
                print(f"🗃️ {mseed_path}")
                self.success.append(info)
                continue

            # Downloading miniseed
            try:
                if self.verbose:
                    print(f"-" * 75)
                    print(
                        f"⌛ {start_date_str} {start_hour_str} to {end_hour_str} :: Starting download"
                    )
                stream = self.client.get_waveforms(
                    network=self.network,
                    station=self.station,
                    location=self.location,
                    channel=self.channel,
                    starttime=start_hour,
                    endtime=end_hour,
                )

                if len(stream) == 0:
                    info["error"] = "Data not found in server"
                    self.failed.append(info)
                    print(
                        f"⚠️ {start_date_str} {start_hour_str} to {end_hour_str} :: Data not found in server"
                    )
                    continue

                if self.verbose:
                    print(
                        f"✅ {start_date_str} {start_hour_str} to {end_hour_str} :: Download completed"
                    )
            except Exception as e:
                info["error"] = f"Error downloading. {e}"
                self.failed.append(info)
                print(
                    f"❌ {start_date_str} {start_hour_str} to {end_hour_str} :: Error downloading {nslc}\n{e}"
                )
                continue

            # Writing miniseed
            try:
                for trace in stream:
                    trace.data = np.where(trace.data == -(2**31), 0, trace.data)
                    trace.data = trace.data.astype(np.int32)

                if use_merge:
                    try:
                        stream.merge(fill_value=0)
                        if self.verbose:
                            print(
                                f"🧲 {start_date_str} {start_hour_str} to {end_hour_str} :: "
                                f"Merged {len(stream)} traces."
                            )
                    except Exception as e:
                        info["error"] = f"Merging error. {e}"
                        self.failed.append(info)
                        if self.verbose:
                            print(
                                f"⚠️ {start_date_str} {start_hour_str} to {end_hour_str} :: "
                                f"Merging error. Continue without merging. {e}"
                            )
                        continue

                stream.write(mseed_path, format="MSEED")
                self.success.append(info)

                print(
                    f"🗃️ {start_date_str} {start_hour_str} to {end_hour_str} saved to :: {mseed_path}"
                )

            except Exception as e:
                info["error"] = f"Error writing trace. {e}"
                self.failed.append(info)
                print(
                    f"❌ Error writing {mseed_path} :: {start_hour_str} to {end_hour_str}\n{e}"
                )
                continue

        return None

    def to_idds(self, period: int = 60, use_merge: bool = False) -> None:
        """Download to IDDS directory.

        Args:
            period (int, optional): Download period in minutes. Defaults to 60 minutes.
            use_merge (bool, optional): Whether to merged traces. Defaults to False.

        Returns:
            None
        """
        assert 0 < period <= 60, ValueError(
            f"❌ Period must be between 1 to 60 minutes. "
            f"Your value is {period} minutes"
        )
        for _date in self.date_range:
            self._idds(_date, period=period, use_merge=use_merge)

        self.print_results()
        return None

    def relative_dir(self, year: str) -> str:
        """SDS relative directory.

        Args:
            year (str): SDS year directory.

        Returns:
            str: SDS relative directory.
        """
        return os.path.join(
            year,
            self.network,
            self.station,
            f"{self.channel}.{self.channel_type}",
        )

    def idds_dir(self, year: str, julian_day: str) -> str:
        """Get IDDS directory.

        Args:
            year (str): Year
            julian_day (str): Julian day

        Returns:
            str: IDDS directory
        """
        idds_directory: str = os.path.join(
            self.download_directory,
            "IDDS",
            self.relative_dir(year),
            julian_day,
        )
        os.makedirs(idds_directory, exist_ok=True)

        return idds_directory

    def sds_dir(self, year: str) -> str:
        """Return SDS directory.

        Args:
            year (str): Year of data.

        Returns:
            str: Path to SDS directory.
        """
        sds_dir = os.path.join(
            self.download_directory,
            "SDS",
            self.relative_dir(year),
        )
        os.makedirs(sds_dir, exist_ok=True)

        return sds_dir

    def _sds_chunking(
        self, date: datetime, chunk_size: int, chunk_dir: str, filename: str
    ) -> list[str]:
        chunk_files = []
        end_date = date + timedelta(days=1) - timedelta(milliseconds=1)
        hour_ranges = pd.date_range(
            start=date, end=end_date, freq=f"{str(chunk_size)}min"
        )

        for hour in hours(hour_ranges, chunk_size):
            index = hour["index"]
            start_hour = hour["start_hour"]
            end_hour = hour["end_hour"]
            start_hour_str = hour["start_hour"].strftime("%H:%M:%S")
            end_hour_str = hour["end_hour"].strftime("%H:%M:%S")

            try:
                chunk_filepath = os.path.join(chunk_dir, f"_{filename}.{index}")

                if os.path.isfile(chunk_filepath) and self.overwrite is False:
                    print(
                        f"ℹ️✅ {start_hour_str} to {end_hour_str} - {self.nslc} exists. Skipping"
                    )
                    chunk_files.append(chunk_filepath)
                    continue

                if self.verbose:
                    print(
                        f"ℹ️⌚ Chunk Downloading :: {start_hour_str} to {end_hour_str}"
                    )

                stream = self.client.get_waveforms(
                    network=self.network,
                    station=self.station,
                    location=self.location,
                    channel=self.channel,
                    starttime=start_hour,
                    endtime=end_hour,
                )

                if len(stream) == 0:
                    continue

                for trace in stream:
                    trace.data = np.where(trace.data == -(2**31), 0, trace.data)
                    trace.data = trace.data.astype(np.int32)

                stream.write(chunk_filepath, format="MSEED")
                chunk_files.append(chunk_filepath)
            except Exception as e:
                print(f"⚠️ Cannot download {start_hour_str} to {end_hour_str} :: {e}")
                continue

        if self.verbose:
            print(f"ℹ️🔢 Total chunk files: {len(chunk_files)}")

        return chunk_files

    def _sds(
        self, date: datetime, use_merge: bool = False, chunk_size: int = None
    ) -> None:
        """Private method to download to SDS directory.

        Args:
            date (datetime): Date to download.
            use_merge (bool, optional): Whether to merged traces. Defaults to False.
            chunk_size (int, optional): Chunk size. Defaults to None.

        Returns:
            None
        """
        julian_day = date.strftime("%j")
        year = date.year

        sds_dir = self.sds_dir(str(year))

        start_date_str = date.strftime("%Y-%m-%d")
        end_hour = date + timedelta(minutes=60 * 24) - timedelta(milliseconds=1)

        filename = f"{self.nslc}.{self.channel_type}.{year}.{julian_day}"
        filepath = os.path.join(sds_dir, filename)

        info = {
            "nslc": self.nslc,
            "date": start_date_str,
            "start_time": date.strftime("%H:%M:%S"),
            "end_time": end_hour.strftime("%H:%M:%S"),
            "filepath": filepath,
            "error": None,
        }

        if os.path.isfile(filepath) and self.overwrite is False:
            print(f"ℹ️ {start_date_str} - {self.nslc} exists. Skipping")
            print(f"🗃️ {start_date_str}: {filepath}")
            self.success.append(info)
            return None

        try:
            stream = Stream()
            chunk_files = []

            if self.verbose:
                print(f"-" * 75)
                print(f"⌛ {start_date_str} - {self.nslc} :: Starting download")

            # Using chunking files
            if chunk_size is not None:
                if self.verbose:
                    print(
                        f"🔢 {start_date_str} - {self.nslc} :: Using {chunk_size} minutes of chunking"
                    )

                tmp_dir = os.path.join(sds_dir, ".tmp")
                os.makedirs(tmp_dir, exist_ok=True)

                chunk_files = self._sds_chunking(
                    date=date,
                    chunk_size=chunk_size,
                    chunk_dir=tmp_dir,
                    filename=filename,
                )

                if len(chunk_files) == 0:
                    return None

                if self.verbose:
                    print(f"ℹ️ℹ️ Adding all {len(chunk_files)} traces")

                for _file in chunk_files:
                    try:
                        _stream = read(_file, format="MSEED")
                        stream += _stream
                    except Exception as e:
                        print(f"⚠️ Failed to append :: {e}")

                if self.verbose:
                    print(f"✅✅ Found {len(stream)} traces.")

            # Download without chunking
            else:
                stream = self.client.get_waveforms(
                    network=self.network,
                    station=self.station,
                    location=self.location,
                    channel=self.channel,
                    starttime=UTCDateTime(date),
                    endtime=UTCDateTime(end_hour),
                )

            if len(stream) == 0:
                info["error"] = "Data not found in server"
                self.failed.append(info)
                print(f"⚠️ {start_date_str} - {self.nslc} :: Data not found in server")
        except Exception as e:
            info["error"] = f"Error downloading. {e}"
            self.failed.append(info)
            print(f"❌ {start_date_str} - {self.nslc} :: Error downloading\n{e}")
            return None

        if len(stream) > 0:
            try:
                for trace in stream:
                    trace.data = np.where(trace.data == -(2**31), 0, trace.data)
                    trace.data = trace.data.astype(np.int32)

                if use_merge:
                    try:
                        stream.merge(fill_value=0)
                        if self.verbose:
                            print(
                                f"🧲 {start_date_str} - {self.nslc} :: Merged {len(stream)} traces."
                            )
                    except Exception as e:
                        info["error"] = f"Merging error. {e}"
                        self.failed.append(info)
                        if self.verbose:
                            print(
                                f"⚠️ {start_date_str} - {self.nslc} :: Continue without merging. {e}"
                            )

                stream.write(filepath, format="MSEED")

                self.success.append(info)

                if len(chunk_files) > 0:
                    if self.verbose:
                        print("🗑️ Cleanup temporary files..")
                    for _file in chunk_files:
                        if os.path.isfile(_file):
                            os.remove(_file)

                print(f"🗃️ {start_date_str} - {self.nslc} saved to :: {filepath}")

                if self.plot_seismogram:
                    self._plot_seismogram(
                        start_date=start_date_str,
                        stream=stream,
                        filepath=filepath,
                        relative_dir=self.relative_dir(str(year)),
                    )

            except Exception as e:
                info["error"] = f"Error writing trace. {e}"
                self.failed.append(info)
                print(f"❌ {start_date_str} Error writing {filepath} :: {e}")
        return None

    def to_sds(self, use_merge: bool = False, chunk_size: int = None) -> Self:
        """Download to SDS directory.

        Args:
            use_merge (bool, optional): Whether to merged traces. Defaults to False.
            chunk_size (int, optional): How many minutes of chunking. Defaults to None.

        Returns:
            Self: self
        """
        for _date in self.date_range:
            self._sds(_date, use_merge=use_merge, chunk_size=chunk_size)

        self.print_results()
        return self

    def _plot_seismogram(
        self, start_date: str, stream: Stream, filepath: str, relative_dir: str
    ) -> str:
        """Plot seismogram.

        Args:
            start_date (str): Start date of stream.
            stream (Stream): Stream to plot.
            filepath (str): Path to save plot.
            relative_dir (str): Relative path to save plot.

        Returns:
            str: Path to save plot.
        """
        image_path = PlotSeismogram(
            date=start_date,
            stream=stream,
            filepath=filepath,
            seismogram_dir=self.seismogram_dir,
            relative_dir=relative_dir,
            overwrite=self.overwrite,
            verbose=self.verbose,
        ).save()

        return image_path

    def print_results(self) -> None:
        """Print results to console.

        Returns:
            None
        """
        print(f"=" * 75)
        if len(self.failed) > 0:
            print(f"⚠️ Failed to download {len(self.failed)} traces")
        print(
            f"✅ Download completed for {self.nslc} :: {self.start_date_str} to {self.end_date_str}"
        )
        print(f"=" * 75)
        return None
