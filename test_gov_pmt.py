from gov_pmt import GovPmt

# Note: tests may fail if changes are made to the data textfile,
# but changes to program selections are OK.


def test_total_gov_pmt():
    g = GovPmt(2023)

    g.program_corn = GovPmt.ARC_CO
    g.program_soy = GovPmt.ARC_CO
    g.program_wheat = GovPmt.ARC_CO

    total_gov_pmt = g.total_gov_pmt(1, 1)
    assert total_gov_pmt == 0

    total_gov_pmt = g.total_gov_pmt(0.6)
    assert total_gov_pmt == 145655

    total_gov_pmt = g.total_gov_pmt(yf=0.55)
    assert total_gov_pmt == 358497

    total_gov_pmt = g.total_gov_pmt(.75, .8)
    assert total_gov_pmt == 83012
