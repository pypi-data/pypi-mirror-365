# === LINEAR REGRESSION ALGORITHM ===
# https://github.com/hurtki/DataSince

from .gradient_descent import gradient_descent_3d

class LinearRegression:
    def __init__(self):
        self.X = []
        self.y = []
        self.coef = 0
        self.intercept = 0
    
    # function to fit the model to the inout data 
    def fit(self, X: list[float], y: list[float]):
        self.X = X
        self.y = y
        start = (0.0, 0.0)   
        learning_rate = 0.01
        iterations = 1000
        time_log = 0
        coef, intercept = gradient_descent_3d(self.__nigzeret, start, learning_rate, iterations, time_log)
        self.coef, self.intercept = round(coef, 2), round(intercept, 2)

        print(f"Learning ended succsesfully. finall parametres: w={self.coef}, b={self.intercept}")

    def score(self) -> float:
        """
        returns R**2 of the Linear Regression model 
        """
        return 0.0

    # predict for one number 
    def __predict_single(self, x:float, w:float, b:float) -> float:
        return x * w + b
    
    def __predict(self, X:list[float], w, b:float) -> list[float]:
        if isinstance(X, list):
            return [self.__predict_single(n, w, b) for n in X]
        else:
            raise Exception("X should be a list of numerics")

            
    # loss counter 
    def __loss(self, X, y: list[float], w: float, b: float) -> float:
        if isinstance(X, list) and isinstance(y, list):
            preds = [self.__predict_single(xi, w, b) for xi in X]
            return sum((pi - yi) ** 2 for pi, yi in zip(preds, y)) / len(X)
        else:
            raise Exception("X and Y should be a list of numerics")

    def __gradient(self, X: list, y: list, w:float, b:float) -> tuple[float, float]:
        if not (isinstance(X, list) and isinstance(y, list)):
            raise Exception("X and Y should be a list of numerics")
        
        if len(X) != len(y):
            raise ValueError("X and y must have the same length")
        
        preds = self.__predict(X, w, b)
        n = len(X)
        errors = [preds[i] - y[i] for i in range(n)]

        w_gradient = 2 * sum(X[i] * errors[i] for i in range(n)) / n
        b_gradient = 2 * sum(errors) / n
        
        return (w_gradient, b_gradient)
        
    def __nigzeret(self, params: tuple[float, float]) -> tuple[float, float]:
        w, b = params
        return self.__gradient(self.X, self.y, w, b)
    