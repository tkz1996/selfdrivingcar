class PD:
    def __init__(self, naturalFreq = 1.25, dampingRatio = 1, dtLength = 2):
        #S^2 + kvS + kp = 0, characteristic eqn, S^2 + 2EWnS + Wn^2 = 0
        #kv = kd (both in terms of dt, velocity by definition)
        self.kp = naturalFreq ** 2
        self.kd = 2 * dampingRatio * naturalFreq
        self.prevAngle = 0
        self.currAngle = 0
        self.dt = 1/dtLength
    
    def control(self, newAngle): #newG is new steering angle
        self.currAngle = newAngle
        dEdT = (self.currAngle - self.prevAngle) / self.dt
        steeringAngle = self.kp*self.currAngle + self.kd*dEdT
        self.prevAngle = self.currAngle
        return steeringAngle