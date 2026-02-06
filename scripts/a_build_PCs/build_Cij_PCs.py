#%%

from heterogeneity_code.d_nport_portshares.a_build_PCs.a_select_sample.funds_that_hold_bonds import create_funds_that_hold_bonds_list
from heterogeneity_code.d_nport_portshares.a_build_PCs.b_build_port_weights.b_build_port_weights import  build_portf_weights
from heterogeneity_code.d_nport_portshares.a_build_PCs.d_build_PCs.a_simple_one_dimensional import build_assetcat_PC_fullpanel
from heterogeneity_code.a_configs import CONFIGS

aggregation_level = CONFIGS["NPORT"]["build_PCs"]["aggregation_level"] # type: ignore # noqa: F821, E501, F723

# step 1
create_funds_that_hold_bonds_list()

# # step 2
build_portf_weights(aggregation_level)

# # step 3
build_assetcat_PC_fullpanel()