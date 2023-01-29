from cost import Cost


def test_total_revenue():
    c = Cost(2023)
    total_cost = c.total_cost()
    assert total_cost == 6757673

    total_cost = c.total_cost(yield_factor=0.6)
    assert total_cost == 6319587

    total_cost = c.total_cost(.9)
    assert total_cost == 6648151
