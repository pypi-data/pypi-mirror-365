import os

from matplotlib import pyplot as plt
from obspy import Stream, Trace
from PIL import Image


class PlotSeismogram:
    def __init__(
        self,
        date: str,
        stream: Stream,
        filepath: str,
        seismogram_dir: str,
        relative_dir: str,
        filetype: str = "jpg",
        overwrite: bool = False,
        verbose: bool = False,
    ):
        self.date = date
        self.stream = stream

        filename = os.path.basename(filepath)
        self.filename = f"{filename}.{filetype}"

        filepath = os.path.join(seismogram_dir, relative_dir)
        os.makedirs(filepath, exist_ok=True)

        self.thumbnail_dir = os.path.join(filepath, "thumbnails")
        os.makedirs(self.thumbnail_dir, exist_ok=True)

        self.filepath = os.path.join(filepath, self.filename)
        self.thumbnail_filepath = os.path.join(self.thumbnail_dir, self.filename)

        self.overwrite = overwrite
        self.verbose = verbose

    def thumbnail(self) -> str:
        """Generate thumbnail of seismogram.

        Returns:
            str: Thumbnail file path.
        """
        image = Image.open(self.filepath)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.thumbnail((320, 180))
        image.save(self.thumbnail_filepath)

        return self.thumbnail_filepath

    def title(self, trace: Trace) -> str:
        """Generate title of seismogram.

        Args:
            trace (Trace): Trace of seismogram.

        Returns:
            str: Title of seismogram.
        """
        stats = trace.stats
        sampling_rate = stats.sampling_rate
        number_of_sample = stats.npts
        return f"{self.date} | {trace.id} | {sampling_rate} Hz | {number_of_sample} samples"

    def save(self) -> str | None:
        """Save seismogram plot.

        Returns:
            str | None: Seismogram image location.
        """
        image_exists = True if os.path.exists(self.filepath) else False
        thumbnail_exists = True if os.path.exists(self.thumbnail_dir) else False

        # Skip if file exists
        if image_exists and not self.overwrite:
            if not thumbnail_exists:
                self.thumbnail()

            if self.verbose:
                print(f"🖼️ {self.date} :: {self.filepath}")

            return self.filepath

        try:
            trace = self.stream[0]

            trace.plot(
                type="dayplot",
                interval=60,
                one_tick_per_line=True,
                color=["k"],
                outfile=self.filepath,
                number_of_ticks=13,
                size=(1600, 900),
                title=self.title(trace),
            )

            plt.close("all")

            if self.verbose:
                print(f"🖼️ {self.date} :: {self.filepath}")

            self.thumbnail()

            return self.filepath

        except IOError:
            print(f"⚠️ {self.date} Couldn't save : {self.filepath}")
            return None
