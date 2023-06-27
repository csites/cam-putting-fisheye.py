import math
import matplotlib.pyplot as plt

def estimate_stimp(initial_speed, final_speed, distance):
  """
  Estimates the stimp of a putting green based on the initial and final speed of a golf ball over a segment.

  Args:
    initial_speed: The initial speed of the golf ball in feet per second.
    final_speed: The final speed of the golf ball in feet per second.
    distance: The distance that the golf ball rolled in feet.

  Returns:
    The estimated stimp of the putting green.
  """

  mass = 0.04564 # Pro V1 kg
  radius = 0.0427 # m
  density_of_air = 1.293 # kg m−3

  # Acceleration due to gravity.
  acceleration_due_to_gravity = 9.81 # m/s²

  # Moment of Inertia for a rolling sphere.
  moment_of_inertia = (2/5) * mass * (radius ** 2)

  # Calculate the work done by friction.
  work_done_by_friction = - (final_speed ** 2 - initial_speed ** 2) / 2 / mass * distance

  # Calculate the force of friction.
  force_of_friction = work_done_by_friction / distance

  # Calculate the normal force.
  normal_force = mass * acceleration_due_to_gravity

  # Calculate the buoyant force.
  buoyant_force = (4/3) * math.pi * radius ** 3 * density_of_air * acceleration_due_to_gravity

  # Calculate the coefficient of rolling friction.
  coefficient_of_rolling_friction = force_of_friction * (mass * acceleration_due_to_gravity * moment_of_inertia) / (work_done_by_friction * normal_force - buoyant_force)
  print("coefficient_of_rolling_friction = "+str(coefficient_of_rolling_friction))
  # Calculate the stimp.
  stimp = (0.8200 * distance * 0.00218499635) / coefficient_of_rolling_friction
  print("Test stimp = "+str(0.8200/coefficient_of_rolling_friction))
  return stimp

if __name__ == "__main__":
  initial_speed = 6.32 * 0.3048 # m/s
  final_speed = 0
  distances = [6, 7, 8, 10, 11, 12, 13, 14]
  stimpse = []

  for distance in distances:
    distance = distance * 0.3048 # m/ft.
    stimp = estimate_stimp(initial_speed, final_speed, distance)
    print("distance="+str(distance)+" stimp="+str(stimp))
    stimpse.append(stimp)

plt.plot(distances, stimpse)
plt.xlabel("Distance (ft)")
plt.ylabel("Stimp")
plt.title("Stimp vs. Distance")
plt.show()
