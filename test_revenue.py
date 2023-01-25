from revenue import Revenue


def test_total_revenue():
    rev = Revenue(2023)
    total_revenue = rev.total_revenue(1, 1)
    assert total_revenue == 9940729

    total_revenue = rev.total_revenue(.9, .9)
    assert total_revenue == 8131679
