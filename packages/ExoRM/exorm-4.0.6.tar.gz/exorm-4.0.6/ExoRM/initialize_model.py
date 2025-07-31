def initialize_model(inputs_save_path = None, trace_path = None, kwargs = {'cores': 4}):
    from ExoRM import read_rm_data, unique_radius, preprocess_data, init_model, ExoRM
    import matplotlib.pyplot as plot
    import numpy

    data = read_rm_data()
    data = unique_radius(data)
    data = preprocess_data(data)
    data

    _x = data['radius']
    _y = data['mass']

    x = numpy.log10(_x)
    y = numpy.log10(_y)

    x_upper = numpy.log10(_x + data['pl_radeerr1'])
    x_lower = numpy.log10(_x + data['pl_radeerr2'])
    x_err = numpy.maximum(x_upper - x, x - x_lower)

    y_upper = numpy.log10(_y + data['pl_bmasseerr1'])
    y_lower = numpy.log10(_y + data['pl_bmasseerr2'])
    y_err = numpy.maximum(y_upper - y, y - y_lower)

    x_obs = x
    y_true = y

    x, y, x_obs, y_true

    erm = ExoRM()

    erm.create_trace(x_obs, x_err, y_true, y_err, inputs_save_path = inputs_save_path, trace_path = trace_path, **kwargs)

    y_pred, lower, upper = erm.predict_full(x_obs, x_err)

    plot.scatter(x, y)
    plot.scatter(x, y_pred)
    plot.scatter(x, lower)
    plot.scatter(x, upper)
    plot.show()