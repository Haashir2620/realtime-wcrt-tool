class Task:
    def __init__(self, name, C, T , D):
        self.name = name
        self.C = float(C)
        self.T = float(T)
        self.D = float(D)

    def __repr__(self):
        return f"Task(name={self.name}, C={self.C}, T={self.T}, D={self.D})"