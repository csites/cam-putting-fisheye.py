import numpy as np
import matplotlib.pyplot as plt

def exponential_function(x, a, b):
  return a * np.exp(b * x)

# Generate some data points.
x_data = np.linspace(0, 10, 100)
y_data = exponential_function(x_data, 2, 3)

# Add some noise to the data.
y_data += np.random.normal(0, 0.1, size=len(y_data))

# Fit the data to an exponential function.
popt, pcov = curve_fit(exponential_function, x_data, y_data)

# Print the fitted parameters.
print(popt)

# Plot the data and the fitted function.
plt.plot(x_data, y_data, 'o')
plt.plot(x_data, exponential_function(x_data, *popt))
plt.show()
