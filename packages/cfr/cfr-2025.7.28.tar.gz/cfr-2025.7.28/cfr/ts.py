import os
import xarray as xr
import numpy as np
import cftime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.stats import pearsonr
import copy
from . import utils
from .utils import (
    coefficient_efficiency,
    p_header,
    p_hint,
    p_success,
    p_fail,
    p_warning,
)

class EnsTS:
    ''' The class for ensemble timeseries

    The ensembles variable should be in shape of (nt, nEns), where nt is the number of years,
    and nEns is the number of ensemble members.

    Args:
        time (numpy.array): the time axis of the series
        value (numpy.array): the value axis of the series
        value_name (str): the name of value axis; will be used as ylabel in plots

    Attributes:
        nt (int): the size of the time axis
        nEns (int): the size of the ensemble
        median (numpy.array): the median of the ensemble timeseries

    '''
    def __init__(self, time=None, value=None, value_name=None):
        if np.ndim(value) == 1:
            value = value[:, np.newaxis]

        if time is not None:
            try:
                time = [np.datetime64(t) for t in time]
            except:
                pass

            try:
                time = utils.datetime2year_float(time)
            except:
                pass

        self.time = time
        self.value = value
        self.value_name = value_name

        if self.value is not None:
            self.refresh()

    def annualize(self, months=list(range(1, 13)), verbose=False):
        new = self.copy()
        new.value = []
        for val in self.value.T:
            try:
                new.time, val_ann = utils.annualize(self.time, val, months=months)
            except:
                new.time, val_ann = utils.annualize(self.time, val, months=list(range(1, 13)))
                if verbose: p_warning(f'Record {self.pid} cannot be annualized with months {months}. Use calendar year instead.')

            new.time, val_ann = utils.clean_ts(new.time, val_ann)
            new.value.append(val_ann)
        
        new.value = np.array(new.value).T
        new.refresh()
        return new

    def fetch(self, name=None, **from_df_kws):
        ''' Fetch a proxy database from cloud

        Args:
            name (str): a predifined database name or an URL starting with "http" 
        '''
        url_dict = utils.ensts_url_dict

        if name is None:
            p_warning(f'>>> Choose one from the supported databases:')
            for k in url_dict.keys():
                p_warning(f'- {k}')
            return None

        if name in url_dict:
            url = url_dict[name]
        else:
            url = name

        read_func = {
            '.json': pd.read_json,
            '.csv': pd.read_csv,
            '.pkl': pd.read_pickle,
        }
        ext = os.path.splitext(url)[-1].lower()
        if ext in read_func:
            # cloud & local
            df = read_func[ext](url)
            ensts = self.from_df(df, **from_df_kws)
        else:
            raise ValueError('Wrong file extention based on the given URL!')

        return ensts

    def refresh(self):
        self.nt = np.shape(self.value)[0]
        self.nEns = np.shape(self.value)[1]
        self.median = np.nanmedian(self.value, axis=1)
        self.mean = np.nanmean(self.value, axis=1)
        self.std = np.nanstd(self.value, axis=1)

    def get_mean(self):
        res = self.copy() # copy object to get metadata
        res.value = self.mean[:, np.newaxis]
        res.refresh()
        return res

    def get_median(self):
        res = self.copy() # copy object to get metadata
        res.value = self.median[:, np.newaxis]
        res.refresh()
        return res

    def get_std(self):
        res = self.copy() # copy object to get metadata
        res.value = self.std[:, np.newaxis]
        res.refresh()
        return res

    def from_df(self, df, time_column='time', value_columns=None):
        ''' Load data from a pandas.DataFrame

        Parameters
        ----------
        df : pandas.DataFrame
            The pandas.DataFrame object.

        time_column : str
            The label of the column for the time axis.

        value_columns : list of str
            The list of the labels for the value axis of the ensemble members.

        '''
        if value_columns is None:
            value_columns = list(set(df.columns) - {time_column})
            
        arr = df[value_columns].values
        time = df[time_column].values
        nt = len(time)
        value = np.reshape(arr, (nt, -1))

        ens = EnsTS(time=time, value=value)
        return ens

    def to_df(self, time_column=None, value_column='ens'):
        ''' Convert an EnsTS to a pandas.DataFrame

        Parameters
        ----------
        time_column : str
            The label of the column for the time axis.

        value_column : str
            The base column label for the ensemble members.
            By default, the columns for the members will be labeled as "ens.0", "ens.1", "ens.2", etc.

        '''
        time_column = 'time' if time_column is None else time_column
        data_dict = {}
        data_dict[time_column] = self.time
        nt, nEns = np.shape(self.value)
        for i in range(nEns):
            data_dict[f'{value_column}.{i}'] = self.value[:, i]

        df = pd.DataFrame(data_dict)
        return df

    def __getitem__(self, key):
        ''' This makes the object subscriptable. '''
        new = self.copy()
        new.value = new.value[key]
        if type(key) is tuple:
            new.time = new.time[key[0]]
        else:
            new.time = new.time[key]

        new.refresh()
        return new

    def __add__(self, series):
        ''' Add a series to the ensembles.

        Parameters
        ----------
        series : int, float, array, EnsTS
            A series to be added to the value field of each ensemble member.
            Can be a constant int/float value, an array, or another EnsTS object with only one member.
            If it's an EnsembleTS that has multiple members, the median will be used as the series.

        '''
        new = self.copy()
        if isinstance(series, EnsTS):
            series = series.median

        if np.ndim(series) > 0:
            series = np.array(series)[:, np.newaxis]

        new.value += series
        new.refresh()
        return new

    def __sub__(self, series):
        ''' Substract a series from the ensembles.

        Parameters
        ----------
        series : int, float, array, EnsTS
            A series to be substracted from the value field of each ensemble member.
            Can be a constant int/float value, an array, or another EnsTS object with only one member.
            If it's an EnsembleTS that has multiple members, the median will be used as the series.
        '''
        new = self.copy()
        if isinstance(series, EnsTS):
            series = series.median

        if np.ndim(series) > 0:
            series = np.array(series)[:, np.newaxis]

        new.value -= series
        new.refresh()
        return new

    def __mul__(self, series):
        ''' Element-wise multiplication. The multiplier should have the same length as self.nt.

        Parameters
        ----------
        series : int, float, array, EnsTS
            A series to be element-wise multiplied by for the value field of each ensemble member.
            Can be a constant int/float value, an array, or another EnsTS object with only one member.
            If it's an EnsembleTS that has multiple members, the median will be used as the series.
        '''
        new = self.copy()
        if isinstance(series, EnsTS):
            series = series.median

        if np.ndim(series) > 0:
            for i in range(self.nt):
                new.value[i] *= series[i]
        else:
            new.value *= series

        new.refresh()
        return new

    def __truediv__(self, series):
        ''' Element-wise division. The divider should have the same length as self.nt.

        Parameters
        ----------
        series : int, float, array, EnsTS
            A series to be element-wise divided by for the value field of each ensemble member.
            Can be a constant int/float value, an array, or another EnsTS object with only one member.
            If it's an EnsembleTS that has multiple members, the median will be used as the series.
        '''
        new = self.copy()
        if isinstance(series, EnsTS):
            series = series.median

        if np.ndim(series) > 0:
            for i in range(self.nt):
                new.value[i] /= series[i]
        else:
            new.value /= series

        new.refresh()
        return new

    def copy(self):
        ''' Make a deepcopy of the object. '''
        return copy.deepcopy(self)

    def plot(self, figsize=[12, 4], color='indianred',
        xlabel='Year (CE)', ylabel=None, title=None, ylim=None, xlim=None,
        lgd_kws=None, title_kws=None, plot_valid=True, ax=None, **plot_kws):
        ''' Plot the raw values (multiple series).

        Args:
            plot_valid (bool, optional): If True, will plot the validation target series if existed. Defaults to True.
        '''

        lgd_kws = {} if lgd_kws is None else lgd_kws
        title_kws = {} if title_kws is None else title_kws

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        ax.margins(0)
        # plot timeseries
        _plot_kwargs = {'linewidth': 1}
        if 'label' not in plot_kws:
            plot_kws['label'] = self.value_name
        _plot_kwargs.update(plot_kws)

        ax.plot(self.time, self.value, color=color, **_plot_kwargs)
        ax.set_xlabel(xlabel)
        if ylabel is None: ylabel = self.value_name
        ax.set_ylabel(ylabel)

        if plot_valid and hasattr(self, 'valid_stats'):
            lb = f'{self.ref_name}'
            s =  ' ('
            for k, v in self.valid_stats.items():
                if k == 'corr':
                    s += fr'$r$={v:.2f}, '
                elif k == 'R2':
                    s += fr'$R^2$={v:.2f}, '
                elif k == 'CE':
                    s += fr'$CE$={v:.2f}, '
            s = s[:-2]
            s += ')'
            lb += s

            ax.plot(self.ref_time, self.ref_value, label=lb, color='k')

        if xlim is not None:
            ax.set_xlim(xlim)

        if ylim is not None:
            ax.set_ylim(ylim)

        if self.value_name is not None:
            _legend_kwargs = {'ncol': 2, 'loc': 'upper left'}
            _legend_kwargs.update(lgd_kws)
            ax.legend(**_legend_kwargs)

        if title is not None:
            _title_kwargs = {'fontweight': 'bold'}
            _title_kwargs.update(title_kws)
            ax.set_title(title, **_title_kwargs)

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def line_density(self, figsize=[12, 4], cmap='plasma', color_scale='linear', bins=None, num_fine=None,
        xlabel='Year (CE)', ylabel=None, title=None, ylim=None, xlim=None, 
        title_kws=None, ax=None, **pcolormesh_kwargs,):
        ''' Plot the timeseries 2-D histogram

        Args:
            cmap (str): The colormap for the histogram.
            color_scale (str): The scale of the colorbar; should be either 'linear' or 'log'.
            bins (list or tuple): The number of bins for each axis: nx, ny = bins.

        Referneces:
            https://matplotlib.org/3.5.0/gallery/statistics/time_series_histogram.html

        '''
        pcolormesh_kwargs = {} if pcolormesh_kwargs is None else pcolormesh_kwargs

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        if num_fine is None:
            num_fine = np.min([self.nt*8, 1000])

        num_series = self.nEns
        x = self.time
        Y = self.value.T
        x_fine = np.linspace(x.min(), x.max(), num_fine)
        y_fine = np.empty((num_series, num_fine), dtype=float)
        for i in range(num_series):
            y_fine[i, :] = np.interp(x_fine, x, Y[i, :])
        y_fine = y_fine.flatten()
        x_fine = np.tile(x_fine, [num_series, 1]).flatten()

        if bins is None:
            bins = [num_fine//2, num_series//10]

        h, xedges, yedges = np.histogram2d(x_fine, y_fine, bins=bins)
        h = h / h.max()  # normalize

        pcm_kwargs = {}
        # if 'vmax' in pcolormesh_kwargs:
        #     vmax = pcolormesh_kwargs['vmax']
        #     pcolormesh_kwargs.pop('vmax')
        # else:
        #     vmax = np.max(h) // 2
        vmax = 1

        if color_scale == 'log':
            pcm_kwargs['norm'] = LogNorm(vmax=vmax)
        elif color_scale == 'linear':
            pcm_kwargs['vmax'] = vmax
        else:
            raise ValueError('Wrong `color_scale`; should be either "log" or "linear".')

        pcm_kwargs.update(pcolormesh_kwargs)

        ax.set_xlabel(xlabel)
        if ylabel is None: ylabel = self.value_name
        ax.set_ylabel(ylabel)

        if xlim is not None:
            ax.set_xlim(xlim)

        if ylim is not None:
            ax.set_ylim(ylim)

        cmap = copy.copy(plt.cm.__dict__[cmap])
        cmap.set_bad(cmap(0))
        pcm = ax.pcolormesh(xedges, yedges, h.T, cmap=cmap, rasterized=True, **pcm_kwargs)

        fig.colorbar(pcm, ax=ax, label='Density', pad=0)

        if title is not None:
            _title_kwargs = {'fontweight': 'bold'}
            _title_kwargs.update(title_kws)
            ax.set_title(title, **_title_kwargs)
        
        return fig, ax
            

    def plot_qs(self, figsize=[12, 4], qs=[0.025, 0.25, 0.5, 0.75, 0.975], color='indianred',
        xlabel='Year (CE)', ylabel=None, title=None, ylim=None, xlim=None, alphas=[0.5, 0.1],
        lgd_kws=None, title_kws=None, ax=None, plot_valid=True, **plot_kws):
        ''' Plot the quantiles

        Args:
            figsize (list, optional): The size of the figure. Defaults to [12, 4].
            qs (list, optional): The list to denote the quantiles plotted. Defaults to [0.025, 0.25, 0.5, 0.75, 0.975].
            color (str, optional): The basic color for the quantile envelopes. Defaults to 'indianred'.
            xlabel (str, optional): The label for the x-axis. Defaults to 'Year (CE)'.
            ylabel (str, optional): The label for the y-axis. Defaults to None.
            title (str, optional): The title of the figure. Defaults to None.
            ylim (tuple or list, optional): The limit of the y-axis. Defaults to None.
            xlim (tuple or list, optional): The limit of the x-axis. Defaults to None.
            alphas (list, optional): The alphas for the quantile envelopes. Defaults to [0.5, 0.1].
            lgd_kws (dict, optional): The keyward arguments for the `ax.legend()` function. Defaults to None.
            title_kws (dict, optional): The keyward arguments for the `ax.title()` function. Defaults to None.
            ax (matplotlib.axes, optional): The `matplotlib.axes` object. If set the image will be plotted in the existing `ax`. Defaults to None.
            plot_valid (bool, optional): If True, will plot the validation target series if existed. Defaults to True.
            **kwargs (dict, optional): The keyward arguments for the `ax.plot()` function. Defaults to None.
        '''

        lgd_kws = {} if lgd_kws is None else lgd_kws
        title_kws = {} if title_kws is None else title_kws

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        ax.margins(0)

        # calculate quantiles
        ts_qs = np.quantile(self.value, qs, axis=-1)
        nqs = len(qs)
        idx_mid = int(np.floor(nqs/2))

        if qs[idx_mid] == 0.5:
            label_mid = 'median'
        else:
            label_mid = f'{qs[2]*100}%'

        # plot timeseries
        _plot_kwargs = {'linewidth': 1}
        _plot_kwargs.update(**plot_kws)

        ax.plot(self.time, ts_qs[idx_mid], label=label_mid, color=color, **_plot_kwargs)
        for i, alpha in zip(range(idx_mid), alphas[::-1]):
            ax.fill_between(self.time, ts_qs[-(i+1)], ts_qs[i], color=color, alpha=alpha, label=f'{qs[i]*100}% to {qs[-(i+1)]*100}%')

        if plot_valid and hasattr(self, 'valid_stats'):
            lb = f'{self.ref_name}'
            s =  ' ('
            for k, v in self.valid_stats.items():
                if k == 'corr':
                    s += fr'$r$={v:.2f}, '
                elif k == 'R2':
                    s += fr'$R^2$={v:.2f}, '
                elif k == 'CE':
                    s += fr'$CE$={v:.2f}, '
            s = s[:-2]
            s += ')'
            lb += s

            ax.plot(self.ref_time, self.ref_value, label=lb, color='k')
            n_ref = 1
        else:
            n_ref = 0

        ax.set_xlabel(xlabel)
        if ylabel is None: ylabel = self.value_name
        ax.set_ylabel(ylabel)

        if xlim is not None:
            ax.set_xlim(xlim)

        if ylim is not None:
            ax.set_ylim(ylim)


        _legend_kwargs = {'ncol': len(qs)//2+1+n_ref, 'loc': 'upper left'}
        _legend_kwargs.update(lgd_kws)
        ax.legend(**_legend_kwargs)

        if title is not None:
            _title_kwargs = {'fontweight': 'bold'}
            _title_kwargs.update(title_kws)
            ax.set_title(title, **_title_kwargs)

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

    def compare(self, ref=None, ref_time=None, ref_value=None, ref_name='reference', stats=['corr', 'CE'], timespan=None):
        ''' Compare against a reference timeseries.

        Args:
            ref (cfr.ts.EnsTS): the reference time series object
            ref_time (numpy.array): the time axis of the reference timeseries
            ref_value (numpy.array): the value axis of the reference timeseries
            stats (list, optional): the list of validation statistics to calculate. Defaults to ['corr', 'CE'].
            timespan (tuple, optional): the time period for validation. Defaults to None.
        '''
        new = self.copy()
        new.valid_stats = {}
        if ref is not None:
            ref_time = ref.time
            ref_value = ref.median
        ref_time = np.array(ref_time)
        ref_value = np.array(ref_value)
        new.ref_name = ref_name

        recon_value = np.array(self.get_median().value)[:, 0]
        recon_time = np.array(self.get_median().time)

        if timespan is None:
            time_min = np.max([np.min(recon_time), np.min(ref_time)])
            time_max = np.min([np.max(recon_time), np.max(ref_time)])
            timespan = [time_min, time_max]

        recon_mask = (recon_time>=timespan[0])&(recon_time<=timespan[1])
        recon_slice = recon_value[recon_mask]

        ref_mask = (ref_time>=timespan[0])&(ref_time<=timespan[1])
        ref_slice = ref_value[ref_mask]
        new.ref_time = ref_time[ref_mask]
        new.ref_value = ref_value[ref_mask]

        if len(recon_slice) != len(ref_slice):
            raise ValueError(f'Inconsistent length of the two timeseries. recon: {len(recon_slice)}; ref: {len(ref_slice)}.')

        for stat in stats:
            if stat == 'corr':
                r, p = pearsonr(recon_slice, ref_slice)
                new.valid_stats['corr'], new.valid_stats['p-value'] = r, p
            elif stat == 'R2':
                r, p = pearsonr(recon_slice, ref_slice)
                new.valid_stats['R2'], new.valid_stats['p-value'] = r**2, p
            elif stat == 'CE':
                new.valid_stats['CE'] = coefficient_efficiency(ref_slice, recon_slice)
            else:
                raise ValueError('Wrong `stat`; should be one of `corr`, `R2`, and `CE`.' )

        return new