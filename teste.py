import numpy as np
import uaibot as ub

robot = ub.Robot.create_kuka_kr5()
sim = ub.Simulation([robot])

#Vamos fazer a primeira junta variar de 0 até 2*pi, enquanto as outras continuam em
# zero. O tempo irá variar de 0,01 em 0,01 segundos, até 10 segundos.
dt=0.01
tmax=10
for i in range(round(tmax/dt)):
    t = i*dt
    robot.add_ani_frame(time = t, q = [ (2*np.pi)*t/tmax, 0, 0, 0, 0, 0])

#Vamos ver o resultado
sim.run()