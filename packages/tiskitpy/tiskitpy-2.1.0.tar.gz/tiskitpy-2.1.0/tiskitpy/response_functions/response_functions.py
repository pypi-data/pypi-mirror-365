# Copyright 2021 Wayne Crawford
import fnmatch  # Allows Unix filename pattern matching
import copy

import numpy as np
import xarray as xr
from matplotlib import pyplot as plt

from ..spectral_density import SpectralDensity   # Only imported to check that input is a SpectralDensity function
# from ..utils import match_one_str, coherence_significance_level
import tiskitpy.utils as baseutils
from tiskitpy.logger import init_logger

logger = init_logger()
np.seterr(all="ignore")


class ResponseFunctions(object):
    """
    Class of Frequency Response Functions for a given input channel.

    From Bendat & Piersol, chapter 6.  The frequency response function is
    the relation between coherent parts of the signal: if the measured
    input :math:`x(t) = u(t) + m(t)` and the measured output
    :math:`y(t) = v(t) + n(t)`, where :math:`u(t)` and :math:`v(t)` are
    coherent and :math:`m(t)` and :math:`n(t)` are not, then the
    frequency response function :math:`H(f)` is such that
    :math:`v(t) = H(f)*u(t)`.
    As to spectra, :math:`G_vv(f) = abs(H(f))^2 * G_uu(f)`
    
    The input and output channel_ids should be tikitpy_ids (seed_codes +
    cleaned_sequence info)

    Args:
        sdf (:class:`.SpectralDensity`): Spectral density functions objet
        in_id (str): input channel id.  Can use Unix wildcards ('*', '?') but
            will return error if more than one string matches
        out_ids (list of str): output channel ids  (None => all but
            in_id)
        noise_channel (str): 'input', 'output', 'equal', 'unknown'
        n_to_reject (int): number of neighboring frequencies for which the
            coherence must be above the 95% significance level in order
            to calculate frequency response function (other values are set to
            0, n_to_reject=0 means use all frequencies)
        min_freq (float or None): Return zero for frequencies below
            this value
        max_freq (float or None): Return zero for frequencies above
            this value
        quiet (bool): don't warn if creating a test object
        show_progress (bool): plot response functions and coherences
    """
    def __init__(self, sdf, in_id, out_ids=None, noise_channel="output",
                 n_to_reject=3, min_freq=None, max_freq=None,
                 quiet=False, show_progress=False, noise_chan=None):
        """
        Attributes:
            _ds (:class: XArray.dataset): container for response functions and
                attributes
        """
        # Handle deprecated noise_chan argument
        if noise_chan is not None:
            if not noise_channel == "output":
                logger.warning('ResponseFunctions argument "noise_chan" is obsolete, ignored')
            else:
                logger.warning('ResponseFunctions argument "noise_chan" is deprecated, use "noise_channel"')
                noise_channel = noise_chan

        if sdf is None:
            logger.info("Creating test ResponseFunction object (no data)")
            if out_ids is None:
                raise ValueError("cannot have empty out_ids for test object")
            f = np.array([1])
            dims = ("input", "output", "f")
            shape = (1, len(out_ids), len(f))
            self._ds = xr.Dataset(
                data_vars={
                    "value": (dims, np.zeros(shape, dtype="complex"))
                },
                coords={
                    "input": [in_id],
                    "output": out_ids,
                    "noise_channel": ("output", [noise_channel for x in out_ids]),
                    "f": f
                },
                attrs={
                    "n_winds": 0,
                    "input_clean_sequence": []
                },
            )

        else:
            if not isinstance(sdf, SpectralDensity):
                raise TypeError("sdf is not a SpectralDensity object")
            # if not type(sdf) == "SpectralDensity":
            #     raise TypeError(f"{type(sdf).split['.'][-1]=} is not 'SpectralDensity'")
            in_id, out_ids = self._expand_ids(sdf, in_id, out_ids)
            in_units = sdf.channel_units(in_id)
            clean_sequence = sdf.clean_sequence(in_id)
            out_units = [sdf.channel_units(x) for x in out_ids]
            f = sdf.freqs
            # Set properties
            dims = ("input", "output", "f")
            shape = (1, len(out_ids), len(f))
            # rf units are out_chan_units/in_chan_units
            # instrument_response units are in_chan_units/out_chan_units
            # rf * instrument_response gives rf w.r.t. data counts
            self._ds = xr.Dataset(
                data_vars={
                    "value": (dims, np.zeros(shape, dtype="complex")),
                    "uncert_mult": (dims, np.zeros(shape)),
                    "corr_mult": (dims, np.zeros(shape)),
                    "instrument_response": (dims, np.ones(shape, dtype="complex"))
                },
                coords={
                    "input": [in_id],
                    "output": out_ids,
                    "f": f,
                    "in_units": ("input", [in_units]),
                    "out_units": ("output", out_units),
                    "noise_channel": ("output", [noise_channel for x in out_ids]),
                },
                attrs={
                    "n_winds": sdf.n_windows,
                    "input_clean_sequence": clean_sequence
                }
            )
            for out_id in out_ids:
                rf, err_mult, corr_mult = self._calcrf(
                    sdf, in_id, out_id, noise_channel,
                    n_to_reject, min_freq, max_freq)
                self._ds["value"].loc[dict(input=in_id,
                                           output=out_id)] = rf
                self._ds["uncert_mult"].loc[dict(input=in_id,
                                                 output=out_id)] = err_mult
                self._ds["corr_mult"].loc[dict(input=in_id,
                                               output=out_id)] = corr_mult
                self._ds["instrument_response"].loc[
                    dict(input=in_id, output=out_id)
                ] = (sdf.channel_instrument_response(out_id)
                     / sdf.channel_instrument_response(in_id))
            if show_progress:
                self._plot_progress(sdf)

    def __repr__(self):
        s = (f"{self.__class__.__name__}(<SpectralDensity object>, "
             f"'{self.input_channel_id}', {self.output_channel_ids}, "
             f"{self.noise_channels})")
        return s

    def __str__(self):
        s = f"{self.__class__.__name__} object:\n"
        s += f"  input_channel_id='{self.input_channel_id}'\n"
        s += f"  output_channel_ids={self.output_channel_ids}\n"
        s += f"  noise_channels={self.noise_channels}\n"
        s += f"  n_windows={self.n_windows}"
        return s

    def copy(self):
        return copy.copy(self)

    def deepcopy(self):
        return copy.deepcopy(self)

    @property
    def freqs(self):
        """Frequency response function frequencies"""
        return self._ds.coords["f"].values

    @property
    def input_channel_id(self):
        return str(self._ds.coords["input"].values[0])

    @property
    def input_clean_sequence(self):
        """"""
        return self._ds.attrs["input_clean_sequence"]

    @property
    def output_channel_ids(self):
        return list(self._ds.coords["output"].values)

    @property
    def input_units(self):
        """Frequency response function input channel units"""
        return str(self._ds.coords["in_units"].values[0])

    @property
    def n_windows(self):
        """Number of time series data windows used"""
        return self._ds.attrs["n_winds"]

    @property
    def noise_channels(self):
        """Names of the noise channel for each rf"""
        return list(self._ds.coords["noise_channel"].values)

    def coh_signif(self, prob=0.95):
        """
        Return coherence significance level

        Args:
            prob (float): significance level (between 0 and 1)
        """
        return baseutils.coherence_significance_level(self.n_windows, prob)

    def output_units(self, output_channel_id):
        """Frequency response function output channel units"""
        oc = self._match_out_id(output_channel_id)
        return str(self._ds.sel(output=oc).coords["out_units"].values)

    def noise_channel(self, output_channel_id):
        """
        Return the channel assumed to have incoherent noise
        
        Args:
            output_channel_id (str): the channel to use
            
        Returns:
            str: The channel ('input', 'output', 'equal', or 'unknown')
        """
        oc = self._match_out_id(output_channel_id)
        return str(self._ds.sel(output=oc).coords["noise_channel"].values)

    def value(self, output_channel_id, zero_as_none=False, verbose=False):
        """
        Return frequency response function for the given output channel

        Args:
            output_channel_id (str): output channel id
            zero_as_none (bool): return non-calculated values as Nones instead
                of zeros
        """
        oc = self._match_out_id(output_channel_id)
        if verbose is True:
            print(f'{output_channel_id=} was matched by {oc=}')
        
        rf = np.squeeze(self._ds["value"].sel(output=oc).values)
        if zero_as_none:
            rf[np.abs(rf) == 0] = None  # returns nan + nanj!
        return rf

    def value_wrt_counts(self, output_channel_id, zero_as_none=False):
        """
        Return frequency response function with respect to raw data counts

        Args:
            output_channel_id (str): output channel name
            zero_as_none (bool): return non-calculated values as Nones instead
                of zeros
        """
        oc = output_channel_id
        return self.value(oc, zero_as_none) * self.instrument_response(oc)

    def corrector(self, output_channel_id, zero_as_none=False):
        """
        Return coherent channel correction factor for the given output channel

        Args:
            output_channel_id (str): output channel id
            zero_as_none (bool): return non-calculated values as Nones instead
                of zeros
        """
        oc = self._match_out_id(output_channel_id)
        corr_mult = np.squeeze(self._ds["corr_mult"].sel(output=oc).values)
        return self.value(output_channel_id, zero_as_none) * corr_mult

    def corrector_wrt_counts(self, output_channel_id, zero_as_none=False):
        """
        Return frequency response function with respect to raw data counts

        Args:
            output_channel_id (str): output channel id
            zero_as_none (bool): return non-calculated values as Nones instead
                of zeros
        """
        oc = output_channel_id
        return self.corrector(oc, zero_as_none) * self.instrument_response(oc)

    def instrument_response(self, output_channel_id, zero_as_none=False):
        """
        Return (output_channel_instr_response/input_channel_instr_response)

        Divide count-based response function by this to get unit-based
        Multiply unit-based response function by this to get count-based

        Args:
            output_channel_id (str): output channel id
            zero_as_none (bool): NOT USED!
        
        Returns:
            :class:`numpy.ndarray``
        """
        oc = self._match_out_id(output_channel_id)
        ir = self._ds["instrument_response"].sel(output=oc).values
        return np.squeeze(ir)

    def uncert_mult(self, output_channel_id):
        """
        Return uncertainty as a fraction of the frequency response function

        Args:
            output_channel (str): channel to return uncertainty for
        """
        oc = self._match_out_id(output_channel_id)
        return np.squeeze(self._ds["uncert_mult"].sel(output=oc).values)

    def uncertainty(self, out_id):
        """
        Return frequency response function uncertainty

        Args:
            out_id (str): channel to return uncertainty for
        """
        return self.value(out_id) * self.uncert_mult(out_id)

    def uncertainty_wrt_counts(self, out_id):
        """
        Return frequency response function uncertainty with respect to counts
        """
        return self.value_wrt_counts(out_id) * self.uncert_mult(out_id)

    @staticmethod
    def _expand_ids(sdf, in_id, out_ids):
        """
        Wildcard expansion

        Return in_id and out_ids expanded to match input and output
        channel name in the SpectralDensity object

        Also returns all output channels if out_ids is None
        """
        # Validate in_id
        verified_in_id = baseutils.match_one_str(in_id, sdf.ids, "in_id", "sdf.ids")

        # Validate out_ids
        if out_ids is None:
            # Select all channels except in_id
            verified_out_ids = [x for x in sdf.ids if not x == in_id]
        else:
            if not isinstance(out_ids, list):
                raise TypeError("Error: out_ids is not a list")
            verified_out_ids = []
            for out_id in out_ids:
                voc = baseutils.match_one_str(out_id, sdf.ids, "out_id", "sdf.ids")
                verified_out_ids.append(voc)

        return verified_in_id, verified_out_ids

    def _match_out_id(self, value):
        """
        Returns output channel id matching string (may have *,? wildcards)

        Error if there is not exactly one match
        """
        # Validate in_id
        if not isinstance(value, str):
            raise TypeError("Error: value is not a str")
        out_id = baseutils.match_one_str(value, self.output_channel_ids,
                                 "value", "self.output_channel_ids")
        return out_id

    def _calcrf(self, spect_density, input, output, noise_channel="output",
                n_to_reject=1, min_freq=None, max_freq=None):
        """
        Calculate frequency response function between two channels

        Returns 0 for values where coherence is beneath signif level

        Uses equations from Bendat&Piersol, 1986 (BP86)

        Args:
            spect_density(:class: ~SpectralDensity): cross-spectral density
                matrix
            input (str): input channel id
            output (str): output channel id
            noise_channel (str): which channel has the noise
            n_to_reject (int): only use values for which more than this
                many consecutive coherences are above the 95% significance
                level (0 = use all)
            min_freq (float): set to zero for frequencies below this value
            max_freq (float): set to zero for frequencies above this value

        Returns:
            (tuple):
                H (numpy.array): frequency response function
                H_err (numpy.array): uncertainty multiplier
                corr_mult (numpy.array): value to multiply H by when correcting
                    spectra
        """
        coh = spect_density.coherence(input, output)
        f = spect_density.freqs

        # Calculate Frequency Response Function
        Gxx = spect_density.autospect(input)
        Gyy = spect_density.autospect(output)
        Gxy = spect_density.crossspect(input, output)
        Gyx = spect_density.crossspect(output, input)
        # Crawford et al. 1991 eqn 4,  from BP2010 eqn 9.90
        H_err = np.sqrt((np.ones(coh.shape) - coh) / (2*coh*self.n_windows))
        noise_channels = ("output", "input", "equal", "unknown")
        if not noise_channel in noise_channels:
            raise ValueError(f"{noise_channel=} not in {noise_channels}")
        if noise_channel == "output":
            H = Gxy / Gxx  # BP86 eqn 6.37
            corr_mult = np.ones(H.shape)  # No change
        elif noise_channel == "input":
            H = Gyy / Gyx    # BP86 eqn 6.42
            corr_mult = coh  # derived from BP86 eqns 6.44 and 6.46
        elif noise_channel == "equal":
            # Derived from BP86 eqns 6.48, 6.49, 6.51 and 6.52
            H = (Gxy / Gxx) / np.sqrt(coh)
            corr_mult = np.sqrt(coh)
        elif noise_channel == "unknown":
            Hmax = (Gyy / Gyx)*(1+H_err)   # high value; all noise on input
            Hmin = (Gxy / Gxx)/(1+H_err)   # low value: all noise on output
            H = (Hmin + Hmax)/2
            H_err = ((Hmax-Hmin)/2)/H
            corr_mult = np.sqrt(coh) # Just copied "equal", probably wrong
        else:
            raise ValueError(f'unknown noise channel: "{noise_channel}"')
        H = self._zero_bad(H, coh, n_to_reject, f, min_freq, max_freq)

        # Calculate uncertainty
        return H, H_err, corr_mult

    def plot(self, errorbars=True, show=True, outfile=None):
        """
        Plot frequency response functions

        Args:
            errorbars (bool): plot error bars
            show (bool): show on the screen
            outfile (str): save figure to this filename
        Returns:
            (numpy.ndarray): array of axis pairs (amplitude, phase)
        """
        inp = self.input_channel_id
        outputs = self.output_channel_ids
        rows = 1
        cols = len(outputs)
        ax_array = np.ndarray((rows, cols), dtype=tuple)
        # fig, axs = plt.subplots(rows, cols, sharex=True)
        fig = plt.figure()
        in_suffix = self._find_str_suffix(inp, outputs)
        for out_id, j in zip(outputs, range(len(outputs))):
            axa, axp = self.plot_one(inp, out_id, fig, (rows, cols),
                                     (0, j), show_ylabel=j == 0,
                                     errorbars=errorbars,
                                     title=f"{out_id}/{in_suffix}",
                                     show_xlabel=True)
        ax_array[0, j] = (axa, axp)
        if outfile:
            plt.savefig(outfile)
        if show:
            plt.show()
        else:
            plt.close()
        return ax_array

    def _plot_progress(self, spect_dens, show=True):
        """
        Plot frequency response functions and the coherences that made them

        Args:
            spect_dens (:class:`tiskit:SpectralDensity`): spectral density
                matrix
            show (bool): show plot
        Returns:
            (numpy.ndarray): array of axis pairs (amplitude, phase)
        """
        inp = self.input_channel_id
        outputs = self.output_channel_ids
        shape = (2, len(outputs))
        ax_array = np.ndarray(shape, dtype=tuple)
        fig, axs = plt.subplots(shape[0], shape[1], sharex=True)
        in_suffix = self._find_str_suffix(inp, outputs)
        for out_id, j in zip(outputs, range(len(outputs))):
            axa, axp = self.plot_one(
                inp,
                out_id,
                fig,
                shape,
                (0, j),
                show_ylabel=j == 0,
                show_xlabel=True,
                title=f"{out_id}/{in_suffix}",
            )
            ax_array[0, j] = (axa, axp)
            axa, axp = spect_dens.plot_one_coherence(
                inp,
                out_id,
                fig,
                shape,
                (1, j),
                show_ylabel=j == 0,
                show_xlabel=True,
                show_phase=False,
            )
            ax_array[1, j] = axa
        if show:
            plt.show()
        return ax_array

    def _find_str_suffix(self, inp, outps):
        """
        Find longest non-common suffix of inp, outps

        Args:
            inp (str): string to reduce
            outps: (list of str): list of base strings to compare
        Returns:
            result (str): longest non-commmon suffix
        """
        ii_ind = len(inp) - 1
        for oc, j in zip(outps, range(len(outps))):
            for ii in range(0, len(oc)):
                if not inp[ii] == oc[ii]:
                    break
            if ii < ii_ind:
                ii_ind = ii
            return inp[ii:]

    def plot_one(self, in_id, out_id,
                 fig=None, fig_grid=(1, 1), plot_spot=(0, 0), errorbars=True,
                 label=None, title=None, show_xlabel=True, show_ylabel=True):
        """
        Plot one frequency response function

        Args:
            in_id (str): input channel id
            out_id (str): output channel id
            fig (:class: ~matplotlib.figure.Figure): figure to plot on, if
                None this method will plot on the current figure or create
                a new figure.
            fig_grid (tuple): this plot sits in a grid of this many
                (rows, columns)
            plot_spot (tuple): put this plot at this (row, column) of
                the figure grid
            errorbars (bool): plot as vertical error bars
            label (str): string to put in legend
            title (str): string to put in title
            show_xlabel (bool): put an xlabel on this subplot
            show_ylabel (bool): put a y label on this subplot

        Returns:
            tuple:
                frequency response function amplitude plot
                frequency response function phase plot
        """
        f = self.freqs
        rf = self.value(out_id).copy()
        rferr = self.uncertainty(out_id)
        rfunits = self.output_units(out_id) + "/" + self.input_units
        ibad = (rf == 0).nonzero()
        if fig is None:
            fig = plt.gcf()

        # Plot amplitude
        if self.input_units.upper() == 'PA' and self.output_units(out_id) == '1':
            fig.suptitle("Compliance")
        else:
            fig.suptitle("Frequency Response Functions")
        ax_a = plt.subplot2grid(
            (3 * fig_grid[0], 1 * fig_grid[1]),
            (3 * plot_spot[0] + 0, plot_spot[1] + 0),
            rowspan=2,
        )
        rf[rf == 0] = np.nan
        rferr[rferr == 0] = np.nan
        if errorbars is True:
            ax_a.errorbar(f, np.abs(rf), np.abs(rferr), fmt='b_', ecolor='k',
                          markersize=3, label=rfunits)
            if np.any(rf is not np.nan):
                ax_a.set_yscale('log')
            ax_a.set_xscale('log')
            ax_a.legend()
        else:
            ax_a.loglog(f, np.abs(rf + rferr), color="blue", linewidth=0.5)
            ax_a.loglog(f, np.abs(rf - rferr), color="blue", linewidth=0.5)
            ax_a.loglog(f, np.abs(rf), color="black", label=label)
        ax_a.set_xlim(self.freqs[1], self.freqs[-1])
        if title is not None:
            ax_a.set_title(title, fontsize='medium')
        if label is not None:
            ax_a.legend()
        if show_ylabel:
            ax_a.set_ylabel("FRF")
        
        # Plot phase
        ax_p = plt.subplot2grid(
            (3 * fig_grid[0], 1 * fig_grid[1]),
            (3 * plot_spot[0] + 2, plot_spot[1] + 0),
            sharex=ax_a,
        )
        phases = np.angle(rf, deg=True)
        phases[ibad] = np.nan
        phase_lim = 220
        igood = np.invert(np.isnan(phases))
        wrap_phases = phases.copy()
        wrap_phases[igood] = np.unwrap(phases[igood], period=360)
        if (np.all(wrap_phases[igood] > -phase_lim)
            and np.all(wrap_phases[igood] < phase_lim)):
            ax_p.semilogx(f, wrap_phases)
        else:
            ax_p.semilogx(f, phases)
        ax_p.set_ylim(-phase_lim, phase_lim)
        ax_p.set_xlim(self.freqs[1], self.freqs[-1])
        # ax_p.set_xlim(f[1], f[-1])
        ax_p.set_yticks((-180, 0, 180))
        if show_ylabel:
            ax_p.set_ylabel("Phase")
        else:
            ax_p.set_yticklabels([])
        if show_xlabel:
            ax_p.set_xlabel("Frequency (Hz)")
        return ax_a, ax_p

    def _zero_bad(self, H, coh, n_to_reject, f, min_freq, max_freq):
        """
        Set non-significant elements to zero

        Args:
            H (np.ndarray): one-D array
            coh (np.ndarray): absolute coherence (1D)
            n_to_reject: how many consecutive "coherent" values are needed to
                accept the value at thise indice?
            f (np.array): frequencies
            min_freq: set values to zero for frequencies below this
            max_freq: set values to zero for frequencies above this
        """
        assert isinstance(H, np.ndarray)
        assert isinstance(coh, np.ndarray)
        if min_freq is not None and max_freq is not None:
            if min_freq >= max_freq:
                raise ValueError("min_freq >= max_freq")
        goods = np.full(coh.shape, True)
        if min_freq is not None:
            goods[f < min_freq] = False
        if max_freq is not None:
            goods[f > max_freq] = False
        if n_to_reject > 0:
            goods = np.logical_and(goods, coh > self.coh_signif(0.95))
            # goods = coh > self.coh_signif(0.95)

            # for n == 1, should do nothing, for n == 2, shift once, etc
            if n_to_reject > 1:
                goods_orig = goods.copy()
                # calc n values for both sides: 2=>0, 3,4=>1, 5,6->2, etc
                both_sides = int(np.floor((n_to_reject - 1) / 2))
                # Shift to both sides
                for n in range(1, both_sides + 1):
                    goods = np.logical_and(
                        goods, np.roll(goods_orig, n)
                    )
                    goods = np.logical_and(
                        goods, np.roll(goods_orig, -n)
                    )
                if n_to_reject % 2 == 0:  # IF EVEN, roll in one from above
                    goods = np.logical_and(
                        goods,
                        goods_orig.roll(
                            f=-both_sides - 1, fill_value=goods_orig[-1]
                        ),
                    )
            H[~goods] = 0
        return H
