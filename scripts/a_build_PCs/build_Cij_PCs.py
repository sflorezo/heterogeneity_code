from heterogeneity_code.a_nport_portshares.a_build_PCs.a_select_sample.funds_that_hold_bonds import create_funds_that_hold_bonds_list
from heterogeneity_code.a_nport_portshares.a_build_PCs.b_build_port_weights.build_port_weights import  build_portf_weights
from heterogeneity_code.a_nport_portshares.a_build_PCs.c_build_PCs.a_simple_one_dimensional import fullpanel_build_PC

# step 1
create_funds_that_hold_bonds_list()

# # step 2
build_portf_weights()

# # step 3
fullpanel_build_PC()