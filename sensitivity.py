"""
Module sensitivity


"""
from tabulate import tabulate
from revenue import Revenue


def sens_revenue(crop_year):
    """
    Display a sensitivity table for the specified crop year
    for straightforward comparison with the revenue table
    in 'benchmarks.xls!KeyInputs'
    """
    yield_pcts = "40 55 70 80 90 95 100 105".split()
    price_pcts = "60 75 90 95 100 105 110 125 140 165 180".split()

    yield_pct_labels = [p+'%' for p in yield_pcts]
    price_pct_labels = [p+'%' for p in price_pcts]

    yield_pcts = [int(p)/100 for p in yield_pcts]
    price_pcts = [int(p)/100 for p in price_pcts]

    r = Revenue(2023)

    ny = len(yield_pcts)

    # Compute sensitivity data (8 yield values, 11 price values)
    data = [['']*3 + [round(r.total_revenue(p, y)/1000) for y in yield_pcts]
            for p in price_pcts]

    # add 3 empty rows for headers
    table = [['']*(3+ny)] + [['']*(3+ny)] + [['']*(3+ny)] + data

    # add header text
    table[0][0] = 'REVENUE'
    table[0][1] = 'Yield'
    table[1][0] = 'Price'
    table[0][2] = 'Corn'
    table[1][2] = 'Beans'
    table[2][0] = 'Corn'
    table[2][1] = 'Beans'
    table[2][2] = '%'

    # Row headers at left
    for i, p in enumerate(price_pcts):
        table[3+i][0] = round(p * r.fall_futures_price_corn, 2)
        table[3+i][1] = round(p * r.fall_futures_price_soy, 2)
        table[3+i][2] = price_pct_labels[i]

    # Column headers along top
    for i, p in enumerate(yield_pcts):
        table[0][3+i] = round(p * r.proj_yield_farm_corn, 1)
        table[1][3+i] = round(p * r.projected_yield_soy(), 1)
        table[2][3+i] = yield_pct_labels[i]

    print(tabulate(table, tablefmt="simple_grid"))
