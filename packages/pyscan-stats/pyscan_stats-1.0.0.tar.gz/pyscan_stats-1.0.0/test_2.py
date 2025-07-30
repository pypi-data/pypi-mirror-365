import pyscan
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import tqdm
import matplotlib.patches as patches
import time

def plot_result(b_arr, m_arr, extents, rect=None, rect2=None, max_area=None):
    print('Plotting...')
    non_nan_b = b_arr[~np.isnan(b_arr)]
    non_nan_m = m_arr[~np.isnan(m_arr)]
    vmin = min(non_nan_b.min(), non_nan_m.min(), np.abs(non_nan_b - non_nan_m).min())
    vmax = max(non_nan_b.max(), non_nan_m.max(), np.abs(non_nan_b - non_nan_m).max())
    fig, axs = plt.subplots(1, 2, figsize=(6, 3))

    # Plot Baseline (b)
    im1 = axs[0].imshow(b_arr, cmap='coolwarm', vmin=vmin, vmax=vmax, extent=extents,origin='lower')
    axs[0].set_title('Baseline')

    # Plot Measure (m)
    im2 = axs[1].imshow(m_arr, cmap='coolwarm', vmin=vmin, vmax=vmax, extent=extents, origin='lower')
    axs[1].set_title('Measure')

    if rect is not None:
        for ax in axs:
            rect_patch = patches.Rectangle(
                (rect.lowX(), rect.lowY()), rect.upX() - rect.lowX(), rect.upY() - rect.lowY(),
                linewidth=2, edgecolor='k', facecolor='none'
            )
            ax.add_patch(rect_patch)
        axs[0].text(rect.lowX() -1, rect.lowY() - 1, f'Area Limited \n Subgrid \n ({max_area} cells)', color='k', fontsize=11)

    if rect2 is not None:
        for ax in axs:
            rect_patch = patches.Rectangle(
                (rect2.lowX(), rect2.lowY()), rect2.upX() - rect2.lowX(), rect2.upY() - rect2.lowY(),
                linewidth=2, edgecolor='r', facecolor='none'
            )
            ax.add_patch(rect_patch)
        axs[0].text(rect2.lowX(), rect2.lowY() - 0.5, 'Unlimited Subgrid', color='darkred', fontsize=11)

    plt.tight_layout()
    plt.show()

def grid_to_np(grid):
    print('Converting grid to numpy...')
    size = grid.size()
    m_arr = np.zeros((size, size))
    b_arr = np.zeros((size, size))
    for y in tqdm.tqdm(range(size)):
        for x in range(size):
            b_arr[y, x] = grid.blueWeight(y, x)  # Note: 
            m_arr[y, x] = grid.redWeight(y, x)
    # remember, in pyscan grid, y,x are sorted from small to large. So we have to flip the y-axis
    # m_arr = np.flipud(m_arr)
    # b_arr = np.flipud(b_arr)
    return m_arr, b_arr


unique_xs = np.array([0, 1, 2])
unique_ys = np.array([0, 1, 2])
extents = (unique_xs[0], unique_xs[-1], unique_ys[0], unique_ys[-1])
b_arr = np.ones((len(unique_ys), len(unique_xs)))
m_arr = np.ones((len(unique_ys), len(unique_xs)))
# Add a block of 3x3 1s in m_arr
m_arr[1:3, 1:3] = 2

print("Baseline array (b_arr):")
print(b_arr)
print("Measure array (m_arr):")
print(m_arr)

# transform m_arr to N,3 2D array of coord, coord, value
n_m_arr = np.zeros((m_arr.size, 3))
n_b_arr = np.zeros((b_arr.size, 3))
coords = np.array(np.meshgrid(unique_xs, unique_ys)).T.reshape(-1, 2)
n_m_arr[:, :2] = coords
n_b_arr[:, :2] = coords
for i in range(coords.shape[0]):
    n_m_arr[i, 2] = m_arr[coords[i, 1], coords[i, 0]]
    n_b_arr[i, 2] = b_arr[coords[i, 1], coords[i, 0]]
m_arr = n_m_arr
b_arr = n_b_arr

grid = pyscan.Grid(unique_xs, unique_ys, m_arr, b_arr)

m_arr, b_arr = grid_to_np(grid)
print("Converted Measure array (m_arr):")
print(m_arr)
print("Converted Baseline array (b_arr):")
print(b_arr)


disc_f = pyscan.RKULLDORF

max_area = 1000

print('Limited grid size run...')
subgrid = pyscan.max_subgrid_linear(grid, 1, -1, max_area)

rect = grid.toRectangle(subgrid)
col0, col1, row0, row1 = subgrid.lowCol(), subgrid.upCol(), subgrid.lowRow(), subgrid.upRow()

width = col1 - col0
height = row1 - row0
fvalue = subgrid.fValue()

cell_height_x = unique_xs[1] - unique_xs[0]
cell_width_y = unique_ys[1] - unique_ys[0]

xB, xU, yB, yU = rect.lowX(), rect.upX(), rect.lowY(), rect.upY()

# Rect size in number of cells
rect_size_area = width * height
print(f'Fvalue: {fvalue}')
print(f'Width: {width} cells, Height: {height} cells')
print(f'Area: {rect_size_area} cells')
print(f'Area limit: {max_area} cells')
print(f'Rectangle: ({col0}, {col1}), ({row0}, {row1})')
print(f"Rectangle coordinates: ({xB}, {yB}), ({xU}, {yU})")

plot_result(b_arr, m_arr, extents, rect, max_area=rect_size_area)

print('done')