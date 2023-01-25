"""
Module cost

Contains a single class, Cost, which loads its data from a text file
for a given crop year when an instance is created.  Its main function
is to return total estimated cost for the farm for the given crop year
corresponding to arbitrary sensitivity factors for price and yield.
"""


class Cost(object):
    """
    Parses a text file in the directory containing this class
    named e.g. "2023_cost_data.txt", which has all required
    budgeting cost data for a farm for a given crop year.

    Computes total estimated cost for the farm crop year
    corresponding to arbitrary sensitivity factors for price and yield.

    Sample usage in a python or ipython console:
      from cost import Cost
      c = Cost(2023)
      print(c.total_cost() # price_factor and yield_factor default to 1
      print(c.total_cost(.9, 1.1) # specifies both price and yield factors
      print(c.total_cost(yield_factor=1.2) # uses default for price_factor
    """
    def __init__(self, crop_year):
        self.items = self.load_for_crop_year(crop_year)

    def load_for_crop_year(self, crop_year):
        """
        Load individual cost items from data file
        ignoring lines that begin with '#' and blank lines
        """
        with open(f'{crop_year}_cost_data.txt') as f:
            contents = f.read()

        lines = filter(lambda line: line and line[0] != '#',
                       contents.strip().split('\n'))

        items = [line.strip().split() for line in lines]
        return {k: float(v) if '.' in v else int(v) for k, v in items}
