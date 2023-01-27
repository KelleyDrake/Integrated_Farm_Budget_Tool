# crop_insurance_tool

A tool for midwest grain farmers to help evaluate farm payment and crop insurance decisions in terms of their overall cash flow.

The current implementation is under development with a goal of verifying this Python codebase against Kelley's benchmarking.xlsx Excel workbook.  Once the logic has been validated, the plan is to build a publicly available web application, possibly in Django.  Once registered, a farmer could enter/upload his or her farm-specific data and select options for farm plan and crop insurance to maximize cash flow while minimizing risk.

At this point only the revenue component is complete (but untested).  The other four components will be built shortly.

## Prerequisites 

- [Python 3.10 or above](https://www.python.org/)
- [pip (Python package manager](https://pip.pypa.io/en/stable/installation/)
- [git version control](https://git-scm.com/downloads)
- [tabulate](https://pypi.org/project/tabulate/) `pip install tabulate`

## Installation

`git clone https://github.com/ddrake/crop_insurance_tool.git`

## Usage

In Python console or ipython console:

To see the revenue sensitivity table for 2023:
`from sensitivity import sens_revenue`
`sens_revenue(2023)`

To compute a single cell of the table (or test arbitrary factors): 
`from revenue import Revenue`
`r = Revenue(2023)`
`r.total_revenue(price_factor=.95, yield_factor=1.05)`

## Project collaborators

- Kelley Drake
- Dow Drake
- Bennett Drake
- Bennett's colleagues (to be named soon)

