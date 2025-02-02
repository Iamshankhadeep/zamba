from enum import Enum
import os
from pathlib import Path
from typing import Optional

from loguru import logger
import pandas as pd
from pydantic.class_validators import root_validator, validator
from tqdm import tqdm

from zamba.data.video import VideoLoaderConfig
from zamba.models.config import (
    ZambaBaseModel,
    check_files_exist_and_load,
    validate_model_cache_dir,
)
from zamba.models.densepose.densepose_manager import MODELS, DensePoseManager
from zamba.models.utils import RegionEnum
from zamba.settings import VIDEO_SUFFIXES


class DensePoseOutputEnum(Enum):
    segmentation = "segmentation"
    chimp_anatomy = "chimp_anatomy"


class DensePoseConfig(ZambaBaseModel):
    """Configuration for running dense pose on videos.

    Args:
        video_loader_config (VideoLoaderConfig): Configuration for loading videos
        output_type (str): one of DensePoseOutputEnum (currently "segmentation" or "chimp_anatomy").
        render_output (bool): Whether to save a version of the video with the output overlaid on top.
            Defaults to False.
        embeddings_in_json (bool): Whether to save the embeddings matrices in the json of the
            DensePose result. Setting to True can result in large json files. Defaults to False.
        data_dir (Path): Where to find the files listed in filepaths (or where to look if
            filepaths is not provided).
        filepaths (Path, optional): Path to a CSV file with a list of filepaths to process.
        save_dir (Path, optional): Directory for where to save the output files;
            defaults to os.getcwd().
        cache_dir (Path, optional): Path for downloading and saving model weights. Defaults
            to env var `MODEL_CACHE_DIR` or the OS app cache dir.
        weight_download_region (RegionEnum, optional): region where to download weights; should
            be one of RegionEnum (currently 'us', 'asia', and 'eu'). Defaults to 'us'.
    """

    video_loader_config: VideoLoaderConfig
    output_type: DensePoseOutputEnum
    render_output: bool = False
    embeddings_in_json: bool = False
    data_dir: Path
    filepaths: Optional[Path] = None
    save_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None
    weight_download_region: RegionEnum = RegionEnum("us")

    _validate_cache_dir = validator("cache_dir", allow_reuse=True, always=True)(
        validate_model_cache_dir
    )

    def run_model(self):
        """Use this configuration to execute DensePose via the DensePoseManager"""
        if not isinstance(self.output_type, DensePoseOutputEnum):
            self.output_type = DensePoseOutputEnum(self.output_type)

        if self.output_type == DensePoseOutputEnum.segmentation.value:
            model = MODELS["animals"]
        elif self.output_type == DensePoseOutputEnum.chimp_anatomy.value:
            model = MODELS["chimps"]
        else:
            raise Exception(f"invalid {self.output_type}")

        output_dir = Path(os.getcwd()) if self.save_dir is None else self.save_dir

        dpm = DensePoseManager(
            model, model_cache_dir=self.cache_dir, download_region=self.weight_download_region
        )

        for fp in tqdm(self.filepaths.filepath, desc="Videos"):
            fp = Path(fp)

            vid_arr, labels = dpm.predict_video(fp, video_loader_config=self.video_loader_config)

            # serialize the labels generated by densepose to json
            output_path = output_dir / f"{fp.stem}_denspose_labels.json"
            dpm.serialize_video_output(
                labels, filename=output_path, write_embeddings=self.embeddings_in_json
            )

            # re-render the video with the densepose labels visualized on top of the video
            if self.render_output:
                output_path = output_dir / f"{fp.stem}_denspose_video{''.join(fp.suffixes)}"
                visualized_video = dpm.visualize_video(
                    vid_arr, labels, output_path=output_path, fps=self.video_loader_config.fps
                )

            # write out the anatomy present in each frame to a csv for later analysis
            if self.output_type == DensePoseOutputEnum.chimp_anatomy.value:
                output_path = output_dir / f"{fp.stem}_denspose_anatomy.csv"
                dpm.anatomize_video(
                    visualized_video,
                    labels,
                    output_path=output_path,
                    fps=self.video_loader_config.fps,
                )

    @root_validator(pre=False, skip_on_failure=True)
    def get_filepaths(cls, values):
        """If no file list is passed, get all files in data directory. Warn if there
        are unsupported suffixes. Filepaths is set to a dataframe, where column `filepath`
        contains files with valid suffixes.
        """
        if values["filepaths"] is None:
            logger.info(f"Getting files in {values['data_dir']}.")
            files = []
            new_suffixes = []

            # iterate over all files in data directory
            for f in values["data_dir"].rglob("*"):
                if f.is_file():
                    # keep just files with supported suffixes
                    if f.suffix.lower() in VIDEO_SUFFIXES:
                        files.append(f.resolve())
                    else:
                        new_suffixes.append(f.suffix.lower())

            if len(new_suffixes) > 0:
                logger.warning(
                    f"Ignoring {len(new_suffixes)} file(s) with suffixes {set(new_suffixes)}. To include, specify all video suffixes with a VIDEO_SUFFIXES environment variable."
                )

            if len(files) == 0:
                raise ValueError(f"No video files found in {values['data_dir']}.")

            logger.info(f"Found {len(files)} videos in {values['data_dir']}.")
            values["filepaths"] = pd.DataFrame(files, columns=["filepath"])
        return values

    @root_validator(skip_on_failure=True)
    def validate_files(cls, values):
        # if globbing from data directory, already have valid dataframe
        if isinstance(values["filepaths"], pd.DataFrame):
            files_df = values["filepaths"]
        else:
            # make into dataframe even if only one column for clearer indexing
            files_df = pd.DataFrame(pd.read_csv(values["filepaths"]))

        if "filepath" not in files_df.columns:
            raise ValueError(f"{values['filepaths']} must contain a `filepath` column.")

        # can only contain one row per filepath
        num_duplicates = len(files_df) - files_df.filepath.nunique()
        if num_duplicates > 0:
            logger.warning(
                f"Found {num_duplicates} duplicate row(s) in filepaths csv. Dropping duplicates so predictions will have one row per video."
            )
            files_df = files_df[["filepath"]].drop_duplicates()

        values["filepaths"] = check_files_exist_and_load(
            df=files_df,
            data_dir=values["data_dir"],
            skip_load_validation=True,
        )
        return values
