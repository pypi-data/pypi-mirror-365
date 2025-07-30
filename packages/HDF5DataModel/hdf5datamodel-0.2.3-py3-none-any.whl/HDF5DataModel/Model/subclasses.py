#from typing import Optional
import os
import collections
import numpy as np
#from HDF5DataModel.Model.h5model import H5DataModel
from HDF5DataModel.Model.attrsclasses import DatasetAttrs, AcquisitionAtrrs, AcqSigAttrs, GenSigAttrs, AcqTraceAttrs

from pyseg2.rawseg2 import write_raw_seg2


class Dataset:
    def __init__(self, name='default', parent: "H5DataModel"=None):
        self.name = name
        self.attrs = DatasetAttrs()
        self.acquisitions = collections.OrderedDict()
        self.parent = parent  # the parent H5DataModel of this dataset

    def add_acquisition(self, name):
        self.acquisitions[name] = Acquisition()
        return self.acquisitions[name]

    def to_hdf5_file(self, h5file):
        """Save the experiment to a HDF5 file"""
        experiment_group = h5file.create_group(self.name)
        experiment_group.attrs.update(self.attrs.__dict__)
        for acq_name, acquisition in self.acquisitions.items():
            acquisition_group = experiment_group.create_group(acq_name)
            acquisition_group.attrs.update(acquisition.attrs.__dict__)
            for sig_name, acq_sig in acquisition.acq_sigs.items():
                acq_sig_group = acquisition_group.create_group(sig_name)
                acq_sig_group.attrs.update(acq_sig.attrs.__dict__)
                for trace_name, trace in acq_sig.traces.items():
                    trace_group = acq_sig_group.create_group(trace_name)
                    trace_group.attrs.update(trace.attrs.__dict__)
                    trace_group.create_dataset('signal', data=trace.data)
            for gen_name, gen_sig in acquisition.gen_sigs.items():
                gen_sig_group = acquisition_group.create_group(gen_name)
                gen_sig_group.attrs.update(gen_sig.attrs.__dict__)
                gen_sig_group.create_dataset('signal', data=gen_sig.signal)

    def from_h5(self, h5file, experiment_name):
        """Load the experiment from a HDF5 file"""
        self.name = experiment_name
        experiment_group = h5file[experiment_name]
        self.attrs = DatasetAttrs()
        self.attrs.set_attrs_from_dict(dict(experiment_group.attrs))
        for acq_name in experiment_group:
            acquisition_group = experiment_group[acq_name]
            self.add_acquisition(acq_name)
            self.acquisitions[acq_name].attrs = AcquisitionAtrrs()
            self.acquisitions[acq_name].attrs.set_attrs_from_dict(dict(acquisition_group.attrs))
            for sig_name in acquisition_group:
                if acquisition_group[sig_name].attrs['type'] == 'Acquisition attributes':
                    self.acquisitions[acq_name].add_acq_sig(sig_name)
                    acq_sig_group = acquisition_group[sig_name]
                    self.acquisitions[acq_name].acq_sigs[sig_name].attrs = AcqSigAttrs()
                    self.acquisitions[acq_name].acq_sigs[sig_name].attrs.set_attrs_from_dict(dict(acq_sig_group.attrs))
                    for trace_name in acq_sig_group:
                        trace_group = acq_sig_group[trace_name]
                        self.acquisitions[acq_name].acq_sigs[sig_name].add_trace(trace_name)
                        self.acquisitions[acq_name].acq_sigs[sig_name].traces[trace_name].attrs = AcqTraceAttrs()
                        self.acquisitions[acq_name].acq_sigs[sig_name].traces[trace_name].attrs.set_attrs_from_dict(dict(trace_group.attrs))
                        self.acquisitions[acq_name].acq_sigs[sig_name].traces[trace_name].data = np.array(trace_group['signal'])
                elif acquisition_group[sig_name].attrs['type'] == 'Generation attributes':
                    self.acquisitions[acq_name].add_gen_sig(sig_name)
                    gen_sig_group = acquisition_group[sig_name]
                    self.acquisitions[acq_name].gen_sigs[sig_name].attrs = GenSigAttrs()
                    self.acquisitions[acq_name].gen_sigs[sig_name].attrs.set_attrs_from_dict(dict(gen_sig_group.attrs))
                    self.acquisitions[acq_name].gen_sigs[sig_name].signal = np.array(gen_sig_group['signal'])


class Acquisition:
    """An acquisition is a set of one generation signal and multiple acquisition signals with the sample and config"""
    def __init__(self, parent: "Dataset"=None):
        self.attrs = AcquisitionAtrrs()
        self.acq_sigs = collections.OrderedDict()
        self.gen_sigs = collections.OrderedDict()
        self.parent = parent  # the Parent Acquisition of self

    def add_acq_sig(self, name):
        self.acq_sigs[name] = AcqSig()
        return self.acq_sigs[name]

    def add_gen_sig(self, name):
        self.gen_sigs[name] = GenSig()
        return self.gen_sigs[name]


class AcqSig:
    def __init__(self, parent: "Acquisition"=None):
        self.attrs = AcqSigAttrs()
        self.traces = collections.OrderedDict()
        self.parent = parent

    def add_trace(self, name):
        self.traces[name] = AcqTrace()
        return self.traces[name]

    def to_seg2(self, filename: str, allow_overwrite: bool=False, include_type_names: bool=False):

        trace_header_and_data = []
        for trace in self.traces.values():
            trace: AcqTrace

            # FILL THE MANDATRY ATTRIBUTES
            trace.attrs.SAMPLE_INTERVAL = 1. / trace.attrs.sampling_freq
            # ...

            trace_header_and_data.append((trace.attrs.__dict__, trace.data))

        write_raw_seg2(
            filename=filename,
            file_header=self.attrs.__dict__,
            trace_header_and_data=trace_header_and_data,
            allow_overwrite=allow_overwrite,
            include_type_names=include_type_names,
            )


class GenSig:
    def __init__(self, parent: "Acquisition"=None):
        self.attrs = GenSigAttrs()
        self.signal = np.zeros(1)
        self.parent = parent  # the parent Acquisition of self


class AcqTrace:
    def __init__(self, parent: "AcqSig, GenSig"=None):
        self.data = np.zeros(10)
        self.attrs = AcqTraceAttrs()
        self.parent = parent
