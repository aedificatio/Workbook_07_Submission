import math
from w_sections.columns import *

# testing data
LL_01 = Load(400000)      
ST_01 = SteelColumn(
    height=3000.0, 
    area=4525, 
    MoIx=25100000.0, 
    MoIy=9250000.0, 
    K_x=0.5, 
    K_y=0.5, 
    E=210000, 
    column_tag='HEA180', 
    axial_load = LL_01, 
    yield_stress=235, 
    gamma_m=1.0)
test_column_01 = ColumnDoublySymmetric(
        height=3000, 
        area=120000, 
        MoIx=1600000000.0, 
        MoIy=900000000.0, 
        K_x=1.0, 
        K_y=0.7, 
        E=20000
    )
test_column_02 = ColumnDoublySymmetric(
        height=0.0, 
        area=0.0, 
        MoIx=1600000000.0, 
        MoIy=900000000.0, 
        K_x=1.0, 
        K_y=0.7, 
        E=20000
    )


def test_create_load():
    test_data = ["24.6", "58.0"]
    assert isinstance(create_load(test_data), Load)
    assert create_load(test_data).dead == 24.6
    assert create_load(test_data).live == 58.0


def test_max_factored_load():
    test_load = Load(dead = 25.7, snow = 37.9, quake = 56.6)
    assert math.isclose(max_factored_load(test_load), 115.74, rel_tol=1e-09)


def test_calc_radius_of_gyration():
    assert math.isclose(test_column_01.calc_radius_of_gyration('x'), 115.47005383792515, rel_tol=1e-09)
    assert math.isclose(test_column_01.calc_radius_of_gyration('y'), 86.60254037844386, rel_tol=1e-09)
    
    
def test_calc_euler_buckling_load():
    assert math.isclose(test_column_01.calc_euler_buckling_load('x'), 35091926.75942883, rel_tol=1e-09)
    assert math.isclose(test_column_01.calc_euler_buckling_load('y'), 40284099.59628309, rel_tol=1e-09)
    

def test_factored_axial_capacity():
    assert math.isclose(ST_01.factored_axial_capacity('x'), 1057925.9442006957, rel_tol=1e-09)
    assert math.isclose(ST_01.factored_axial_capacity('y'), 980192.3571053795, rel_tol=1e-09)

    
def test_factored_dcr():
    assert math.isclose(ST_01.factored_dcr('x'), 0.453717958833743, rel_tol=1e-09)
    assert math.isclose(ST_01.factored_dcr('y'), 0.4896997987389895, rel_tol=1e-09)

    
def test_convert_row_to_col_data():
    test_row = ['C02', '22620.0', '2300.0', '1139000000.0', '271000000.0', '250', '200000.0', '0.7', '1.0', '389660.0', '287120.0']
    test_col = convert_row_to_col_data(test_row)
    assert test_col.column_tag == 'C02'
    assert isinstance(test_col.axial_load, Load)