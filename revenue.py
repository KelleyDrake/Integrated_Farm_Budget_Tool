"""
Module revenue

Contains a single class, Revenue, which loads its data from a text file
for a given crop year when an instance is created.  Its main function
is to return total estimated revenue for the farm for the given crop year
corresponding to arbitrary sensitivity factors for price and yield.
"""


class Revenue(object):
    """
    Parses a text file in the directory containing this class
    named e.g. "2023_revenue_data.txt", which has all required
    budgeting revenue data for a farm for a given crop year.

    Computes total estimated revenue for the farm crop year
    corresponding to arbitrary sensitivity factors for price and yield.

    Sample usage in a python or ipython console:
      from revenue import Revenue
      r = Revenue(2023)
      print(r.total_revenue() # price_factor and yield_factor default to 1
      print(r.total_revenue(.9, 1.1) # specifies both price and yield factors
      print(r.total_revenue(yield_factor=1.2) # uses default for price_factor
    """

    def __init__(self, crop_year):

        # Get a dict with the textfile key/value data
        # and make object attributes from it.
        for k, v in self.load_for_crop_year(crop_year).items():
            setattr(self, k, v)

    def load_for_crop_year(self, crop_year):
        """
        Load individual revenue items from data file
        ignoring lines that begin with '#' and blank lines
        return a dict with all the key/value information
        """
        with open(f'{crop_year}_revenue_data.txt') as f:
            contents = f.read()

        lines = filter(lambda line: line and line[0] != '#',
                       contents.strip().split('\n'))

        items = [line.strip().split() for line in lines]
        return {k: float(v) if '.' in v else int(v) for k, v in items}

    def deliverable_bu_corn(self, yield_factor=1):
        """
        Estimated corn bushels with shrink and yield factor applied
        """
        ret = (self.acres_corn *
               self.proj_yield_farm_corn *
               (1 - self.est_shrink_corn/100.) * yield_factor)
        # print('deliverable_bu_corn', ret)
        return ret

    def estimated_soy_bushels(self):
        """
        Compute estimated raw total soy bushels
        considering wheat/dc soy acres
        """
        ret = (self.acres_wheat_dc_soy *
               self.proj_yield_farm_dc_soy +
               (self.acres_soy -
                self.acres_wheat_dc_soy) *
               self.proj_yield_farm_full_soy)
        # print('estimated_soy_bushels', ret)
        return ret

    def deliverable_bu_soy(self, yield_factor=1):
        """
        Estimated soy bushels with shrink and yield factor applied
        """
        ret = (self.estimated_soy_bushels() *
               (1 - self.est_shrink_soy/100.) * yield_factor)
        # print('deliverable_bu_soy', ret)
        return ret

    def revenue_uncontracted_crop(self, crop, price_factor=1, yield_factor=1):
        """
        Estimated revenue of uncontracted corn or soy for specified
        price_factor and yield_factor rounded to whole dollars
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        ret = round(
            ((self.deliverable_bu_corn(yield_factor) if crop == 'corn' else
              self.deliverable_bu_soy(yield_factor)) -
             getattr(self, f'contract_bu_{crop}')) *
            (getattr(self, f'fall_futures_price_{crop}') * price_factor +
             getattr(self, f'est_basis_{crop}')) *
            (1 - getattr(self, f'est_deduct_{crop}')/100.))
        # print("revenue_uncontracted_crop", crop, ret)
        return ret

    def revenue_uncontracted(self, price_factor=1, yield_factor=1):
        """
        Estimated revenue of uncontracted grain for specified
        price_factor and yield_factor in whole dollars
        """
        ret = sum(
            [self.revenue_uncontracted_crop(crop, price_factor, yield_factor)
             for crop in ['corn', 'soy']])
        # print('revenue_uncontracted', ret)
        return ret

    def revenue_contracted_crop(self, crop, price_factor=1):
        """
        Expected revenue from contracted corn or soy rounded to whole dollars
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        ret = round(
            getattr(self, f'contract_bu_{crop}') *
            getattr(self, f'avg_contract_price_{crop}') *
            (1 - getattr(self, f'est_deduct_{crop}')/100.) *
            price_factor)
        # print('revenue_contracted_crop', crop, ret)
        return ret

    def revenue_contracted(self, price_factor=1):
        """
        Expected revenue from contracted grain in whole dollars
        """
        ret = sum([self.revenue_contracted_crop(crop, price_factor)
                  for crop in ['corn', 'soy']])
        # print('revenue_contracted', ret)
        return ret

    def total_revenue_crop(self, crop, price_factor=1, yield_factor=1):
        """
        Convenience method providing total revenue for a given
        crop based on price and yield factors
        """
        if crop not in ['corn', 'soy', 'wheat']:
            raise ValueError("crop must be 'corn', 'soy' or 'wheat'")
        ret = (self.revenue_wheat if crop == 'wheat' else
               self.revenue_contracted_crop(crop, price_factor) +
               self.revenue_uncontracted_crop(
                   crop, price_factor, yield_factor))
        # print('total_revenue_crop', crop, ret)
        return ret

    def total_revenue_other(self):
        """
        Total of other revenue *excluding* government program payments
        """
        ret = sum([getattr(self, f'ppp_loan_forgive_{crop}') +
                   getattr(self, f'mfp_cfap_{crop}') +
                   getattr(self, f'rental_revenue_{crop}') +
                   getattr(self, f'other_revenue_{crop}')
                   for crop in ['corn', 'soy']])
        # print('total_revenue_other', ret)
        return ret

    def total_revenue(self, price_factor=1, yield_factor=1):
        """
        Total revenue reflecting current estimates and price/yield factors
        """
        return sum([self.revenue_wheat,
                    self.revenue_uncontracted(price_factor, yield_factor),
                    self.revenue_contracted(price_factor),
                    self.total_revenue_other()])
