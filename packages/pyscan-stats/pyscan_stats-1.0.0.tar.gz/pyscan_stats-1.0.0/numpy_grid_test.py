import pyscan
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import tqdm
import matplotlib.patches as patches
import time
import seaborn as sns

ds_october = xr.open_dataset(f"data/pm_utah_2016_october.nc")
ds_january = xr.open_dataset(f"data/pm_utah_2016_january.nc")

extents = [ds_october.x.min(), ds_october.x.max(), ds_october.y.min(), ds_october.y.max()]

def upscale_resolution(ds, factor):
    minx, maxx = ds.x.min(), ds.x.max()
    miny, maxy = ds.y.min(), ds.y.max()
    new_x = np.linspace(minx, maxx, len(ds.x) * factor)
    new_y = np.linspace(maxy, miny, len(ds.y) * factor)
    new_ds = ds.interp(x=new_x, y=new_y, method='linear')
    return new_ds

# ds_october = upscale_resolution(ds_october, 4)
# ds_january = upscale_resolution(ds_january, 4)

def xr_to_coords(ds):
    ds_stacked = ds.stack(xy=['y', 'x'])  # Stack x and y into a single dimension
    ds_non_nan = ds_stacked.dropna('xy')  # Drop NaNs along the stacked dimension
    xs = ds.x.values
    x_non_nan = ds_non_nan.x.values
    ys = ds.y.values
    y_non_nan = ds_non_nan.y.values
    values_non_nan = ds_non_nan.value.values
    non_nan_array = np.column_stack((x_non_nan, y_non_nan, values_non_nan))
    return non_nan_array, np.unique(xs), np.unique(ys)


def xr_to_grid1_(ds_m, ds_b):
    print("Net grid...")
    b = []
    m = []
    pts = []
    for i in tqdm.tqdm(range(len(ds_m.x))):
        for j in range(len(ds_m.y)):
            # skip nan values
            # ACCESS is (y, x)
            if np.isnan(ds_m.value[j, i]) or np.isnan(ds_b.value[j, i]):
                continue
            x = ds_m.x[i]
            y = ds_m.y[j]

            v2 = ds_m.value[j, i]
            v1 = ds_b.value[j, i]

            b.append(pyscan.WPoint(v1, x, y, 1)) # january is baseline
            m.append(pyscan.WPoint(v2, x, y, 1)) # october is measure
        
    unique_xs = sorted(list(set(ds_m.x.values)))
    unique_ys = sorted(list(set(ds_m.y.values)))
    zip_ = list(zip(unique_xs, unique_ys))
    pts = [pyscan.Point(x, y, 1) for x, y in zip_]

    grid = pyscan.make_net_grid(pts, m, b)
    return grid


def xr_to_grid1(ds_m, ds_b):
    print("Net grid...")
    b_arr, unique_xs, unique_ys = xr_to_coords(ds_b)
    m_arr, _, _ = xr_to_coords(ds_m)
    pts = [pyscan.Point(x, y, 1) for x, y in zip(unique_xs, unique_ys)]
    b = [pyscan.WPoint(b, x, y, 1.) for b, x, y in zip(b_arr[:, 2], b_arr[:, 0], b_arr[:, 1])]
    m = [pyscan.WPoint(m, x, y, 1.) for m, x, y in zip(m_arr[:, 2], m_arr[:, 0], m_arr[:, 1])]

    grid = pyscan.make_net_grid(pts, m, b)
    return grid


def xr_to_grid0(ds_m, ds_b):
    print("Exact grid...")
    bs = [pyscan.WPoint(ds_b.value[j, i], ds_b.x[i], ds_b.y[j], 1) for i in range(len(ds_b.x)) for j in range(len(ds_b.y)) if not np.isnan(ds_b.value[j, i])]
    ms = [pyscan.WPoint(ds_m.value[j, i], ds_m.x[i], ds_m.y[j], 1) for i in range(len(ds_m.x)) for j in range(len(ds_m.y)) if not np.isnan(ds_m.value[j, i])]

    grid = pyscan.make_exact_grid(ms, bs)
    return grid

