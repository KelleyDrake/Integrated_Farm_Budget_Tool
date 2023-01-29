"""
Module cost

Contains a single class, Cost, which loads its data from a text file
for a given crop year when an instance is created.  Its main function
is to return total estimated cost for the farm for the given crop year
corresponding to an arbitrary sensitivity factor for yield.
"""


class Cost(object):
    """
    Parses a text file in the directory containing this class
    named e.g. "2023_cost_data.txt", which has all required
    budgeting cost data for a farm for a given crop year.

    Computes total estimated cost for the farm crop year
    corresponding to arbitrary sensitivity factor for yield.

    Sample usage in a python or ipython console:
      from cost import Cost
      c = Cost(2023)
      print(c.total_cost()    # yield_factor defaults to 1
      print(c.total_cost(1.1) # specifies both price and yield factors
    """
    def __init__(self, crop_year):
        """
        Get an instance for the given crop year, then get a list of
        key/value pairs from the text file and make object attributes from it.
        """
        self.crop_year = crop_year
        for k, v in self.load_for_crop_year():
            setattr(self, k, float(v) if '.' in v else int(v))

    def load_for_crop_year(self):
        """
        Load individual revenue items from data file
        ignoring lines that begin with '#' and blank lines
        return a list with all the key/value pairs
        """
        with open(f'{self.crop_year}_cost_data.txt') as f:
            contents = f.read()

        lines = filter(lambda line: line and line[0] != '#',
                       contents.strip().split('\n'))

        return [line.strip().split() for line in lines]

    def proj_yield_farm_crop(self, crop):
        """
        Helper method providing projected yields for all crops
        used in calculating fuel and payroll costs
        """
        if crop not in ['corn', 'soy', 'wheat']:
            raise ValueError("crop must be 'corn', 'soy' or 'wheat'")

        return (
            ((self.acres_wheat_dc_soy *
              self.proj_yield_farm_dc_soy +
              (self.acres_soy -
               self.acres_wheat_dc_soy) *
              self.proj_yield_farm_full_soy) / self.acres_soy)
            if crop == 'soy' else self.proj_yield_farm_corn
            if crop == 'corn' else self.proj_yield_farm_wheat)

    # VARIABLE COSTS
    # --------------

    # FERTILIZER
    # ----------
    def yield_dep_repl_fert_crop(self, crop, yield_factor=1):
        """
        Yield-dependent replacement fertilizer for corn or soy
        scaled by yield_factor
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        return round(
            (getattr(self, f'dap_{crop}') +
             getattr(self, f'repl_potash_{crop}')) * yield_factor)

    def yield_dep_repl_fert(self, yield_factor=1):
        """
        Yield-dependent replacement fertilizer for crops
        """
        return sum([self.yield_dep_repl_fert_crop(crop, yield_factor)
                    for crop in ['corn', 'soy']])

    def yield_indep_repl_fert_crop(self, crop):
        """
        Yield-dependent replacement fertilizer for corn or soy
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        return round(
            getattr(self, f'cur_est_fertiilizer_cost_{crop}') -
            self.yield_dep_repl_fert_crop(crop, yield_factor=1))

    def yield_indep_repl_fert(self):
        """
        Yield-dependent replacement fertilizer for crops
        """
        return sum([self.yield_indep_repl_fert_crop(crop)
                    for crop in ['corn', 'soy']])

    def total_fert_crop(self, crop, yield_factor=1):
        """
        Total fertilizer cost for specified crop and optional yield_factor
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        return (self.yield_indep_repl_fert_crop(crop) +
                self.yield_dep_repl_fert_crop(crop, yield_factor))

    def total_fert(self, yield_factor=1):
        """
        Total fertilizer cost with optional yield_factor
        """
        return sum(
            [self.total_fert_crop(crop, yield_factor)
             for crop in ['corn', 'soy']])

    # INCREMENTAL WHEAT
    # -----------------

    def incremental_wheat_cost(self, yield_factor=1):
        """
        Only the shipping component of incremental wheat
        is sensitized to yield
        """
        return round(
            self.incremental_wheat_cost_base +
            self.wheat_hauling_base * (yield_factor - 1))

    # DIESEL FUEL
    # -----------
    def clear_diesel_base_cost_crop(self, crop):
        """
        The base cost of clear diesel for the specified crop
        used to compute the clear diesel cost for the crop
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        return (
            self.clear_gpa_2018 * getattr(self, f'acres_{crop}') *
            self.clear_diesel_price * getattr(self, f'fuel_alloc_{crop}'))

    def clear_diesel_cost_crop(self, crop, yield_factor=1):
        """
        The clear diesel cost for the specified crop.  Only the part
        of clear diesel allocated to hauling is scaled by yield.
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        return round(
            self.clear_diesel_base_cost_crop(crop) *
            ((1 - self.est_haul_alloc) +
             self.est_haul_alloc * self.proj_yield_farm_crop(crop) /
             getattr(self, f'yield_2018_{crop}') * yield_factor))

    def dyed_diesel_cost_crop(self, crop):
        """
        The dyed diesel cost for the specified crop
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        return round(
            self.dyed_gpa_2018 * getattr(self, f'acres_{crop}') *
            self.dyed_diesel_price * getattr(self, f'fuel_alloc_{crop}'))

    def diesel_cost_crop(self, crop, yield_factor=1):
        """
        The diesel cost for the specified crop with optional yield_factor
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        return (self.clear_diesel_cost_crop(crop, yield_factor) +
                self.dyed_diesel_cost_crop(crop))

    def diesel_cost(self, yield_factor=1):
        """
        The total diesel cost with optional yield_factor
        """
        return sum([self.diesel_cost_crop(crop, yield_factor)
                    for crop in ['corn', 'soy']])

    # GAS AND ELECTRICITY
    # -------------------
    def gas_electric_cost_crop(self, crop, yield_factor=1):
        """
        The gas and electric cost for the crop, scaled by yield
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        return round(getattr(self, f'gas_electric_{crop}') * yield_factor)

    def gas_electric_cost(self, yield_factor=1):
        """
        The overall gas and electric cost scaled by yield
        """
        return (sum([self.gas_electric_cost_crop(crop, yield_factor)
                     for crop in ['corn', 'soy']]))

    # TOTALS
    # ------
    def total_variable_cost_crop(self, crop, yield_factor=1):
        """
        The total variable cost for the crop, scaled by yield.
        """
        if crop not in ['corn', 'soy', 'wheat']:
            raise ValueError("crop must be 'corn', 'soy' or 'wheat'")

        return (
            self.incremental_wheat_cost(yield_factor) if crop == 'wheat'
            else (
                getattr(self, f'seed_plus_treatment_{crop}') +
                getattr(self, f'chemicals_{crop}') +
                getattr(self, f'wind_peril_premium_{crop}') +
                getattr(self, f'minus_wind_peril_indemnity_{crop}') +
                self.total_fert_crop(crop, yield_factor) +
                self.diesel_cost_crop(crop, yield_factor) +
                self.gas_electric_cost_crop(crop, yield_factor)))

    def total_variable_cost(self, yield_factor=1):
        """
        The total of variable costs, scaled by yield
        """
        return sum([self.total_variable_cost_crop(crop, yield_factor)
                    for crop in ['corn', 'soy', 'wheat']])

    # OVERHEAD
    # --------

    # PAYROLL
    # -------
    def payroll_crop(self, crop, yield_factor=1):
        """
        The overtime portion of the payroll is scaled by the ratio of
        estimated yield (including yield_factor) to 2018 yield.
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        return round(
            self.est_payroll * getattr(self, f'payroll_alloc_{crop}') *
            (1 + self.payroll_pct_ot *
             (self.proj_yield_farm_crop(crop) * yield_factor /
              getattr(self, f'yield_2018_{crop}') - 1)))

    def total_payroll(self, yield_factor=1):
        """
        The total payroll cost, with overtime scaled by yield
        """
        return sum([self.payroll_crop(crop, yield_factor)
                    for crop in ['corn', 'soy']])

    # TOTALS
    # ------
    def total_overhead_crop(self, crop, yield_factor=1):
        """
        The total of all overhead items for the given crop, scaled by yield
        """
        if crop not in ['corn', 'soy']:
            raise ValueError("crop must be 'corn' or 'soy'")

        return (
            self.payroll_crop(crop, yield_factor) +
            getattr(self, f'replacement_capital_{crop}') +
            getattr(self, f'building_equip_repairs_{crop}') +
            getattr(self, f'shop_tools_supplies_parts_{crop}') +
            getattr(self, f'business_insurance_{crop}') +
            getattr(self, f'other_utilities_{crop}') +
            getattr(self, f'professional_fees_{crop}') +
            getattr(self, f'other_operating_expense_{crop}') +
            getattr(self, f'total_land_expenses_{crop}'))

    def total_overhead(self, yield_factor=1):
        """
        The total overhead cost, scaled by yield
        """
        return sum([self.total_overhead_crop(crop, yield_factor)
                    for crop in ['corn', 'soy']])

    def total_cost(self, yield_factor=1):
        """
        The total cost, scaled by yield
        """
        return (self.total_variable_cost(yield_factor) +
                self.total_overhead(yield_factor))
