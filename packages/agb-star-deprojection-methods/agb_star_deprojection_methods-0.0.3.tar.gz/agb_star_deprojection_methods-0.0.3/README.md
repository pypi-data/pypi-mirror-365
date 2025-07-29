# AGB Star Deprojection

A package for visualising radially expanding circumstellar envelopes of AGB stars.

---

## Quick Start

### Installation

```bash
python3 -m pip install agb_star_deprojection_methods
```

### Import

```python
from agb_star_deprojection_methods.classes import CondensedData, StarData
```

### Initialise a StarData object

```python
fits_file = "example_fits_file.fits"  # relative path to fits file
distance_to_star = 8.04e8             # distance to star in AU
rest_frequency = 2.3e11               # rest frequency in Hz

star = StarData(fits_file, distance_to_star, rest_frequency)
```

### Plot channel maps (opens in matplotlib window)

```python
star.plot_channel_maps()  # many optional arguments
```

### Plot 3D deprojection using plotly

```python
star.plot_3D()  # many optional arguments
```

### Export to a CondensedData object

```python
data = star.export()
```

### Tweak parameters and create a new StarData object

```python
data.v_exp = 20
new_star = StarData(data)
```

### Expand envelope over time

```python
years = 1000
info = new_star(years)  # CondensedData object representing the envelope in 1000 years
expanded_star = StarData(info)
```

### Save animation frame-by-frame to a folder

```python
path_to_folder = "animation/frames"
star.plot_3D(folder = path_to_folder, num_angles = 100)
```

---

## Creating a Mask

To create a mask manually, use the following script:

```python
from agb_star_deprojection_methods.classes import StarData

fits_file = "example_fits_file.fits"
distance_to_star = 8.04e8
rest_frequency = 2.3e11

star = StarData(fits_file, distance_to_star, rest_frequency)

stds = 3  # number of standard deviations to initially filter by
savefile = "trial_mask.npy"  # .npy file to save mask to

# open mask selector
star.create_mask(filter_stds=stds, savefile=savefile)
```

Running this will open a matplotlib window with a subplot for each velocity channel.  
- **Double click** inside a subplot, then **drag to lasso points**.  
- When you finish dragging, press:
  - **A** to keep only these points in the mask,
  - **R** to remove these points from the mask,
  - **Enter** to do neither.
- Once you have completed the mask, close the matplotlib application.  
- The mask will be saved to the location specified by `savefile`.

To load the star data with the mask:

```python
from agb_star_deprojection_methods.classes import StarData

fits_file = "example_fits_file.fits"
distance_to_star = 8.04e8
rest_frequency = 2.3e11

maskfile = "trial_mask.npy"  # .npy file to load mask from

star = StarData(fits_file, distance_to_star, rest_frequency, maskfile)

# any other operations you want done
# ...
```

---

## Further Reading

See our report and more detailed documentation at https://psychedelickoala.github.io/agb-star-deprojection-docs/AGB-Star-Deprojection.html.