"""
Module net_indemnity

Contains a single class, NetIndemnity, which loads its data from a text file
for a given crop year when an instance is created.  Its main function
is to return total estimated net indemnity payment to be made to the farm
for the given crop year
corresponding to arbitrary sensitivity factors for price and yield.
"""


class NetIndemnity(object):
    """
    Parses a text file in the directory containing this class
    named e.g. "2023_net_indemnity_data.txt", which has all required
    net indemnity data for a farm for a given crop year.

    Computes total net indemnity payment to the farm for the crop year
    corresponding to arbitrary sensitivity factors for price and yield.

    Sample usage in a python or ipython console:
      from net_indemnity import NetIndemnity
      p = NetIndemnity(2023)
      print(p.total_pmt() # price_factor and yield_factor default to 1
      print(p.total_pmt(.9, 1.1) # specifies both price and yield factors
      print(p.total_pmt(yield_factor=1.2) # uses default for price_factor
    """
    def __init__(self, crop_year):
        self.items = self.load_for_crop_year(crop_year)

    def load_for_crop_year(self, crop_year):
        """
        Load individual net indemnity items from data file
        ignoring lines that begin with '#' and blank lines
        """
        with open(f'{crop_year}_net_indemnity_data.txt') as f:
            contents = f.read()

        lines = filter(lambda line: line and line[0] != '#',
                       contents.strip().split('\n'))

        items = [line.strip().split() for line in lines]
        return {k: float(v) if '.' in v else int(v) for k, v in items}
