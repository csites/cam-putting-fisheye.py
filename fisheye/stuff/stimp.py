import matplotlib.pyplot as plt

def estimate_stimp(V_initial, V_final, Distance):
  """
  Estimates the stimp of a putting green based on the initial and final speed of a golf ball.

  Args:
    V_initial = initial_speed: The initial speed of the golf ball in feet per second.
    V_final = final_speed: The final speed of the golf ball in feet per second.
    Distance: The distance that the golf ball rolled in meters.

  Returns:
    The estimated stimp of the putting green.

  Discussion: 
    We have a golfball rolling acorss a mat.  The mat is soft and the ball sinks a small 
    amount into the mat elastically.  We need to compute the coefficient_of_rolling_first, and since the stimp 
    is proportional to the coefficient_of_rolling_friction, we multiply by a constant to get stimp.  As 
    complicated as the model is, the we can get a good estimate based on the simple formula,
    that COF = (V_initial^2 - V_final^2) / (2 * g * Distance * mass).
    And stimp = COF * conversion_constant. 

  """

  # Mass and radius of a golfball.  USGA Max weight=  1.620oz. (45.93).
  # Brand              Weight(oz) Weight(gm)   
  # Titleist Pro V1	        1.601	  45.64
  # Srixon Soft Feel	      1.469	  41.66 
  # Bridgestone e12 Contact	1.331	  37.75  * Lightest
  # Pinnacle Rush	          1.615	  45.80  
  # Kirkland 3-Piece Cover	1.67	  47.56  * Heaviest Illegal.
  # Taylormade Distance+	  1.615	  45.80
  # Top Flite XL Distance	  1.619  	45.90  * Heaviest Legal. 
  # Advantage	              1.615  	45.80
  # Wilson Triad	          1.5995	45.34
  # Titleist Reload Pro V1	1.6091	45.61
  # Dunlop	                1.6024	45.43
  # Callaway Chrome Soft X  1.611   45.67
  
  mass = 0.04564 # Pro V1 kg
  radius = 0.0427 # m

  # Acceleration due to gravity.
  acceleration_due_to_gravity = 9.81 # m/s²
  # Conversion factor for ft/m 
  ft_per_m = 3.28084 # ft/m
  
  # Moment of Inertia for a rolling sphere.
  # moment_of_inertia = (2/5) * mass * (radius ** 2)

  # Calculate the work done by friction. The work done by friction is the energy lost due to friction its negative.
  # work_done_by_friction = (1/2) * mass * (final speed)^2 - (1/2) * mass * (initial speed)^2 
  # work_done_by_friction = - (final_speed ** 2 - initial_speed ** 2) / 2 / mass * distance

  # Calculate the force of friction.  Interesting note: Work done by rolling = 0. 
  # force_of_friction = work_done_by_friction / distance

  # Calculate the coefficient of rolling friction.  This will be the normal of the sphere 
  # coefficient_of_rolling_friction = force_of_friction * (mass * acceleration_due_to_gravity * moment_of_inertia)
  # print("U_rolling_friction="+str(coefficient_of_rolling_friction))

  # Calculate the stimp in feet. Arbritrary convertion factor.
  # stimp = (0.8200 * distance * 0.00218499635) / (coefficient_of_rolling_friction)
  
  # Convert the stimp from feet to unitless.
  # stimp = distance / stimp 
  
  # Multiply the stimp by 2.5.
  # stimp = stimp / 2.5

  # THe stimp coversion constant is g * correction_factor / 2 * 12.   
  coefficient_of_rolling_friction = (V_final ** 2 - V_initial ** 2) / (2 * g * Distance * mass)
  stimp =  0.411576129655555 / abs(coefficient_of_rolling_friction)
  return stimp 

distances = [6, 7, 8, 10, 11, 12, 13, 14]
stimpse = []

for distance in distances:
  distance = distance * 0.3048 # m/ft.
  stimp = estimate_stimp(6.32 * 0.3048, 0, distance)
  print("distance="+str(distance)+" stimp="+str(stimp))
  stimpse.append(stimp)

#plt.plot(distances, stimpse)
#plt.xlabel("Distance (ft)")
#plt.ylabel("Stimp")
#plt.title("Stimp vs. Distance")
#plt.show()
