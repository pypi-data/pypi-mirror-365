import numpy as np
import pandas as pd

# some weird directory stuff
import sys
sys.path.append("../src/CAST_panel/")
import CAST


#########################################################################################

treat = pd.read_csv("cleaned_data/expansion.csv")
adopt_year = treat["ADOPTION"]

mortality_rates_infant = np.genfromtxt("cleaned_data/mortality_rates_infant_wind3.csv", delimiter=",")
mortality_rates_infant = mortality_rates_infant[1:,1:]


pop_df = pd.read_csv("cleaned_data/births_1999-2020_wind3.csv")

if pop_df.shape[0] == 51:
    pop_df = pop_df.drop([8])

years = np.arange(2001, 2021)
treat = adopt_year - 2001
treat_index = treat.to_list()



print(CAST.rank_selection(mortality_rates_infant, treat_index))

inf_mort_CAST = CAST.method(mortality_rates_infant, treat_index, rank = 3)


print(inf_mort_CAST.get_significant_effects())
