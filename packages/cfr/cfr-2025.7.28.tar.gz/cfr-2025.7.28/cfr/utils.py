import xarray as xr
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import cftime
import colorama as ca
import statsmodels.api as sm
import pyresample
import requests
from tqdm import tqdm


def p_header(text):
    # return cprint(text, 'cyan', attrs=['bold'])  # lib: termcolor
    print(ca.Fore.CYAN + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_hint(text):
    # return cprint(text, 'grey', attrs=['bold'])  # lib: termcolor
    print(ca.Fore.LIGHTBLACK_EX + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_success(text):
    # return cprint(text, 'green', attrs=['bold'])  # lib: termcolor
    print(ca.Fore.GREEN + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_fail(text):
    # return cprint(text, 'red', attrs=['bold'])  # lib: termcolor
    print(ca.Fore.RED + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_warning(text):
    # return cprint(text, 'yellow', attrs=['bold'])  # lib: termcolor
    print(ca.Fore.YELLOW + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def make_bin_vector(ts, bin_width=10):
    bin_vector = np.arange(
        bin_width*(np.min(ts)//bin_width),
        bin_width*(np.max(ts)//bin_width+2),
        step=bin_width,
    )

    return bin_vector
    
def smooth_ts(ts, ys, bin_vector=None, bin_width=10):
    if bin_vector is None:
        bin_vector = np.arange(
            bin_width*(np.min(ts)//bin_width),
            bin_width*(np.max(ts)//bin_width+2),
            step=bin_width)

    ts_bin = (bin_vector[1:] + bin_vector[:-1])/2
    n_bin = np.size(ts_bin)
    ys_bin = np.zeros(n_bin)

    for i in range(n_bin):
        t_start = bin_vector[i]
        t_end = bin_vector[i+1]
        t_range = (ts >= t_start) & (ts < t_end)
        if np.sum(t_range*1) == 1:
            ys_bin[i] = ys[t_range]
        else:
            ys_bin[i] = np.average(ys[t_range], axis=0)

    return ts_bin, ys_bin, bin_vector

def bin_ts(ts, ys, bin_vector=None, bin_width=10, resolution=1, smoothed=False):
    if not smoothed:
        ts_smooth, ys_smooth, bin_vector = smooth_ts(ts, ys, bin_vector=bin_vector, bin_width=bin_width)
    else:
        ts_smooth, ys_smooth = ts, ys

    bin_vector_finer = np.arange(np.min(bin_vector), np.max(bin_vector)+1, step=resolution)
    bin_value = np.zeros(bin_vector_finer.size)

    n_bin = np.size(ts_smooth)
    for i in range(n_bin):
        t_start = bin_vector[i]
        t_end = bin_vector[i+1]
        t_range = (bin_vector_finer >= t_start) & (bin_vector_finer <= t_end)
        bin_value[t_range] = ys_smooth[i]

    return bin_vector_finer, bin_value

def bootstrap(samples, n_bootstraps=1000, stat_func=np.nanmean):

    n_samples = np.shape(samples)[0]
    stats = np.zeros(n_bootstraps)
    for i in range(n_bootstraps):
        rand_ind = np.random.randint(n_samples, size=n_samples)
        stats[i] = stat_func(samples[rand_ind])

    return stats

def clean_ts(ts, ys):
    ''' Delete the NaNs in the time series and sort it with time axis ascending

    Parameters
    ----------
    ts : array
        The time axis of the time series, NaNs allowed
    ys : array
        A time series, NaNs allowed

    Returns
    -------
    ts : array
        The time axis of the time series without NaNs
    ys : array
        The time series without NaNs
    '''
    ys = np.array(ys, dtype=float)
    ts = np.array(ts, dtype=float)
    assert ys.size == ts.size, 'The size of time axis and data value should be equal!'

    ys_tmp = np.copy(ys)
    ys = ys[~np.isnan(ys_tmp)]
    ts = ts[~np.isnan(ys_tmp)]
    ts_tmp = np.copy(ts)
    ys = ys[~np.isnan(ts_tmp)]
    ts = ts[~np.isnan(ts_tmp)]

    # sort the time series so that the time axis will be ascending
    sort_ind = np.argsort(ts)
    ys = ys[sort_ind]
    ts = ts[sort_ind]

    # handle duplicated time points
    t_count = {}
    value_at_t = {}
    for i, t in enumerate(ts):
        if t not in t_count:
            t_count[t] = 1
            value_at_t[t] = ys[i]
        else:
            t_count[t] += 1
            value_at_t[t] += ys[i]

    ys = []
    ts = []
    for t, v in value_at_t.items():
        ys.append(v / t_count[t])
        ts.append(t)

    ts = np.array(ts)
    ys = np.array(ys)

    return ts, ys


def overlap_ts(ts_proxy, ys_proxy, ts_obs, ys_obs):
    ys_proxy = np.array(ys_proxy, dtype=float)
    ts_proxy = np.array(ts_proxy, dtype=float)
    ys_obs = np.array(ys_obs, dtype=float)
    ts_obs = np.array(ts_obs, dtype=float)

    overlap_proxy = (ts_proxy >= np.min(ts_obs)) & (ts_proxy <= np.max(ts_obs))
    overlap_obs = (ts_obs >= np.min(ts_proxy)) & (ts_obs <= np.max(ts_proxy))

    ys_proxy_overlap, ts_proxy_overlap = ys_proxy[overlap_proxy], ts_proxy[overlap_proxy]
    ys_obs_overlap, ts_obs_overlap = ys_obs[overlap_obs], ts_obs[overlap_obs]

    time_overlap = np.intersect1d(ts_proxy_overlap, ts_obs_overlap)
    ind_proxy = list(i for i, t in enumerate(ts_proxy_overlap) if t in time_overlap)
    ind_obs = list(i for i, t in enumerate(ts_obs_overlap) if t in time_overlap)
    ys_proxy_overlap = ys_proxy_overlap[ind_proxy]
    ys_obs_overlap = ys_obs_overlap[ind_obs]

    return time_overlap, ys_proxy_overlap, ys_obs_overlap

def ols_ts(ts_proxy, ys_proxy, ts_obs, ys_obs):
    ys_proxy = np.array(ys_proxy, dtype=float)
    ts_proxy = np.array(ts_proxy, dtype=float)
    ys_obs = np.array(ys_obs, dtype=float)
    ts_obs = np.array(ts_obs, dtype=float)

    time_overlap, ys_proxy_overlap, ys_obs_overlap = overlap_ts(ts_proxy, ys_proxy, ts_obs, ys_obs)

    # calculate the linear regression
    X = sm.add_constant(ys_proxy_overlap)
    ols_model = sm.OLS(ys_obs_overlap, X, missing='drop')

    return ols_model


def gcd(lat1, lon1, lat2, lon2):
	'''
	Calculate the great circle distance between two points
	on the earth (specified in decimal degrees)

	Parameters:
	-----------
	lat1: float
		Latitude of first location (degrees)
	lon1: float
		Longitude of first location (degrees)
	lat2: float
		Latitude of second location (degrees)
	lon2: float
		Longitude of second location (degrees)
		
	Returns:
	--------
	km: float
		Great circle distance between the two locations (in kilometers)
	'''
	# convert decimal degrees to radians
	lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

	# haversine formula
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
	c = 2 * np.arcsin(np.sqrt(a))

	# 6367 km is the radius of the Earth
	km = 6367 * c
	return km

def annualize(time=None, value=None, da=None, months=None):
    # convert negative months to support expressions like [-12, 1, 2]
    months = list(range(1, 13)) if months is None else np.abs(months)

    if da is None:
        dates = year_float2datetime(time)
        da_wk = xr.DataArray(
            value, dims=['time'], coords={'time': dates}
        )
    else:
        da_wk = da

    # sda = da_wk.sel(time=da_wk.time.dt.month.isin(months))
    sda = da_wk.sel(time=da_wk['time.month'].isin(months))
    anchor = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    idx = months[-1]-1
    sda_ann = sda.resample(time=f'A-{anchor[idx]}').mean()
    time_ann = np.floor(datetime2year_float(sda_ann.time.values))
    value_ann = sda_ann.values

    if da is None:
        return time_ann, value_ann
    else:
        return sda_ann

def annualize_var(year_float, var, resolution='month', weights=None):
    ''' Annualize a variable array
    Args:
        var (ndarray): the target variable array with 1st dim to be year
        year_float (1-D array): the time axis of the variable array
        weights (ndarray): the weights that shares the same shape of the target variable array
    Returns:
        var_ann (ndarray): the annualized variable array
        year_ann (1-D array): the time axis of the annualized variable array
    '''
    var = np.array(var)
    year_float = np.array(year_float)

    ndims = len(np.shape(var))
    dims = ['time']
    for i in range(ndims-1):
        dims.append(f'dim{i+1}')

    time = year_float2datetime(year_float, resolution=resolution)

    if weights is not None:
        weights_da = xr.DataArray(weights, dims=dims, coords={'time': time})

        coeff = np.ndarray(np.shape(weights))
        for i, gp in enumerate(list(weights_da.groupby('time.year'))):
            year, value = gp
            k = np.shape(value)[0]
            coeff[k*i:k*(i+1)] = value / np.sum(value, axis=0)

        del weights, weights_da  # save the memory

        var = np.multiply(coeff, var)
        var_da = xr.DataArray(var, dims=dims, coords={'time': time})
        var_ann = var_da.groupby('time.year').sum('time')

    else:
        var_da = xr.DataArray(var, dims=dims, coords={'time': time})
        var_ann = var_da.groupby('time.year').mean('time')

    var_ann = var_ann.values

    year_ann = np.sort(list(set([t.year for t in time])))
    return year_ann, var_ann

def ymd2year_float(year, month, day, resolution='month'):
    ''' Convert a set of (year, month, day) to an array of floats in unit of year
    '''
    year_float = []
    for y, m, d in zip(year, month, day):
        if resolution == 'month': d = 1
        date = datetime(year=y, month=m, day=d)
        fst_day = datetime(year=y, month=1, day=1)
        lst_day = datetime(year=y+1, month=1, day=1)
        year_part = date - fst_day
        year_length = lst_day - fst_day
        year_float.append(y + year_part/year_length)

    year_float = np.array(year_float)
    return year_float

def datetime2year_float(date, resolution='month'):
    ''' Convert a list of dates to floats in year
    '''
    if isinstance(date[0], np.datetime64):
        date = pd.to_datetime(date)

    year = [d.year for d in date]
    month = [d.month for d in date]
    day = [d.day for d in date]
    if resolution == 'month': day = np.ones(np.size(day))

    year_float = ymd2year_float(year, month, day, resolution)

    return year_float

def year_float2datetime(year_float, resolution='month'):
    ''' Convert an array of floats in unit of year to a datetime time; accuracy: one day
    '''
    # if np.min(year_float) < 0:
    #     raise ValueError('Cannot handel negative years. Please truncate first.')

    year = np.array([int(y) for y in year_float], dtype=int)
    month = np.zeros(np.size(year), dtype=int)
    day = np.zeros(np.size(year), dtype=int)

    for i, y in enumerate(year):
        fst_day = datetime(year=y, month=1, day=1)
        lst_day = datetime(year=y+1, month=1, day=1)
        year_length = lst_day - fst_day

        year_part = (year_float[i] - y)*year_length + timedelta(minutes=1)  # to fix the numerical error
        date = year_part + fst_day
        month[i] = date.month
        day[i] = date.day

    if resolution == 'day':
        time = [cftime.datetime(y, m, d, 0, 0, 0, 0, 0, 0, calendar='standard') for y, m, d in zip(year, month, day)]
    elif resolution == 'month':
        time = [cftime.datetime(y, m, 1, 0, 0, 0, 0, 0, 0, calendar='standard') for y, m in zip(year, month)]

    return time

def year_float2dates(year_float):
    ''' Convert an array of floats in unit of year to a datetime time; accuracy: one day
    '''
    # if np.min(year_float) < 0:
    #     raise ValueError('Cannot handel negative years. Please truncate first.')

    year = np.array([int(y) for y in year_float], dtype=int)
    dates = []

    for i, y in enumerate(year):
        fst_day = datetime(year=y, month=1, day=1)
        lst_day = datetime(year=y+1, month=1, day=1)
        year_length = lst_day - fst_day

        year_part = (year_float[i] - y)*year_length + timedelta(minutes=1)  # to fix the numerical error
        date = year_part + fst_day
        dates.append(date)


    return dates

def regrid_field(field, lat, lon, lat_new, lon_new):
    import spharm
    nlat_old, nlon_old = np.size(lat), np.size(lon)
    nlat_new, nlon_new = np.size(lat_new), np.size(lon_new)
    spec_old = spharm.Spharmt(nlon_old, nlat_old, gridtype='regular', legfunc='computed')
    spec_new = spharm.Spharmt(nlon_new, nlat_new, gridtype='regular', legfunc='computed')

    field_new = []
    for field_old in field:
        regridded_field =  spharm.regrid(spec_old, spec_new, field_old, ntrunc=None, smooth=None)
        field_new.append(regridded_field)

    field_new = np.array(field_new)
    return field_new

def regrid_field_curv_rect(field, lat_curv, lon_curv,
        lats=None, lons=None,
        dlat=1, dlon=1, lon_range=None, lat_range=None,
        roi=None, roi_factor=1e6):
    ''' Regrid a curvilinear grid to a linear rectilinear grid

    Args:
        field (np.ndarray): assuming shape in (..., nlat, nlon)

    Note: lon_curv should be in range (-180, 180)!
    '''
    if lons is None:
        if lon_range is not None:
            lons = np.arange(lon_range[0], lon_range[-1]+dlon, dlon)
        else:
            lons = np.arange(np.min(lon_curv), np.max(lon_curv)+dlon, dlon)

    dlon = np.abs(np.median(np.diff(lons)))

    if lats is None:
        if lat_range is not None:
            lats = np.arange(lat_range[0], lat_range[-1]+dlat, dlat)
        else:
            lats = np.arange(np.min(lat_curv), np.max(lat_curv)+dlat, dlat)

    # convert the longitude from (0, 360) to (-180, 180)
    if np.min(lon_curv) >= 0:
        lon_curv = (lon_curv+180) % 360 -180

    lon_rect, lat_rect = np.meshgrid(lons, lats)
    lon_rect = pyresample.utils.wrap_longitudes(lon_rect)

    if roi is None:
        roi = roi_factor * dlon

    old_grid = pyresample.geometry.SwathDefinition(lons=lon_curv, lats=lat_curv)
    new_grid = pyresample.geometry.SwathDefinition(lons=lon_rect, lats=lat_rect)

    fd_shape = field.shape
    field_resh = field.reshape(-1, fd_shape[-2], fd_shape[-1]).transpose(1, 2, 0)
    res = pyresample.kd_tree.resample_nearest(
        old_grid, field_resh, new_grid,
        radius_of_influence=roi,
        fill_value=np.nan,
    )
    rgd_data = res.transpose(2, 0, 1).reshape(*fd_shape[:-2], len(lats), len(lons))

    return rgd_data, lats, lons

def coefficient_efficiency(ref, test, valid=None):
    """ Compute the coefficient of efficiency for a test time series, with respect to a reference time series.

    Args:
        ref (numpy.ndarray):   reference array, of same size as test
        test (numpy.ndarray):  test array
        valid (float): fraction of valid data required to calculate the statistic

    Note:
        Assumes that the first dimension in test and ref arrays is time!!!

    Returns:
        CE (float): CE statistic calculated following Nash & Sutcliffe (1970)
    """

    # check array dimensions
    dims_test = test.shape
    dims_ref  = ref.shape
    # print('dims_test: ', dims_test, ' dims_ref: ', dims_ref)

    if len(dims_ref) == 3:   # 3D: time + 2D spatial
        dims = dims_ref[1:3]
    elif len(dims_ref) == 2: # 2D: time + 1D spatial
        dims = dims_ref[1:2]
    elif len(dims_ref) == 1: # 0D: time series
        dims = 1
    else:
        print('In coefficient_efficiency(): Problem with input array dimension! Exiting...')
        SystemExit(1)

    CE = np.zeros(dims)

    # error
    error = test - ref

    # CE
    numer = np.sum(np.power(error,2),axis=0)
    denom = np.sum(np.power(ref-np.nanmean(ref,axis=0),2),axis=0)
    CE    = 1. - np.divide(numer,denom)

    if valid:
        nbok  = np.sum(np.isfinite(ref),axis=0)
        nball = float(dims_ref[0])
        ratio = np.divide(nbok,nball)
        indok  = np.where(ratio >= valid)
        indbad = np.where(ratio < valid)
        dim_indbad = len(indbad)
        testlist = [indbad[k].size for k in range(dim_indbad)]
        if not all(v == 0 for v in testlist):
            if isinstance(dims,(tuple,list)):
                CE[indbad] = np.nan
            else:
                CE = np.nan

    return CE

def geo_mean(da, lat_min=-90, lat_max=90, lon_min=0, lon_max=360, lat_name='lat', lon_name='lon'):
    ''' Calculate the geographical mean value of the climate field.

    Args:
        lat_min (float): the lower bound of latitude for the calculation.
        lat_max (float): the upper bound of latitude for the calculation.
        lon_min (float): the lower bound of longitude for the calculation.
        lon_max (float): the upper bound of longitude for the calculation.
    '''
    # calculation
    mask_lat = (da[lat_name] >= lat_min) & (da[lat_name] <= lat_max)
    mask_lon = (da[lon_name] >= lon_min) & (da[lon_name] <= lon_max)

    dac = da.sel(
        {
            lat_name: da[lat_name][mask_lat],
            lon_name: da[lon_name][mask_lon],
        }
    )

    wgts = np.cos(np.deg2rad(dac[lat_name]))
    m = dac.weighted(wgts).mean((lon_name, lat_name))
    return m

def colored_noise(alpha, t, f0=None, m=None, seed=None):
    ''' Generate a colored noise timeseries

    Parameters
    ----------
    alpha : float
        exponent of the 1/f^alpha noise
    t : float
        time vector of the generated noise
    f0 : float
        fundamental frequency
    m : int
        maximum number of the waves, which determines the highest frequency of the components in the synthetic noise

    Returns
    -------
    y : array
        the generated 1/f^alpha noise

    References
    ----------
    Eq. (15) in Kirchner, J. W. Aliasing in 1/f(alpha) noise spectra: origins, consequences, and remedies.
        Phys Rev E Stat Nonlin Soft Matter Phys 71, 066110 (2005).
    '''
    n = np.size(t)  # number of time points
    y = np.zeros(n)

    if f0 is None:
        f0 = 1/n  # fundamental frequency
    if m is None:
        m = n//2

    k = np.arange(m) + 1  # wave numbers

    rng = np.random.default_rng(seed)
    theta = rng.random(int(m))*2*np.pi  # random phase
    for j in range(n):
        coeff = (k*f0)**(-alpha/2)
        sin_func = np.sin(2*np.pi*k*f0*t[j] + theta)
        y[j] = np.sum(coeff*sin_func)

    return y

def colored_noise_2regimes(alpha1, alpha2, f_break, t, f0=None, m=None, seed=None):
    ''' Generate a colored noise timeseries with two regimes

    Parameters
    ----------
    alpha1, alpha2 : float
        the exponent of the 1/f^alpha noise
    f_break : float
        the frequency where the scaling breaks
    t : float
        time vector of the generated noise
    f0 : float
        fundamental frequency
    m : int
        maximum number of the waves, which determines the highest frequency of the components in the synthetic noise

    Returns
    -------
    y : array
        the generated 1/f^alpha noise

    References
    ----------
     Eq. (15) in Kirchner, J. W. Aliasing in 1/f(alpha) noise spectra: origins, consequences, and remedies.
         Phys Rev E Stat Nonlin Soft Matter Phys 71, 066110 (2005).
    '''
    n = np.size(t)  # number of time points
    y = np.zeros(n)

    if f0 is None:
        f0 = 1/n  # fundamental frequency
    if m is None:
        m = n//2  # so the aliasing is limited

    k = np.arange(m) + 1  # wave numbers

    if seed is not None:
        np.random.seed(seed)

    theta = np.random.rand(int(m))*2*np.pi  # random phase

    f_vec = k*f0
    regime1= k*f0>=f_break
    regime2= k*f0<=f_break
    f_vec1 = f_vec[regime1]
    f_vec2 = f_vec[regime2]
    s = np.exp(alpha1/alpha2*np.log(f_vec1[0])) / f_vec2[-1]

    for j in range(n):
        coeff = np.ndarray((np.size(f_vec)))
        coeff[regime1] = f_vec1**(-alpha1/2)
        coeff[regime2] = (s*f_vec2)**(-alpha2/2)
        sin_func = np.sin(2*np.pi*k*f0*t[j] + theta)
        y[j] = np.sum(coeff*sin_func)

    return y

def arr_str2np(arr):
    arr =  np.array([float(s) for s in arr[1:-1].split(',')])
    return arr

def is_numeric(obj):
    attrs = ['__add__', '__sub__', '__mul__', '__truediv__', '__pow__']
    return all(hasattr(obj, attr) for attr in attrs)

def replace_str(fpath, d):
    ''' Replace the string in a given text file according
    to the dictionary `d`
    '''
    with open(fpath, 'r') as f:
        text = f.read()
        for k, v in d.items():
            search_text = k
            replace_text = v
            text = text.replace(search_text, replace_text)

    with open(fpath, 'w') as f:
        f.write(text)


def download(url: str, fname: str, chunk_size=1024, show_bar=True, verify=False):
    resp = requests.get(url, stream=True, verify=verify)
    total = int(resp.headers.get('content-length', 0))
    if show_bar:
        with open(fname, 'wb') as file, tqdm(
            desc='Fetching data',
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in resp.iter_content(chunk_size=chunk_size):
                size = file.write(data)
                bar.update(size)
    else:
        with open(fname, 'wb') as file:
            for data in resp.iter_content(chunk_size=chunk_size):
                size = file.write(data)

proxydb_url_dict = {
    'PAGES2kv2': 'https://github.com/fzhu2e/cfr-data/raw/main/pages2kv2.json',
    'pseudoPAGES2k/ppwn_SNRinf_rta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNRinf_rta.nc',
    'pseudoPAGES2k/ppwn_SNR10_rta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNR10_rta.nc',
    'pseudoPAGES2k/ppwn_SNR2_rta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNR2_rta.nc',
    'pseudoPAGES2k/ppwn_SNR1_rta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNR1_rta.nc',
    'pseudoPAGES2k/ppwn_SNR0.5_rta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNR0.5_rta.nc',
    'pseudoPAGES2k/ppwn_SNR0.25_rta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNR0.25_rta.nc',
    'pseudoPAGES2k/ppwn_SNRinf_fta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNRinf_fta.nc',
    'pseudoPAGES2k/ppwn_SNR10_fta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNR10_fta.nc',
    'pseudoPAGES2k/ppwn_SNR2_fta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNR2_fta.nc',
    'pseudoPAGES2k/ppwn_SNR1_fta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNR1_fta.nc',
    'pseudoPAGES2k/ppwn_SNR0.5_fta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNR0.5_fta.nc',
    'pseudoPAGES2k/ppwn_SNR0.25_fta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/ppwn_SNR0.25_fta.nc',
    'pseudoPAGES2k/tpwn_SNR10_rta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/tpwn_SNR10_rta.nc',
    'pseudoPAGES2k/tpwn_SNR2_rta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/tpwn_SNR2_rta.nc',
    'pseudoPAGES2k/tpwn_SNR1_rta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/tpwn_SNR1_rta.nc',
    'pseudoPAGES2k/tpwn_SNR0.5_rta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/tpwn_SNR0.5_rta.nc',
    'pseudoPAGES2k/tpwn_SNR0.25_rta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/tpwn_SNR0.25_rta.nc',
    'pseudoPAGES2k/tpwn_SNR10_fta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/tpwn_SNR10_fta.nc',
    'pseudoPAGES2k/tpwn_SNR2_fta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/tpwn_SNR2_fta.nc',
    'pseudoPAGES2k/tpwn_SNR1_fta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/tpwn_SNR1_fta.nc',
    'pseudoPAGES2k/tpwn_SNR0.5_fta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/tpwn_SNR0.5_fta.nc',
    'pseudoPAGES2k/tpwn_SNR0.25_fta': 'https://github.com/fzhu2e/paper-pseudoPAGES2k/raw/main/data/tpwn_SNR0.25_fta.nc',
}

climfd_url_dict = {
    'iCESM_past1000historical/tas': 'https://atmos.washington.edu/~rtardif/LMR/prior/tas_sfc_Amon_iCESM_past1000historical_085001-200512.nc',
    'iCESM_past1000historical/pr': 'https://atmos.washington.edu/~rtardif/LMR/prior/pr_sfc_Amon_iCESM_past1000historical_085001-200512.nc',
    'iCESM_past1000historical/d18O': 'https://atmos.washington.edu/~rtardif/LMR/prior/d18O_sfc_Amon_iCESM_past1000historical_085001-200512.nc',
    'iCESM_past1000historical/psl': 'https://atmos.washington.edu/~rtardif/LMR/prior/psl_sfc_Amon_iCESM_past1000historical_085001-200512.nc',
    'iCESM_past1000/tas': 'https://atmos.washington.edu/~rtardif/LMR/prior/tas_sfc_Amon_iCESM_past1000_085001-184912.nc',
    'iCESM_past1000/pr': 'https://atmos.washington.edu/~rtardif/LMR/prior/pr_sfc_Amon_iCESM_past1000_085001-184912.nc',
    'iCESM_past1000/d18O': 'https://atmos.washington.edu/~rtardif/LMR/prior/d18O_sfc_Amon_iCESM_past1000_085001-184912.nc',
    'iCESM_past1000/psl': 'https://atmos.washington.edu/~rtardif/LMR/prior/psl_sfc_Amon_iCESM_past1000_085001-184912.nc',
    'gistemp1200_ERSSTv4': 'https://github.com/fzhu2e/cfr-data/raw/main/gistemp1200_ERSSTv4.nc.gz',
    'gistemp1200_GHCNv4_ERSSTv5': 'https://data.giss.nasa.gov/pub/gistemp/gistemp1200_GHCNv4_ERSSTv5.nc.gz',
    'CRUTSv4.07/tas': 'https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.07/cruts.2304141047.v4.07/tmp/cru_ts4.07.1901.2022.tmp.dat.nc.gz',
    'CRUTSv4.07/pr': 'https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.07/cruts.2304141047.v4.07/pre/cru_ts4.07.1901.2022.pre.dat.nc.gz',
    '20CRv3/tas': 'https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/Monthlies/2mSI-MO/air.2m.mon.mean.nc',
    '20CRv3/pr': 'https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/Monthlies/sfcSI-MO/prate.mon.mean.nc',
    'HadCRUTv5': 'https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/analysis/HadCRUT.5.0.1.0.analysis.anomalies.ensemble_mean.nc',
    'HadCRUT4.6_GraphEM': 'https://github.com/fzhu2e/cfr-data/raw/main/HadCRUT4.6_GraphEM_median.nc',
    'GPCCv2020': 'https://downloads.psl.noaa.gov//Datasets/gpcc/monitor/precip.monitor.mon.total.1x1.v2020.nc',
}

ensts_url_dict = {
    'BC09_NINO34': 'https://github.com/fzhu2e/cfr-data/raw/main/BC09_NINO34.csv',
}
