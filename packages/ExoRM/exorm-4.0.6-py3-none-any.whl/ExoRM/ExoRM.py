import numpy
import os
import pandas
import pickle
import arviz
import pymc as pm
from pymc.gp import HSGP
import pytensor.tensor as pt

from platformdirs import user_data_dir

def get_exorm_filepath(relative_filepath):
    return os.path.join(user_data_dir('ExoRM'), relative_filepath)

def read_rm_data(path = None, relative_filepath = 'exoplanet_rm.csv'):
    if path is None:
        path = get_exorm_filepath(relative_filepath)

    data = pandas.read_csv(path)

    return data

def read_exoplanet_data(path = None, relative_filepath = 'exoplanet_data.csv'):
    if path is None:
        path = get_exorm_filepath(relative_filepath)

    data = pandas.read_csv(path)

    return data

def save_data_to_other(new_path, relative_filepath = 'exoplanet_data.csv'):
    pandas.read_csv(get_exorm_filepath(relative_filepath)).to_csv(new_path, index = False)

def save_rm_to_other(new_path, relative_filepath = 'exoplanet_rm.csv'):
    pandas.read_csv(get_exorm_filepath(relative_filepath)).to_csv(new_path, index = False)

def unique_radius(data):
    counts = []
    for i in range(len(data['radius'])):
        while data.loc[i, 'radius'] in counts:
            data.loc[i, 'radius'] += 1e-12

        counts.append(data.loc[i, 'radius'])

    return data.sort_values('radius').reset_index(drop = True)

def preprocess_data(data):
    data['density'] = data['mass'] / data['radius'] ** 3
    data = data[~((data['density'] >= numpy.percentile(data['density'], 99)) | (data['density'] <= numpy.percentile(data['density'], 1)))].reset_index(drop = True)

    return data

def nn_forward(x, weights1, bias1, weights2, bias2):
    h = pt.dot(x, weights1) + bias1
    h_activated = pt.switch(pt.lt(h, 0), 0, h)  # ReLU
    out = pt.dot(h_activated, weights2) + bias2
    return out.flatten()

def numpy_nn_forward(x, weights1, bias1, weights2, bias2):
    h = numpy.dot(x, weights1) + bias1
    h_activated = numpy.where(h < 0, 0, h)  # ReLU, same logic as pt.switch(pt.lt(h, 0), 0, h)
    out = numpy.dot(h_activated, weights2) + bias2
    return out.flatten()

