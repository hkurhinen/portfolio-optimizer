import numpy as np
import pandas as pd
from pandas_datareader import data
from desdeo_problem import variable_builder, ScalarObjective, MOProblem, ScalarConstraint
from desdeo_emo.EAs.NSGAIII import NSGAIII
from desdeo_emo.EAs.RVEA import RVEA

class Portfolio:
  def __init__(self, assets, start, end):
    self.assets = assets
    self.df = data.DataReader(assets, 'yahoo', start=start, end=end)
    self.df = self.df['Adj Close']
    self.cov_matrix = self.df.pct_change().apply(lambda x: np.log(1+x)).cov()
    self.corr_matrix = self.df.pct_change().apply(lambda x: np.log(1+x)).corr()
    self.ind_er = self.df.resample('Y').last().pct_change().mean()

  def returns(self, x):
      weights = x/np.sum(x)
      r = np.dot(weights, self.ind_er)
      return -1 * r

  def variance(self, x):
    weights = x/np.sum(x)
    var = self.cov_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()
    sd = np.sqrt(var)
    return sd*np.sqrt(250)

  def returns_along_axis(self, x):
      return np.apply_along_axis(self.returns, 1, x)

  def variance_along_axis(self, x):
      return np.apply_along_axis(self.variance, 1, x)

  def get_percentages(self, x):
      t = np.sum(x)
      return [x[0] / t, x[1] / t, x[2] / t, x[3] / t]

  def optimize(self, algorithm, population_size, n_gen_per_iter, n_iterations):
    decision_variables = variable_builder(self.assets,
      initial_values=np.full(len(self.assets), 25.0),
      lower_bounds=np.full(len(self.assets), 0.0),
      upper_bounds=np.full(len(self.assets), 100.0))

    objective_functions = [
      ScalarObjective(name='Returns', evaluator=self.returns_along_axis),
      ScalarObjective(name='Variance', evaluator=self.variance_along_axis)]

    problem = MOProblem(
      variables=decision_variables, 
      objectives=objective_functions)

    if (algorithm == "RVEA"):
      evolver = RVEA(
        problem, 
        population_size=population_size,
        n_gen_per_iter=n_gen_per_iter,
        n_iterations=n_iterations)
    else:
      evolver = NSGAIII(
        problem,
        population_size=population_size,
        n_gen_per_iter=n_gen_per_iter,
        n_iterations=n_iterations)

    while evolver.continue_evolution():
      evolver.iterate()

    individuals, _ =  evolver.end()
    weights = np.apply_along_axis(self.get_percentages, 1, individuals)
    returns = self.returns_along_axis(weights)
    returns = returns * -1
    variance = self.variance_along_axis(weights)
    data = {
      'returns': returns, 
      'variance': variance
    }
    for counter, symbol in enumerate(self.df.columns.tolist()):
      data[symbol+'_weight'] = [w[counter] for w in weights]

    return pd.DataFrame(data)



