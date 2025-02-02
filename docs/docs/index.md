# Zamba

[![Docs Status](https://img.shields.io/badge/docs-stable-informational)](https://zamba.drivendata.org/docs/)
[![tests](https://github.com/drivendataorg/zamba/workflows/tests/badge.svg?branch=master)](https://github.com/drivendataorg/zamba/actions?query=workflow%3Atests+branch%3Amaster)
[![codecov](https://codecov.io/gh/drivendataorg/zamba/branch/master/graph/badge.svg)](https://codecov.io/gh/drivendataorg/zamba)
<!-- [![PyPI](https://img.shields.io/pypi/v/zamba.svg)](https://pypi.org/project/zamba/) -->

 <div class="embed-responsive embed-responsive-16by9" width=500>     <iframe width=600 height=340 class="embed-responsive-item" src="https://s3.amazonaws.com/drivendata-public-assets/monkey-vid.mp4" frameborder="0" allowfullscreen=""></iframe></div>

> *Zamba* means "forest" in Lingala, a Bantu language spoken throughout the Democratic Republic of the Congo and the Republic of the Congo.

**`zamba` is a tool built in Python that uses machine learning and computer vision to automatically detect and classify animals in camera trap videos.** You can use `zamba` to:

- Identify which species appear in each video
- Filter out blank videos
- Create your own custom models that identify your species in your habitats
- And more! 🙈 🙉 🙊

The official models in `zamba` can identify blank videos (where no animal is present) along with 32 species common to Africa and 11 species common to Europe. Users can also finetune models using their own labeled videos to then make predictions for new species and/or new ecologies.

`zamba` can be used both as a command-line tool and as a Python package. It is also available as a user-friendly website application, [Zamba Cloud](https://www.zambacloud.com/).

We encourage people to share their custom models trained with Zamba. If you train a model and want to make it available, please add it to the [Model Zoo Wiki](https://github.com/drivendataorg/zamba/wiki) for others to be able to use!



## Installing `zamba`

First, make sure you have the prerequisites installed:

* Python 3.7 or 3.8
* FFmpeg > 4.3

Then run:
```console
pip install https://github.com/drivendataorg/zamba/releases/latest/download/zamba.tar.gz
```

See the [Installation](install/) page of the documentation for details.

## Getting started

Once you have `zamba` installed, some good starting points are:

- The [Quickstart](quickstart/) page for basic examples of usage
- The user tutorial for either [classifying videos](predict-tutorial/) or [training a model](train-tutorial/) depending on what you want to do with `zamba`

## Example usage

Once `zamba` is installed, you can see the basic command options with:
```console
$ zamba --help
Usage: zamba [OPTIONS] COMMAND [ARGS]...

  Zamba is a tool built in Python to automatically identify the species seen
  in camera trap videos from sites in Africa and Europe. Visit
  https://zamba.drivendata.org/docs for more in-depth documentation.

Options:
  --version             Show zamba version and exit.
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  --help                Show this message and exit.

Commands:
  densepose  Run densepose algorithm on videos.
  predict    Identify species in a video.
  train      Train a model on your labeled data.
```

`zamba` can be used "out of the box" to generate predictions or train a model using your own videos. `zamba` supports the same video formats as FFmpeg, [which are listed here](https://www.ffmpeg.org/general.html#Supported-File-Formats_002c-Codecs-or-Features). Any videos that fail a set of FFmpeg checks will be skipped during inference or training.

### Classifying unlabeled videos

```console
$ zamba predict --data-dir path/to/videos
```

By default, predictions will be saved to `zamba_predictions.csv`. Run `zamba predict --help` to list all possible options to pass to `predict`.

See the [Quickstart](quickstart/) page or the user tutorial on [classifying videos](predict-tutorial/) for more details.

### Training a model

```console
$ zamba train --data-dir path/to/videos --labels path_to_labels.csv --save_dir my_trained_model
```

The newly trained model will be saved to the specified save directory. The folder will contain a model checkpoint as well as training configuration, model hyperparameters, and validation and test metrics. Run `zamba train --help` to list all possible options to pass to `train`.

You can use your trained model on new videos by editing the `train_configuration.yaml` that is generated by `zamba`. Add a `predict_config` section to the yaml that points to the checkpoint file that is generated:

```yaml
...
# generated train_config and video_loader_config
...

predict_config:
  checkpoint: PATH_TO_YOUR_CHECKPOINT_FILE

```

Now you can pass this configuration to the command line. See the [Quickstart](quickstart/) page or the user tutorial on [training a model](train-tutorial/) for more details.

You can then share your model with others by adding it to the [Model Zoo Wiki](https://github.com/drivendataorg/zamba/wiki).


## Contributing

We would love your contributions of code fixes, new models, additional training data, docs revisions, and anything else you can bring to the project!

See the docs page on [contributing to `zamba`](contribute/) for details.