def init_model(model_type = 'nn', inputs_save_path = None):
    if inputs_save_path is None:
        inputs_save_path = get_exorm_filepath('inputs.pkl')

    try:
        with open(inputs_save_path, 'rb') as file:
            data = pickle.load(file)

    except:
        print('No inputs found.')
        return None

    if model_type == 'gp':
        with pm.Model() as model:
            x_data = pm.Data('x_observed_data', data['x_obs'])
            x_err_data = pm.Data('x_err_data', data['x_err'])
            y_data = pm.Data('y_true_data', data['y_true'])
            y_err_data = pm.Data('y_err_data', data['y_err'])

            n = x_data.shape[0]

            mean_func = pm.gp.mean.Zero()
            ell = pm.HalfNormal('ell', sigma = 1)
            eta = pm.HalfNormal('eta', sigma = 1)
            cov_func = eta ** 2 * pm.gp.cov.ExpQuad(input_dim = 1, ls = ell)

            # Changed from HSGP to pm.gp.GP
            gp_f = pm.gp.Latent(cov_func = cov_func, mean_func = mean_func)

            _x_true = pm.Normal('_x_true', mu = x_data, sigma = x_err_data, shape = n)
            f = gp_f.prior('f', X = _x_true[:, None]) # X needs to be 2D, so _x_true[:, None]

            ell_sigma = pm.HalfNormal('ell_sigma', sigma = 1)
            eta_sigma = pm.HalfNormal('eta_sigma', sigma = 1)
            cov_func_sigma = eta_sigma ** 2 * pm.gp.cov.ExpQuad(input_dim = 1, ls = ell_sigma)

            # Changed from HSGP to pm.gp.GP
            gp_sigma = pm.gp.Latent(cov_func = cov_func_sigma, mean_func = mean_func)

            log_sigma_intrinsic = gp_sigma.prior('log_sigma_intrinsic', X = _x_true[:, None])
            sigma_intrinsic = pm.Deterministic('sigma_intrinsic', pt.exp(log_sigma_intrinsic))
            sigma_total = pm.Deterministic('sigma_total', pt.sqrt(y_err_data ** 2 + sigma_intrinsic ** 2))

            nu = pm.HalfNormal('nu', sigma = 10)
            _y_true = pm.StudentT('y_true', nu = nu, mu = f, sigma = sigma_total, observed = y_data)
            y_pred = pm.StudentT('y_pred', nu = nu, mu = f, sigma = sigma_total, shape = n)

    elif model_type == 'nn':
        with pm.Model() as model:
            # Data
            x_data = pm.Data('x_observed_data', data['x_obs'])
            x_err_data = pm.Data('x_err_data', data['x_err'])
            y_data = pm.Data('y_true_data', data['y_true'])
            y_err_data = pm.Data('y_err_data', data['y_err'])

            n = x_data.shape[0]

            # Latent true x
            _x_true = pm.Normal('_x_true', mu=x_data, sigma=x_err_data, shape=n)
            x_in = _x_true[:, None]

            # First NN layer parameters for f
            n_hidden = 4
            w1_std = numpy.sqrt(2 / 1) # Kaiming / He initialization
            w1 = pm.Normal('w1', 0, w1_std, shape=(1, n_hidden))
            b1 = pm.Normal('b1', 0, 1, shape=(n_hidden,)) # Biases often still use small std

            # For w2: input_dim = n_hidden, output_dim = 1
            w2_std = numpy.sqrt(2 / n_hidden)
            w2 = pm.Normal('w2', 0, w2_std, shape=(n_hidden, 1))
            b2 = pm.Normal('b2', 0, 1, shape=(1,))

            f = nn_forward(x_in, w1, b1, w2, b2)

            # --- Neural network for log intrinsic noise (apply He initialization principle) ---
            # Same logic for w1s, b1s, w2s, b2s
            w1s_std = numpy.sqrt(2 / 1)
            w1s = pm.Normal('w1s', 0, w1s_std, shape=(1, n_hidden))
            b1s = pm.Normal('b1s', 0, 1, shape=(n_hidden,))

            w2s_std = numpy.sqrt(2 / n_hidden)
            w2s = pm.Normal('w2s', 0, w2s_std, shape=(n_hidden, 1))
            b2s = pm.Normal('b2s', 0, 1, shape=(1,))

            log_sigma_intrinsic = nn_forward(x_in, w1s, b1s, w2s, b2s)
            sigma_intrinsic = pm.Deterministic('sigma_intrinsic', pt.exp(log_sigma_intrinsic))

            # Total noise combining measurement noise and intrinsic noise
            sigma_total = pm.Deterministic('sigma_total', pt.sqrt(y_err_data ** 2 + sigma_intrinsic ** 2))

            # Student-t likelihood for robustness
            nu = pm.HalfNormal('nu', sigma=10)
            y_true = pm.StudentT('y_true', nu=nu, mu=f, sigma=sigma_total, observed=y_data)

            # Optional posterior predictive
            y_pred = pm.StudentT('y_pred', nu=nu, mu=f, sigma=sigma_total, shape=n)

    elif model_type == 'pwlf':
        with pm.Model() as model:
            # Observed data
            x_data = pm.Data('x_observed_data', data['x_obs'])
            x_err_data = pm.Data('x_err_data', data['x_err'])
            y_data = pm.Data('y_true_data', data['y_true'])
            y_err_data = pm.Data('y_err_data', data['y_err'])

            n = x_data.shape[0]
            nk = 4 - 1  # number of slope changes (i.e., 3 knots for 4 segments)

            # Latent true x (for x error)
            _x_true = pm.Normal('_x_true', mu = x_data, sigma = x_err_data, shape = n)

            # --- Mean function: piecewise linear ---
            intercept = pm.Normal('intercept', mu = y_data.mean(), sigma = y_data.std())
            slope_initial = pm.Normal('slope_initial', mu = 0, sigma = 1)

            x_min = data['x_obs'].min()
            x_max = data['x_obs'].max()
            knot_locs_unsorted = pm.Uniform('knot_locs_unsorted', lower = x_min, upper = x_max, shape = nk)
            knot_locs = pm.Deterministic('knot_locs', pt.sort(knot_locs_unsorted))

            delta_slopes = pm.Normal('delta_slopes', mu = 0, sigma = 0.5, shape = nk)

            f = intercept + slope_initial * _x_true
            for i in range(nk):
                f += delta_slopes[i] * pt.maximum(0, _x_true - knot_locs[i])

            # --- Noise function: piecewise linear log_sigma_intrinsic ---
            intercept_sigma = pm.Normal('intercept_sigma', mu = -1, sigma = 1)
            slope_initial_sigma = pm.Normal('slope_initial_sigma', mu = 0, sigma = 1)
            delta_slopes_sigma = pm.Normal('delta_slopes_sigma', mu = 0, sigma = 0.5, shape = nk)

            log_sigma_intrinsic = intercept_sigma + slope_initial_sigma * _x_true
            for i in range(nk):
                log_sigma_intrinsic += delta_slopes_sigma[i] * pt.maximum(0, _x_true - knot_locs[i])

            sigma_intrinsic = pm.Deterministic('sigma_intrinsic', pt.exp(log_sigma_intrinsic))

            # Combine with measurement error
            sigma_total = pm.Deterministic('sigma_total', pt.sqrt(y_err_data ** 2 + sigma_intrinsic ** 2)) # geometric mean

            # Student-T likelihood for robustness
            nu = pm.HalfNormal('nu', sigma = 10)
            y_true = pm.StudentT('y_true', nu = nu, mu = f, sigma = sigma_total, observed = y_data)

            # Posterior predictive
            y_pred = pm.StudentT('y_pred', nu = nu, mu = f, sigma = sigma_total, shape = n)

    else:
        raise ValueError('Model type not found, available are [gp, nn, pwlf]')

    return model

