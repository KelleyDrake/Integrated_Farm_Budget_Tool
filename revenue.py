"""
Module revenue

Contains a single class, Revenue, which loads its data from a text file
for a given crop year when an instance is created.  Its main function
is to return total estimated revenue for the farm for the given crop year
corresponding to arbitrary sensitivity factors for price and yield.
"""


class Revenue(object):
    """
    Computes total estimated revenue for the farm crop year
    corresponding to arbitrary sensitivity factors for price and yield.

    Sample usage in a python or ipython console:
      from revenue import Revenue
      r = Revenue(2023)
      print(r.total_revenue() # pf and yf default to 1
      print(r.total_revenue(.9, 1.1) # specifies both price and yield factors
      print(r.total_revenue(yf=1.2) # uses default for pf
    """

    def __init__(self, crop_year):
        """
        Get an instance for the given crop year, then get a list of
        key/value pairs from the text file and make object attributes from it.
        """
        self.crop_year = crop_year
        for k, v in self._load_required_data():
            setattr(self, k, float(v) if '.' in v else int(v))

    def _load_required_data(self):
        """
        Load individual revenue items from data file
        return a list with all the key/value pairs
        """
        farm_data = self._load_textfile(f'{self.crop_year}_farm_data.txt')
        cost_data = self._load_textfile(f'{self.crop_year}_revenue_data.txt')

        return (farm_data + cost_data)

    def _load_textfile(self, filename):
        """
        Load a textfile with the given name into a list of key/value pairs,
        ignoring blank lines and comment lines that begin with '#'
        """
        with open(filename) as f:
            contents = f.read()

        lines = filter(lambda line: line and line[0] != '#',
                       contents.strip().split('\n'))

        return [line.strip().split() for line in lines]

    def deliverable_bu_corn(self, yf=1):
        """
        Estimated corn bushels with shrink and yield factor applied
        """
        ret = (self.acres_corn *
               self.proj_yield_farm_corn *
               (1 - self.est_shrink_corn/100.) * yf)
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

    def projected_yield_soy(self):
        """
        Convenience method providing estimated overall soy yield
        """
        return self.estimated_soy_bushels() / self.acres_soy

    def deliverable_bu_soy(self, yf=1):
        """
        Estimated soy bushels with shrink and yield factor applied
        """
        ret = (self.estimated_soy_bushels() *
               (1 - self.est_shrink_soy/100.) * yf)
        # print('deliverable_bu_soy', ret)
        return ret

    def revenue_uncontracted_crop(self, crop, pf=1, yf=1):
        """
        Estimated revenue of uncontracted corn or soy for specified
        pf and yf rounded to whole dollars
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        ret = round(
            ((self.deliverable_bu_corn(yf) if crop == 'corn' else
              self.deliverable_bu_soy(yf)) -
             getattr(self, f'contract_bu_{crop}')) *
            (getattr(self, f'fall_futures_price_{crop}') * pf +
             getattr(self, f'est_basis_{crop}')) *
            (1 - getattr(self, f'est_deduct_{crop}')/100.))
        # print("revenue_uncontracted_crop", crop, ret)
        return ret

    def revenue_uncontracted(self, pf=1, yf=1):
        """
        Estimated revenue of uncontracted grain for specified
        pf and yf in whole dollars
        """
        ret = sum(
            [self.revenue_uncontracted_crop(crop, pf, yf)
             for crop in ['corn', 'soy']])
        # print('revenue_uncontracted', ret)
        return ret

    def revenue_contracted_crop(self, crop):
        """
        Expected revenue from contracted corn or soy rounded to whole dollars
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        ret = round(
            getattr(self, f'contract_bu_{crop}') *
            getattr(self, f'avg_contract_price_{crop}') *
            (1 - getattr(self, f'est_deduct_{crop}')/100.))
        # print('revenue_contracted_crop', crop, ret)
        return ret

    def revenue_contracted(self, pf=1):
        """
        Expected revenue from contracted grain in whole dollars
        """
        ret = sum([self.revenue_contracted_crop(crop)
                  for crop in ['corn', 'soy']])
        # print('revenue_contracted', ret)
        return ret

    def total_revenue_crop(self, crop, pf=1, yf=1):
        """
        Convenience method providing total revenue for a given
        crop based on price and yield factors
        """
        if crop not in ['corn', 'soy', 'wheat']:
            raise ValueError("crop must be 'corn', 'soy' or 'wheat'")
        ret = (self.revenue_wheat if crop == 'wheat' else
               self.revenue_contracted_crop(crop) +
               self.revenue_uncontracted_crop(
                   crop, pf, yf))
        # print('total_revenue_crop', crop, ret)
        return ret

    def total_revenue_grain(self, pf=1, yf=1):
        """
        Convenience method providing total grain revenue for the crop year
        based on price and yield factors
        """
        return sum([self.total_revenue_crop(crop, pf, yf)
                    for crop in ['corn', 'soy', 'wheat']])

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

    def total_revenue(self, pf=1, yf=1):
        """
        Total revenue reflecting current estimates and price/yield factors
        """
        return sum([self.revenue_wheat,
                    self.revenue_uncontracted(pf, yf),
                    self.revenue_contracted(),
                    self.total_revenue_other()])