def print_grid_info(grid, ds_m, ds_b):
    print('Grid size:', grid.size())
    print('Size should be:', max(len(ds_m.x), len(ds_m.y)))
    print('Grid counts:', len(grid.getRedCounts()))
    print('Red counts sum:', sum(grid.getRedCounts()))
    print('Red counts sum should be:', ds_m.value.values[~np.isnan(ds_m.value.values)].sum())
    print('Blue counts sum:', sum(grid.getBlueCounts()))
    print('Blue counts sum should be:', ds_b.value.values[~np.isnan(ds_b.value.values)].sum())
    
    return grid

def xr_to_grid2(ds_m, ds_b):
    # Quantile based grid, b and m are used to define n (depending on resolution) quantiles
    # then the grid is constructed based on these quantiles.
    print("Resolution grid...")
    # arr ix nx3 x,t,value
    m_arr, unique_xs, unique_ys = xr_to_coords(ds_m)
    b_arr, _, _ = xr_to_coords(ds_b)
    b_points = [pyscan.WPoint(b, x, y, 1.) for b, x, y in zip(b_arr[:, 2], b_arr[:, 0], b_arr[:, 1])]
    m_points = [pyscan.WPoint(w, x, y, 1.) for w, x, y in zip(m_arr[:, 2], m_arr[:, 0], m_arr[:, 1])]
    res = max(len(unique_xs), len(unique_ys))
    grid = pyscan.Grid(res, m_points, b_points)
    return grid

def xr_to_grid3(ds_m, ds_b):
    print("Numpy grid...")
    m_arr, unique_xs, unique_ys = xr_to_coords(ds_m)
    b_arr, _, _ = xr_to_coords(ds_b)
    grid = pyscan.Grid(unique_xs, unique_ys, m_arr, b_arr)
    return grid

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
    m_arr = np.flipud(m_arr)
    b_arr = np.flipud(b_arr)
    return m_arr, b_arr

def plot_result(b_arr, m_arr, extents, rect=None, rect2=None):
    # create 3 subplots, 1 for b one m, one diff. if rect non-None, plot it on the the three subplots
    # use same color scale for all three subplots
    print('Plotting...')

    # Compute global min and max for consistent color scaling
    # Non nans values only
    non_nan_b = b_arr[~np.isnan(b_arr)]
    non_nan_m = m_arr[~np.isnan(m_arr)]
    vmin = min(non_nan_b.min(), non_nan_m.min(), np.abs(non_nan_b - non_nan_m).min())
    vmax = max(non_nan_b.max(), non_nan_m.max(), np.abs(non_nan_b - non_nan_m).max())

    fig, axs = plt.subplots(1, 3, figsize=(9, 3))

    # Plot Baseline (b)
    im1 = axs[0].imshow(b_arr, cmap='coolwarm', vmin=vmin, vmax=vmax, extent=extents)
    # cbar1 = plt.colorbar(im1, ax=axs[0], fraction=0.046, pad=0.04)
    axs[0].set_title('Baseline')

    # Plot Measure (m)
    im2 = axs[1].imshow(m_arr, cmap='coolwarm', vmin=vmin, vmax=vmax, extent=extents)
    # cbar2 = plt.colorbar(im2, ax=axs[0], fraction=0.046, pad=0.04)
    axs[1].set_title('Measure')

    # Plot Absolute Difference |b - m|
    im3 = axs[2].imshow(np.abs(b_arr - m_arr), cmap='coolwarm', extent=extents)
    # cbar3 = plt.colorbar(im3, ax=axs[0], fraction=0.046, pad=0.04)
    axs[2].set_title('Difference')

    # Add rectangle if it exists
    if rect is not None:
        for ax in axs:
            rect_patch = patches.Rectangle(
                (rect.lowX(), rect.lowY()), rect.upX() - rect.lowX(), rect.upY() - rect.lowY(),
                linewidth=2, edgecolor='k', facecolor='none'
            )
            ax.add_patch(rect_patch)
        # add a label to the rectangle indicating its Area Limited Subgrid (450 cells)
        # here
        axs[0].text(rect.lowX() -1, rect.lowY() - 1, 'Area Limited \n Subgrid \n (450 cells)', color='k', fontsize=11)

    
    if rect2 is not None:
        for ax in axs:
            rect_patch = patches.Rectangle(
                (rect2.lowX(), rect2.lowY()), rect2.upX() - rect2.lowX(), rect2.upY() - rect2.lowY(),
                linewidth=2, edgecolor='r', facecolor='none'
            )
            ax.add_patch(rect_patch)
        # add a label to the rectangle indicating its NUnlimited Subgrid
        axs[0].text(rect2.lowX(), rect2.lowY() - 0.5, 'Unlimited Subgrid', color='darkred', fontsize=11)

    plt.tight_layout()
    # plt.show()
    # plt.savefig(f"{RESULTS_PATH}/utah_area_limited.png")
    plt.show()

