# QuantPunc

[![PyPI](https://img.shields.io/pypi/v/quantpunc.svg?color=green)](https://pypi.org/project/quantpunc)
[![Python Version](https://img.shields.io/pypi/pyversions/quantpunc.svg?color=green)](https://python.org)
[![License BSD-3](https://img.shields.io/pypi/l/quantpunc.svg?color=green)](https://github.com/tehahn/quantpunc/blob/main/LICENSE)

QuantPunc is a Napari plugin for puncta analysis and quantification in 2D microscopy images. You can also find QuantPunc on [Napari hub]. 

QuantPunc is currently in beta. Please report any problems to the [issues page].

## Features
1. Automated puncta labeling and counting
2. Watershed segmentation
3. Colocalization analysis 
4. Exportable counts and stats

## Installation
You can install `quantpunc` via Napari's plugin manager:

1. Click on "Plugins" in the toolbar.
2. Click on "Install/Uninstall Plugins..." in the context menu.
3. Type "quantpunc" in the searchbar.
4. Click install.

You can also install `quantpunc` via [pip]:

    pip install quantpunc

## Contributing
Contributions are very, very welcome. QuantPunc allows you to implement your own automated puncta labeler. If you're interested in making it available to everyone else or have any other improvements, feel free to send a pull request!

## License
Distributed under the terms of the [BSD-3] license,
QuantPunc is free and open source software

## Issues
QuantPunc is still in beta, so bugs are to be expected. Please report any problems to the [issues page].


[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[pip]: https://pypi.org/project/pip/

[ilastik]: https://www.ilastik.org/
[skimage’s blob detection]: https://scikit-image.org/docs/0.25.x/auto_examples/features_detection/plot_blob.html

[abstract_puncta_labeler]: src/quantpunc/quantification/abstract_puncta_labeler.py
[default_puncta_labelers]: src/quantpunc/quantification/default_puncta_labelers.py

[Napari hub]: https://napari-hub.org/plugins/quantpunc.html
[here]: https://tehahn.github.io/quantpunc/
[issues page]: https://github.com/tehahn/quantpunc/issues