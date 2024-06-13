# ExoEcho

Welcome to ExoEcho! This repository contains the ExoEcho package, a tool for estimating signal and noise of exoplanet observations. 

## Features

- Provides a tool to create Telescope objects.
- Estimates signal & noise of observations conducted by customizable Telescopes! 
- Provides a variety of commonly-used telescope systems for exoplanetary observations.
- Various tools specifically made for the upcoming Ariel mission, including all the instruments at key spectral resolutions. In particular, it provides useful plotting functions for the Ariel telescope.

## Installation

To install ExoEcho, simply run the following command:

```bash
pip install exoecho
```

## Usage

Here's a quick example to get you started:

```python
import exoecho

# Getting Billy Edwards' target list


# Creating telescope object
jwst_nirspec = Telescope(name="JWST NIRSpec", diameter=6.5, wavelength_range=(0.6, 5.3), resolution=100, throughput=0.36)

# Preprocess the data
preprocessed_data = exoecho.preprocess(data)

# Detect echoes
echoes = exoecho.detect_echoes(preprocessed_data)

# Analyze and visualize the results
exoecho.analyze(echoes)
exoecho.visualize(echoes)
```

## License

ExoEcho is licensed under the MIT License. See [LICENSE](LICENSE) for more information.

## Contact

If you have any questions or suggestions, feel free to reach out to us at benjamin.coull-neveu@mail.mcgill.ca.
