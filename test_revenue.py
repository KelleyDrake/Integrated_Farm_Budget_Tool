from revenue import Revenue

# Note: tests may fail if changes are made to the data textfile


def test_total_revenue():
    rev = Revenue(2023)
    total_revenue = rev.total_revenue(1, 1)
    assert total_revenue == 9935986

    total_revenue = rev.total_revenue(yf=0.4)
    assert total_revenue == 4177886

    total_revenue = rev.total_revenue(pf=0.6)
    assert total_revenue == 9134646

    total_revenue = rev.total_revenue(.9, .9)
    assert total_revenue == 8867769
