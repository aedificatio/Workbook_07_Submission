from w_sections.processing import (
    read_profiles, 
    sections_less_than, 
    sort_by_weight, 
    calculate_steelcolumns,
)
def main():
    profiles = read_profiles('IPE_profiles.csv')
    fy = 235 # MPa
    column_height = 6000 # mm
    deadload = 40000 # N
    liveload = 50000 # N
    checked_profiles = calculate_steelcolumns(profiles, column_height, fy, deadload, liveload)
    drop_failed = sections_less_than(checked_profiles, DCR=1)

    print(f"A IPE column with heigh {column_height/1000} m and load of {deadload/1000} & {liveload/1000} kN\n")

    # Best profile by weight
    best_by_weight = sort_by_weight(drop_failed)
    by_weight_row_nr = best_by_weight[['kg/m']].idxmin()
    by_weight_row = best_by_weight.loc[by_weight_row_nr]
    print(f"The best profile by weight is {by_weight_row['Section name'].values[0]}, with an DCR of {by_weight_row.DCR.values[0]:.3f}")

    # Best profile by DCR
    best_by_dcr = drop_failed.sort_values("DCR", ascending=False)
    by_dcr_row_nr = best_by_dcr[['DCR']].idxmax()
    by_dcr_row = best_by_dcr.loc[by_dcr_row_nr]
    print(f"The best profile by DCR is {by_dcr_row['Section name'].values[0]}, with an DCR of {by_dcr_row.DCR.values[0]:.3f}")

    # Show tasble
    print("\nThe top 5 results by DCR are:")
    print(best_by_dcr.head())

if __name__ == "__main__":
    main()