def init_train_model(x_obs, x_err, y_true, y_err, model_type = 'nn', inputs_save_path = None):
    if inputs_save_path is None:
        inputs_save_path = get_exorm_filepath('inputs.pkl')

    with open(inputs_save_path, 'wb') as file:
        data = {
            'x_obs': x_obs,
            'x_err': x_err,
            'y_true': y_true,
            'y_err': y_err
        }
        pickle.dump(data, file)

    return init_model(model_type, inputs_save_path)

class ExoRM:
    def __init__(self, model_type = 'nn'):
        self.model = init_model(model_type)
        self.model_type = model_type

    def create_trace(self, x_obs, x_err, y_true, y_err, inputs_save_path = None, trace_path = None, *, draw = 1000, tune = 2000, chains = 4, cores = 4, target_accept = 0.99, max_treedepth = 10, progressbar = True):
        if trace_path is None:
            trace_path = get_exorm_filepath('trace.nc')

        self.model = init_train_model(x_obs, x_err, y_true, y_err, model_type = self.model_type, inputs_save_path = inputs_save_path)

        with self.model:
            self.trace = pm.sample(draws = draw, tune = tune, init = 'advi+adapt_diag', chains = chains, cores = cores, target_accept = target_accept, max_treedepth = max_treedepth, idata_kwargs = {'log_likelihood': True}, progressbar = progressbar)

        self.save_trace(trace_path)

    def load_trace(self, trace_path = None):
        if trace_path is None:
            trace_path = get_exorm_filepath('trace.nc')

        self.trace = arviz.from_netcdf(trace_path)

        return self.trace

    def save_trace(self, trace_path = None):
        if trace_path is None:
            trace_path = get_exorm_filepath('trace.nc')

        if os.path.exists(trace_path):
            os.remove(trace_path)
            print('Old trace deleted.')

        arviz.to_netcdf(self.trace, trace_path)

    def save_defaults_to_other(self, inputs_save_path, trace_path):
        arviz.to_netcdf(arviz.from_netcdf(get_exorm_filepath('trace.nc')), trace_path)
        with open(inputs_save_path, 'wb') as file:
            with open(get_exorm_filepath('inputs.pkl'), 'rb') as source:
                pickle.dump(pickle.load(source), file)

    def save_other_to_defaults(self, inputs_save_path, trace_path):
        arviz.to_netcdf(arviz.from_netcdf(trace_path), get_exorm_filepath('trace.nc'))
        with open(get_exorm_filepath('inputs.pkl'), 'wb') as file:
            with open(inputs_save_path, 'rb') as source:
                pickle.dump(pickle.load(source), file)

    def get_raw_predictions(self, x, x_err = None):
        if x_err is None:
            x_err = numpy.zeros_like(x)

        with self.model:
            pm.set_data({'x_observed_data': x, 'x_err_data': x_err, 'y_err_data': numpy.zeros_like(x)})
            posterior_predictive = pm.sample_posterior_predictive(self.trace, var_names = ['y_pred'])

        return posterior_predictive.posterior_predictive['y_pred']  # shape: (chains, draws, n)

    def __call__(self, x, x_err = None):
        mu_y_samples = self.get_raw_predictions(x, x_err)
        y_pred = mu_y_samples.mean(axis = (0, 1))  # shape: (n,)

        return y_pred.to_numpy()

    def predict_full(self, x, x_err = None, lower = 2.5, upper = 97.5):
        mu_y_samples = self.get_raw_predictions(x, x_err)

        y_pred = mu_y_samples.mean(axis = (0, 1))  # shape: (n,)
        lower = numpy.percentile(mu_y_samples, lower, axis = (0, 1))
        upper = numpy.percentile(mu_y_samples, upper, axis = (0, 1))

        return y_pred.to_numpy(), lower, upper

    predict = __call__

    def predict_linear(self, x, x_err = None):
        if x_err is None:
            x_err = numpy.zeros_like(x)

        _x_err = numpy.log10(x) - numpy.log10(x - x_err) # max error

        return 10 ** self.predict(numpy.log10(x), _x_err)

    def predict_full_linear(self, x, x_err = None, lower = 2.5, upper = 97.5):
        if x_err is None:
            x_err = numpy.zeros_like(x)

        _x_err = numpy.log10(x) - numpy.log10(x - x_err) # max error

        return [10 ** _ for _ in self.predict_full(numpy.log10(x), _x_err, lower, upper)]

