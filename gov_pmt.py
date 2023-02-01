"""
Module gov_pmt

Contains a single class, GovPmt, which loads its data from a text file
for a given crop year when an instance is created.  Its main function
is to return total estimated cost for the farm for the given crop year
corresponding to arbitrary sensitivity factors for price and yield.
"""


class GovPmt(object):
    """
    Computes total estimated cost for the farm crop year
    corresponding to arbitrary sensitivity factors for price and yield.

    Sample usage in a python or ipython console:
      from gov_pmt import GovPmt
      p = GovPmt(2023)
      print(p.total_pmt() # pf and yf default to 1
      print(p.total_pmt(.9, 1.1) # specifies both price and yield factors
      print(p.total_pmt(yf=1.2) # uses default for pf
    """

    PLC = 1
    ARC_CO = 2

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
        cost_data = self._load_textfile(f'{self.crop_year}_gov_pmt_data.txt')

        return (farm_data + cost_data)

    def _load_textfile(self, filename):
        """
        Load a textfile with the given name into a list of key/value pairs,
        ignoring blank lines and comment lines that begin with '#'
        """
        with open(filename) as f:
            contents = f.read()

        lines = contents.strip().split('\n')
        lines = filter(lambda line: len(line) > 0 and line[0] != '#',
                       [line.strip() for line in lines])
        return [line.split() for line in lines]

    def c(self, s, crop):
        """
        Helper to simplify syntax for reading crop-dependent attributes
        imported from textfile
        """
        return getattr(self, f'{s}_{crop}')

    def assumed_mya_price(self, crop, pf=1):
        """
        Marketing Year Avg Price with price factor (Y38:AA38 -> AR16:AT16)
        """

        return (self.c('fut_price', crop) * pf -
                self.c('decrement_from_futures_to_mya', crop))

    def net_payment_acres(self, crop):
        """
        Net Payment Acres (85 percent of base) (Y10:AA10)
        """
        return (self.base_to_net_pmt_frac *
                self.c('farm_base_acres', crop))

    # PLC
    # ---
    def effective_price(self, crop, pf=1):
        """
        The effective price (Y18:AA18)
        The maximum of the national MYA price and the loan rate
        """
        return max(self.c('natl_loan_rate', crop),
                   self.assumed_mya_price(crop, pf))

    def effective_ref_rate(self, crop):
        """
        The effective reference rate (Y15:AA15)
        max(statutory reference rate (farm bill),
            min(statutory reference rate with new escalator,
                statutory reference rate (farm bill) * rate_cap_factor))
        """
        return max(self.c('stat_ref_rate_farm_bill', crop),
                   min(self.c('stat_ref_rate_new_escal', crop),
                       self.rate_cap_factor_new_escal *
                       self.c('stat_ref_rate_farm_bill', crop)))

    def plc_payment_rate1(self, crop, pf=1):
        """
        Helper for plc_payment rate (Y19:AA19)
        """
        return max(self.effective_ref_rate(crop) - self.effective_price(crop, pf), 0)

    def max_plc_payment_rate(self, crop):
        """
        The maximum PLC payment rate (Y20:AA20)
        """
        return (self.c('stat_ref_rate_farm_bill', crop) -
                self.c('natl_loan_rate', crop))

    def plc_payment_rate(self, crop, pf=1):
        """
        the PLC payment rate (Y21:AA21)
        """
        return min(self.plc_payment_rate1(crop, pf),
                   self.max_plc_payment_rate(crop))

    def farm_plc_yield(self, crop):
        """
        Farm PLC yield (bushels/base acres) [156 Farm Records](L56, O56, R56)
        """
        return (self.c('farm_plc_bu', crop) /
                self.c('farm_base_acres', crop))

    def plc_pmt_pre_sequest(self, crop, pf=1):
        """
        PLC payment for crop, pre-sequestration (Y23:AA23)
        """
        return (self.plc_payment_rate(crop, pf) * self.net_payment_acres(crop) *
                self.farm_plc_yield(crop))

    # ARC-CO
    # ------
    def arc_bmk_county_revenue(self, crop):
        """
        Arc Benchmark County Revenue (Y35:AA35)
        """
        return (self.c('arc_price', crop) *
                self.c('arc_yield', crop))

    def arc_capped_bmk_revenue(self, crop):
        """
        Arc 10 percent cap on Benchmark County Revenue (Y43:AA43)
        """
        return (self.arc_bmk_county_revenue(crop) *
                self.cap_on_bmk_cty_rev)

    def arc_guar_revenue(self, crop):
        """
        Guarantee Revenue 86 percent of Benchmark County (Y36:AA36)
        """
        return (self.arc_bmk_county_revenue(crop) * self.guar_rev_frac)

    def county_rma_yield(self, crop, yf=1):
        """
        County actual/est yield (RMA) (Y40:AA40) -> (AR25:AT25)
        """
        return self.c('est_county_yield', crop) * yf

    def actual_crop_revenue(self, crop, pf=1, yf=1):
        """
        Actual crop revenue (Y41:AA41)
        """
        return (max(self.assumed_mya_price(crop, pf),
                    self.c('natl_loan_rate', crop)) *
                self.county_rma_yield(crop, yf))

    def revenue_shortfall(self, crop, pf=1, yf=1):
        """
        Revenue shortfall (Y42:AA42)
        """
        return max(0, (self.arc_guar_revenue(crop) -
                       self.actual_crop_revenue(crop, pf, yf)))

    def arc_pmt_rate(self, crop, pf=1, yf=1):
        """
        ARC Payment rate (Y44:AA44)
        """
        return min(self.arc_capped_bmk_revenue(crop),
                   self.revenue_shortfall(crop, pf, yf))

    def arc_pmt_pre_sequest(self, crop, pf=1, yf=1):
        """
        ARC payment pre-sequestration (Y48:AA48)
        """
        return self.net_payment_acres(crop) * self.arc_pmt_rate(crop, pf, yf)

    # Government Payment Totals
    # -------------------------
    def prog_pmt_pre_sequest_crop(self, crop, pf=1, yf=1):
        """
        Government program pre-sequestration payment for crop (Y56:AA56)
        """
        return (self.arc_pmt_pre_sequest(crop, pf, yf)
                if self.c('program', crop) == GovPmt.ARC_CO else
                self.plc_pmt_pre_sequest(crop, pf))

    def prog_pmt_pre_sequest(self, pf=1, yf=1):
        """
        Government program pre-sequestration payment total (AB56)
        """
        return sum([self.prog_pmt_pre_sequest_crop(crop, pf, yf)
                    for crop in ['corn', 'soy', 'wheat']])

    def prog_pmt_post_sequest(self, pf=1, yf=1):
        """
        Government program post-sequestration payment total (AB58)
        """
        return self.prog_pmt_pre_sequest(pf, yf) * (1 - self.sequest_frac)

    def total_gov_pmt(self, pf=1, yf=1):
        """
        Total government payment after cap (AB60)
        """
        return round(
            min(self.prog_pmt_post_sequest(pf, yf), self.fsa_pmt_cap))
