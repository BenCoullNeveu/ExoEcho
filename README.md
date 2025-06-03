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

<!-- ## Usage

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
``` -->

## Target List Requirements
The target list that you want to use has to meet certain citeria. First of all, it must be passed as a pandas.DataFrame to ensure consistency with the rest of the package. Most importantly, you must run it through the cleanTargets.py script, which will separate out some given values and their respective uncertainties, the latter(s) of which can be found under the column names f"{column} upper unc" and f"{column} lower unc". **Note that for upper or lower limit values, the given value will be kept but the "<" or ">" symbol will be remove.** Also, you can add which column should be ignored by the cleaning process (such as notes / remarks, target names, references, etc). 

Now for the most important prerequisite for the target lists: column names. I will list of the required target names (which are case sensitive). Please take note of the units, when applicable.

- Star Temperature [K]
- Star Radius [Rs]
- Star Distance [pc]
- Planet Name
- Planet Radius [Rjup]
- Planet Mass [Mjup]
- Planet Semi-major Axis [au]
- Planet Period [days]
- Transit Duration [hrs]

<!-- *Transit Duration [hrs]* is a special case, since it can also be estimated using pylightcurve, but that requires more information. -->

The following are optional column names. If they are not provided, the respective default values will be put instead (shown beside the name, separated by an arrow). Note that *Planet Albedo* is the planet's **bond** albedo. Default values for *Planet Albedo*, *Heat Redistribution Factor*, and *Mean Molecular Weight* are given by Edwards et al. [[1](#edwards)]. The default *Planet Geometric Albedo* is given by Heng et al. [[2](#heng)]

- Planet Albedo -> 0.2
- Heat Redistribution Factor -> 0.8
- Mean Molecular Weight -> 2.3
- Planet Geometric Albedo -> 0.25
- Eclipse Duration [hrs] -> made equal to transit duration [hrs]

## License

ExoEcho is licensed under the MIT License. See [LICENSE](LICENSE) for more information.

## Contact

If you have any questions or suggestions, feel free to reach out to us at benjamin.coull-neveu@mail.mcgill.ca.


## References
[1] <a name="edwards">Edwards et al., “An Updated Study of Potential Targets for Ariel.”</a>
[2] <a name="heng">Heng, Morris, and Kitzmann, “Closed-Formed Ab Initio Solutions of Geometric Albedos and Reflected Light Phase Curves of Exoplanets.”</a>