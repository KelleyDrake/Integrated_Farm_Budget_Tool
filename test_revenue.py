from revenue import Revenue


def test_total_revenue():
    rev = Revenue(2023)
    total_revenue = rev.total_revenue(1, 1)
    assert total_revenue == 9935986

    total_revenue = rev.total_revenue(yield_factor=0.4)
    assert total_revenue == 4177886

    total_revenue = rev.total_revenue(price_factor=0.6)
    assert total_revenue == 9134646

    total_revenue = rev.total_revenue(.9, .9)
    assert total_revenue == 8867769


