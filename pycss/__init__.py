import math, sys, md5, time
import numpy as np
import pp
import copy
import ast
import matplotlib.pyplot as plt

def _wrapper(func_handle, opt_params, fixed_params=None):
    """Wraps the main calculation function, in order to support two dictionaries of parameters,
    which will be passed to the calculation function as a combined set of keyword arguments.
    """
    params = dict(**opt_params)
    if fixed_params is not None:
        params.update(fixed_params)
    result = func_handle(**params)
    return result


class CSSEngine(object):
    def __init__(self, func_handle, opt_params, arguments, delta, ncpus='autodetect', basic_result=None, omega=1):
        """Main entrypoint for Composit Scaled Sensitivity calculation.
        Delegates calculation of basic computation and permuted computations to workers.
        Returns the calculated CSS and matrix of scaled sensitivities.

        :param opt_params: list of strings
        :param func_handle: function
        :param delta: int
        :param ncpus: int or 'autodetect'
        :param arguments: dict
        :param basic_response: numpy.array

        """

        self.opt_params = opt_params
        self.func_handle = func_handle
        self.delta = delta
        self.arguments = arguments
        self.basic_result = basic_result

        # Set the weights for each optimization parameter
        if isinstance(omega, dict):
            self.omega = omega
        else:
            self.omega = dict()
            for k in self.opt_params:
                self.omega[k] = omega

        self.ncpus = ncpus
        self.job_server = pp.Server(ppservers=())
        self.job_server.set_ncpus(ncpus=self.ncpus)
        self.ncpus = self.job_server.get_ncpus()

        self.jobs = dict()
        self.results = dict()
        self.ss = None
        self.css = None

        # Optional arguments for the job submission.
        # They can be modified after instantiation, before starting the computations.
        self.depfuncs = ()
        self.modules = ()
        self.callback = None
        self.callbackargs = ()
        self.group = 'default'
        self.globals = None

        # toggles wether dict or mapping in self.arguments are passed directly to the
        # function, or wether the key/value pairs are passed as keyword arguments.
        self.use_kwargs = True


    def _get_arg_indices(self, arg):
        """If argument name contains list/array indices, extract and return these."""
        tmp = arg.split('[', 1)
        if len(tmp) == 2:
            return tmp[0], ast.literal_eval('['+tmp[1])
        else:
            return tmp[0], None

    def go(self):
        """Compute Composite Scaled Sensitivities and plot."""
        self.do_computations()
        self.calculate_css()
        self.plot_css()

    def do_computations(self):
        """Delegates calculation of basic computation and permuted computations to workers.
        Reads and stores results.
        """

#        import pdb
#        pdb.set_trace()

        if self.use_kwargs:
            func = _wrapper
        else:
            func = self.func_handle

        # First submit standard calculation if needed.
        if self.basic_result is None:

            if self.use_kwargs:
                args = (self.func_handle, self.arguments)
            else:
                args = (self.arguments,)

            self.jobs['__basic__'] = self.job_server.submit(func, args,
                                                            depfuncs=self.depfuncs, modules=self.modules,
                                                            callback=self.callback, callbackargs=self.callbackargs,
                                                            group=self.group, globals=self.globals)
            print "Base job submitted..."

        # Then submit permuted calculations
        for k in self.opt_params:
            arguments = copy.deepcopy(self.arguments)

            key, indices = self._get_arg_indices(k)

            if indices is None or not indices:
                arguments[key] = self.arguments[key]*self.delta
            else:
                if len(indices) == 2:
                    # we have a 2D array index
                    arguments[key][indices[0]][indices[1]] = self.arguments[key][indices[0]][indices[1]]*self.delta
                else:
                    # we have just a single index
                    arguments[key][indices[0]] = self.arguments[key][indices[0]]*self.delta

            if self.use_kwargs:
                args = (self.func_handle, arguments)
            else:
                args = (arguments,)

            self.jobs[k] = self.job_server.submit(func, args,
                                                  depfuncs=self.depfuncs, modules=self.modules,
                                                  callback=self.callback, callbackargs=self.callbackargs,
                                                  group=self.group, globals=self.globals)
            print "Job '{0}' submitted...".format(k)

        # Collect and store the results
        self.basic_result = self.jobs['__basic__']()
        if not isinstance(self.basic_result, np.ndarray):
            if not hasattr(self.basic_result, '__iter__'):
                self.basic_result = np.array([self.basic_result])
            else:
                self.basic_result = np.array(self.basic_result)

        for k in self.opt_params:
            self.results[k] = self.jobs[k]()

    def print_stats(self):
        """Prints job execution statistics."""
        self.job_server.print_stats()

    def calculate_css(self):
        """Calculates scaled sensitivities and CSS."""
        self.ss = np.zeros((len(self.basic_result), len(self.opt_params)))
        self.css = np.zeros((len(self.opt_params),))

        for n,p in enumerate(self.opt_params):
            key, indices = self._get_arg_indices(p)
            if indices is None or not indices:
                v = self.arguments[p]
            else:
                if len(indices) == 2:
                    v = self.arguments[key][indices[0]][indices[1]]
                else:
                    v = self.arguments[key][indices[0]]

            # Calculate ss_j and css_j for the present parameter.
            self.ss[:, n] = ((self.results[p]-self.basic_result)/((v*self.delta)-v))*(v)*np.sqrt(self.omega[p])
            self.css[n] = np.sum(self.ss[:, n]**2)/len(self.ss[:, n])

    def plot_css(self):
        """Make a bar plot of the previously calculated CSS values."""
        #fig = plt.figure()
        x = np.arange(len(self.opt_params))
        width = 0.8
        plt.bar(x, self.css, width=width, facecolor='0.5', edgecolor='k')
        plt.xticks( x + width/2.,  self.opt_params, rotation='vertical')
        xlim = plt.gca().get_xlim()
        plt.gca().set_xlim([xlim[0]-width/2., xlim[1]+width/2.])
        plt.gca().set_ylabel('Composite Scaled Sensitivity')
        fig = plt.gcf()
        fig.tight_layout()
        plt.draw()
        plt.show(block=False)
        return fig

    def print_css(self):
        """Print table of css stdout."""
        maxlen = 0
        for p in self.opt_params:
            if len(p)>maxlen:
                maxlen = len(p)

        maxlen = max(maxlen, 9)

        print "----------------------------------------------------"
        print "Parameter".ljust(maxlen+3) + "CSS value".ljust(11) + "Initial value"
        print "----------------------------------------------------"

        for a,v in zip(self.opt_params, self.css):
            print "{0}:".format(a).ljust(maxlen+3) + "{0:8.3e}".format(v).ljust(11) + "{0:7.3f}".format(self.arguments[a])

        print "----------------------------------------------------"