'''
This module reads profiles from a csv file and performs some calculations
- applies the unit_scalar to the profiles
- calculates factored load, axial resistance, demand/capacity ratio
'''
import pandas as pd
import numpy as np
from w_sections.columns import SteelColumn, Load


def read_profiles(csv_file: str) -> pd.core.frame.DataFrame:
    """
    Returns a pandas dataframe with IPE-profiles with units scaled correctly.
    """
    profiles = pd.read_csv(csv_file)
    for column in profiles.columns:
        if column != "Section name":
            pd.to_numeric(profiles[column], errors='coerce')

    # Units applied over multiple columns by function
    def apply_unitscalar(columns, scalar):
        """
        Returns None, applies unitscalar to a list of columns
        """
        profiles[columns] = profiles[columns] * scalar
        return
    apply_unitscalar(['iy', 'iz', 'Ss'], 10)

    # Units applied over multiple columns at once
    profiles[['A', 'Avz']] = profiles[['A', 'Avz']] * 100
    profiles[['Wel.y', 'Wpl.y', 'Wel.z', 'Wpl.z']] = profiles[['Wel.y', 'Wpl.y', 'Wel.z', 'Wpl.z']] * 1000

    # Units applied in a for loop per column
    for column in ['Iy', 'Iz', 'It']:
        profiles[column] = profiles[column] * 10000
    for column in ['Iw']:
        profiles[column] = profiles[column] * 1000000000

    return profiles


def sections_greater_than(profiles: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Returns a Dataframe with values greater than **kwargs based on a Dataframe
    """
    kw_masks = [profiles.loc[:, k] >= float(v) for k, v in kwargs.items()]
    mask = np.logical_and.reduce(kw_masks)    
    return profiles.loc[mask]


def sections_less_than(profiles: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Returns a Dataframe with values less than **kwargs based on a Dataframe
    """
    kw_masks = [profiles.loc[:, k] <= float(v) for k, v in kwargs.items()]
    mask = np.logical_and.reduce(kw_masks)    
    return profiles.loc[mask]


def sort_by_weight(profiles: pd.DataFrame, ascending=True, **kwargs) -> pd.DataFrame:
    """
    Return a Dataframe sorted by weight
    """
    sorted_profiles = profiles.sort_values("kg/m", ascending=ascending)
    return sorted_profiles


def create_steelcolumn(profile: pd.Series, height: float, fy: float = 235) -> SteelColumn:
    """
    Returns a SteelColumn object from a row of profiles representing a loaded column.
    """
    column_tag = profile['Section name']
    area = profile['A'].values[0]
    height = height
    MoIx = profile['Iy'].values[0]
    MoIy = profile['Iz'].values[0]
    fy = fy
    E = 210000
    kx = 1.0
    ky = 1.0
    
    column = SteelColumn(height = height, area = area, MoIx = MoIx, MoIy = MoIy,
                         K_x = kx, K_y = ky, E = E, column_tag = column_tag, yield_stress = fy)
    return column


def calculate_column_load(column: SteelColumn, deadload: float, liveload: float) -> tuple:
    """
    Function that takes a SteelColumn, a dead load, and a live load, and returns 
    a tuple representing the following data:
    (factored load, axial resistance, demand/capacity ratio)
    """
    deadload = deadload
    liveload = liveload
    
    load= Load(deadload, liveload)
    column.axial_load = load
    
    factored_load = column.factored_axial_load()
    axial_resistance = column.factored_axial_capacity(axis = 'x')
    DCR = column.factored_dcr(axis = 'x')
    
    return (factored_load, axial_resistance, DCR)


def calculate_columns(columns: list[SteelColumn], deadload: float, liveload: float) -> list[tuple]:
    """
    Function that takes a list[SteelColumn], a dead load, and a live load and 
    returns a list[tuple]. The returned list of tuples contains tuples where 
    each tuple represents the factored load, axial resistance, and 
    demand/capacity ratio generated from each corresponding SteelColumn
    """
    results = []
    for column in columns:
        result = calculate_column_load(column, deadload, liveload)
        results.append(result)
    return results


def calculate_steelcolumns(
        profiles: pd.DataFrame, 
        height: float, 
        fy: float, 
        deadload: float, 
        liveload: float
    ) -> pd.DataFrame:
    """
    Function that takes a DataFrame, a column height, a steel yield strength, a dead load and a live load.
    Returns the DataFrame with five new columns added:
    - Height
    - Dead
    - Live
    - Factored load
    - Axial Resistance
    - DCR (demand/capacity ratio)
    """
    profiles['Height'] = height
    profiles['Dead'] = deadload
    profiles['Live'] = liveload

    for section_name in profiles['Section name']:
        profile = profiles.loc[profiles['Section name'] == section_name]
        
        steel_column = create_steelcolumn(profile, height, fy)
        steel_column.axial_load = Load(dead=deadload, live=liveload)
        
        calc_column_load = calculate_column_load(steel_column, deadload, liveload)
        
        profiles.loc[profiles['Section name'] == section_name, 'Factored load'] = calc_column_load[0]
        profiles.loc[profiles['Section name'] == section_name, 'Axial Resistance'] = calc_column_load[1]
        profiles.loc[profiles['Section name'] == section_name, 'DCR'] = calc_column_load[2]

    return profiles

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
def calculate_steelcolumns_1(
        profiles: pd.DataFrame, 
        height: float, 
        fy: float, 
        deadload: float, 
        liveload: float
    ) -> pd.DataFrame:
    profiles['Height'] = height
    profiles['Dead'] = deadload
    profiles['Live'] = liveload
    
    profiles['xxx'] = profiles.apply(lambda row: pd.Series(create_steelcolumn(profile = row, height = height, fy = 235), axis = 1))
    # steelcolumns = create_steelcolumn(profiles, height = height, fy = 235)
    # results = xx(steelcolumns, deadload=deadload, liveload=liveload)

    # print(steelcolumns, type(steelcolumns))
    # results = create_steelcolumn(profiles, height = height, fy = 235)

    # profiles['Factored load'].values[0] = results[0]
    return profiles




 