def run_algo(ds_january, ds_october, extents, grid):
    disc_f = pyscan.RKULLDORF
    print('Running algorithm...')
    subgrid = pyscan.max_subgrid_convex(grid, .0001, disc_f)
    
    col0, col1, row0, row1 = subgrid.lowCol(), subgrid.upCol(), subgrid.lowRow(), subgrid.upRow()
    width = col1 - col0 + 1
    height = row1 - row0 + 1
    fvalue = subgrid.fValue()

    rect = grid.toRectangle(subgrid)
    rect2 = rect

    xB, xU, yB, yU = rect.lowX(), rect.upX(), rect.lowY(), rect.upY()
    # Rect size in number of cells
    rect_size_area = width * height
    print(f'Fvalue: {fvalue}')
    print(f'Width: {width} cells, Height: {height} cells')
    print(f'Area: {rect_size_area} cells')
    print(f'Rectangle: ({col0}, {col1}), ({row0}, {row1})')
    
    plot_result(ds_january.value.values, ds_october.value.values, extents, rect, rect2)
    print('done')


# t0 = time.time()
# grid0 = xr_to_grid0(ds_october, ds_january)
# t1 = time.time()
# print_grid_info(grid0, ds_october, ds_january)
# print(f'Grid 0 (Exact) took {t1 - t0:.2f} seconds')

def test_grid(grid, ds_october, ds_january):

    m_arr = ds_october.value.values
    m_arr = m_arr / np.nansum(m_arr)
    b_arr = ds_january.value.values
    b_arr = b_arr / np.nansum(b_arr)
    m_arr0, b_arr0 = grid_to_np(grid)
    
    # b_arr0[np.isnan(b_arr)] = np.nan

    min_val = np.min([np.nanmin(m_arr), np.nanmin(b_arr), np.nanmin(m_arr0), np.nanmin(b_arr0)])
    max_val = np.max([np.nanmax(m_arr), np.nanmax(b_arr), np.nanmax(m_arr0), np.nanmax(b_arr0)])
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    sns.heatmap(m_arr, ax=ax[0], cmap='coolwarm', cbar=False, xticklabels=10, yticklabels=10,
                 vmin=min_val, vmax=max_val)
    ax[0].set_title('Original')
    sns.heatmap(m_arr0, ax=ax[1], cmap='coolwarm', cbar=False, xticklabels=10, yticklabels=10,
                 vmin=min_val, vmax=max_val)
    ax[1].set_title('Recovered')
    plt.show()

    # assert np.allclose(m_arr, m_arr0)
    # assert np.allclose(b_arr, b_arr0)


t0 = time.time()
grid1 = xr_to_grid1(ds_october, ds_january)
t1 = time.time()
print_grid_info(grid1, ds_october, ds_january)
print(f'Grid 1 (Net) took {t1 - t0:.2f} seconds')
# run_algo(ds_january, ds_october, extents, grid1)
test_grid(grid1, ds_october, ds_january)

# t0 = time.time()
# grid2 = xr_to_grid2(ds_october, ds_january)
# t1 = time.time()
# print_grid_info(grid2, ds_october, ds_january)
# print(f'Grid 2 (Resolution) took {t1 - t0:.2f} seconds')
# # run_algo(ds_january, ds_october, extents, grid2)
# test_grid(grid2, ds_october, ds_january)

t0 = time.time()
grid3 = xr_to_grid3(ds_october, ds_january)
t1 = time.time()
print_grid_info(grid3, ds_october, ds_january)
print(f'Grid 3 (Numpy) took {t1 - t0:.2f} seconds')
# run_algo(ds_january, ds_october, extents, grid3)
test_grid(grid3, ds_october, ds_january)

print('done')