class ForecasterRM:
    log_mode = True

    @classmethod
    def forecaster(cls, x):
        if not cls.log_mode:
            x = numpy.log10(x)

        y = numpy.zeros_like(x)

        y = numpy.where(x < numpy.log10(1.23), cls.terran(x), y)
        y = numpy.where((x >= numpy.log10(1.23)) & (x < numpy.log10(11.1)), cls.neptunian(x), y)
        y = numpy.where((x >= numpy.log10(11.1)) & (x < numpy.log10(14.3)), numpy.nan, y)
        y = numpy.where(x >= numpy.log10(14.3), cls.stellar(x), y)

        if not cls.log_mode:
            return numpy.power(10, y)

        else:
            return y

    @classmethod
    def terran(cls, x):
        if not cls.log_mode:
            x = numpy.log10(x)

        y = (x - 0.00346) / 0.2790
        if not cls.log_mode:
            return numpy.power(10, y)

        else:
            return y

    @classmethod
    def neptunian(cls, x):
        if not cls.log_mode:
            x = numpy.log10(x)

        y = (x + 0.0925) / 0.589
        if not cls.log_mode:
            return numpy.power(10, y)

        else:
            return y

    @classmethod
    def jovian(cls, x):
        if not cls.log_mode:
            x = numpy.log10(x)

        y = (x - 1.25) / -0.044
        if not cls.log_mode:
            return numpy.power(10, y)

        else:
            return y

    @classmethod
    def stellar(cls, x):
        if not cls.log_mode:
            x = numpy.log10(x)

        y = (x + 2.85) / 0.881
        if not cls.log_mode:
            return numpy.power(10, y)

        else:
            return y