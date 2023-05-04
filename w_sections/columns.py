from dataclasses import dataclass
from math import sqrt, pi


@dataclass
class Load:
    """
    A data type to represent a load magnitude over various load components.
    """
    dead: float = 0.0
    live: float = 0.0
    snow: float = 0.0
    wind: float = 0.0
    quake: float = 0.0


@dataclass
class ColumnDoublySymmetric:
    """
    Datatype representing a doubly symmetric column of homogenous material.
    """
    height: float = 0.0
    area: float = 0.0
    MoIx: float = 0.0
    MoIy: float = 0.0
    K_x: float = 0.0
    K_y: float = 0.0
    E: float = 0.0

    def calc_radius_of_gyration(self, axis: str) -> float:
        """
        Returns the radius of gyration about the x or y axis.
        """
        MoI = self.MoIx if axis.lower() == 'x' else self.MoIy
        try:
            RoG = sqrt(MoI / self.area)
        except ZeroDivisionError:
            raise ValueError("The area cannot be zero.")
        return RoG
    
    def calc_euler_buckling_load(self, axis: str) -> float:
        """
        Returns the theoretical Euler buckling load about the x or y axis
        """
        if axis.lower() == 'x':
            MoI, K = self.MoIx, self.K_x
        elif axis.lower() == 'y':
            MoI, K = self.MoIy, self.K_y
        else:
            raise ValueError(f"{axis=} is not a valid axis. Provide 'x' or 'y' axis.")
        
        try:
            F_euler = (pi**2 * self.E * MoI) / (K * self.height)**2
        except ZeroDivisionError:
            raise ValueError("The height and K-factors cannot be zero.")
        return F_euler

    
@dataclass
class SteelColumn(ColumnDoublySymmetric):
    """
    Datatype representing a steel column.
    """
    column_tag: str = "" 
    axial_load: Load = None
    yield_stress: float = 235
    gamma_m: float = 1.0
    
    def factored_axial_load(self) -> float:
        """
        Returns a float representing the maximum factored load in a Load object.
        """
        return max_factored_load(self.axial_load)
        
    def factored_axial_capacity(self, axis: str) -> float:
        """
        Returns the axial capacity about the {axis} axis.
        """
        if axis == 'x':
            alpha = 0.34 # bucklingcurve b
        else:
            alpha = 0.49 # bucklingcurve c
        
        f_y = self.yield_stress / self.gamma_m
        
        i = self.calc_radius_of_gyration(axis)
        lamda_1 = pi * sqrt(self.E / f_y)
        
        N_cr = self.calc_euler_buckling_load(axis)
        lamda_rel = sqrt(self.area * f_y / N_cr)
        
        rho = 0.5 * (1 + alpha * (lamda_rel - 0.2) + lamda_rel**2 )
        ksi = 1 / (rho + sqrt(rho**2 - lamda_rel**2))
              
        N_b = (ksi * self.area * f_y / self.gamma_m)
        
        return N_b
        
    def factored_dcr(self, axis: str) -> float:
        """
        Returns the DemandCapacityRatio about the {axis} axis.
        """
        DCR = self.factored_axial_load() / self.factored_axial_capacity(axis)
        return DCR

    
def create_load(line: list[str]) -> Load:
    """
    Returns a Load object from a list of strings
    """
    return Load(dead = float(line[0]), live = float(line[1]))


def max_factored_load(load: Load) -> float:
    """
    Returns a float representing the maximum factored load in a Load object.
    """
    load_factors = {
        'dead': 1.2,
        'live': 1.5,
        'snow': 1.5,
        'wind': 1.5,
        'quake': 1.5
    }
    
    load_components = list(load_factors.keys())
    load_components.remove('dead')
    factored_external_loads = [load_factors[load_component] * getattr(load, load_component) 
                               for load_component in load_components]
        
    max_factored_load = load_factors['dead'] * load.dead + max(factored_external_loads)
    return max_factored_load


def convert_row_to_col_data(row: list[str]) -> SteelColumn:
    """
    Returns a SteelColumn object from a row of data representing a loaded column.
    """
    column_tag = row[0]
    area = float(row[1])
    height = float(row[2])
    MoIx = float(row[3])
    MoIy = float(row[4])
    fy = float(row[5])
    E = float(row[6])
    kx = float(row[7])
    ky = float(row[8])
    deadload = float(row[9])
    liveload = float(row[10])
    load= Load(deadload, liveload)
    
    column = SteelColumn(height = height, area = area, MoIx = MoIx, MoIy = MoIy,
                         K_x = kx, K_y = ky, E = E, column_tag = column_tag, axial_load = load, yield_stress = fy)
    return column

