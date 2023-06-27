def coefficient_of_rolling_friction(initial_velocity, final_velocity, distance, mass, radius):
  """
  Calculates the coefficient of rolling friction for a golf ball rolling on a carpet.

  Args:
    initial_velocity: The initial velocity of the golf ball in meters per second.
    final_velocity: The final velocity of the golf ball in meters per second.
    distance: The distance traveled by the golf ball in meters.
    mass: The mass of the golf ball in kilograms.
    radius: The radius of the golf ball in meters.

  Returns:
    The coefficient of rolling friction.
  """

  g = 9.8  # m/s^2
  return (final_velocity ** 2 - initial_velocity ** 2) / (2 * g * distance * mass)

def estimate_stimp(coefficient_of_rolling_friction):
  """
  Converts the coefficient of rolling friction to stimp.  If your curious the 2 * 12 = 24.  2 is because
  the ball sinks into the mat, and has friction forward and back of the normal of g.    

  Args:
    coefficient_of_rolling_friction: The coefficient of rolling friction.

  Returns:
    The stimp in feet per second.
  """

  return  0.411576129655555 / abs(coefficient_of_rolling_friction)

if __name__ == "__main__":
  initial_velocity = 6.32 * 0.3048  # m/s
  final_velocity = 0 * 0.3048  # m/s
  mass = 0.46  # kg
  radius = 0.042  # m

  distances = [6, 7, 8, 9, 10, 11, 12, 13, 14]
  coefficients_of_rolling_friction = []
  stimps = []

  for distance in distances:
    acoefficient_of_rolling_friction = coefficient_of_rolling_friction(initial_velocity, final_velocity, distance, mass, radius)
    coefficients_of_rolling_friction.append(acoefficient_of_rolling_friction)
    stimps.append(estimate_stimp(acoefficient_of_rolling_friction))

  print("Coefficients of rolling friction:", coefficients_of_rolling_friction)
  print("Stimps:", stimps)

  import matplotlib.pyplot as plt

  plt.plot(distances, coefficients_of_rolling_friction, "+")
  plt.plot(distances, stimps, "o")	
  plt.xlabel("Distance (ft)")
  plt.ylabel("Coefficient of rolling friction")
  plt.show()
