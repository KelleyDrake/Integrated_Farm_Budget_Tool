from cost import Cost

# Note: tests may fail if changes are made to the data textfile


def test_total_cost():
    c = Cost(2023)
    total_cost = c.total_cost()
    assert total_cost == 6757673

    total_cost = c.total_cost(yf=0.6)
    assert total_cost == 6319587

    total_cost = c.total_cost(yf=0.9)
    assert total_cost == 6648151
