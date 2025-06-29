/*
###############################################################################
# If you use PhysiCell in your project, please cite PhysiCell and the version #
# number, such as below:                                                      #
#                                                                             #
# We implemented and solved the model using PhysiCell (Version x.y.z) [1].    #
#                                                                             #
# [1] A Ghaffarizadeh, R Heiland, SH Friedman, SM Mumenthaler, and P Macklin, #
#     PhysiCell: an Open Source Physics-Based Cell Simulator for Multicellu-  #
#     lar Systems, PLoS Comput. Biol. 14(2): e1005991, 2018                   #
#     DOI: 10.1371/journal.pcbi.1005991                                       #
#                                                                             #
# See VERSION.txt or call get_PhysiCell_version() to get the current version  #
#     x.y.z. Call display_citations() to get detailed information on all cite-#
#     able software used in your PhysiCell application.                       #
#                                                                             #
# Because PhysiCell extensively uses BioFVM, we suggest you also cite BioFVM  #
#     as below:                                                               #
#                                                                             #
# We implemented and solved the model using PhysiCell (Version x.y.z) [1],    #
# with BioFVM [2] to solve the transport equations.                           #
#                                                                             #
# [1] A Ghaffarizadeh, R Heiland, SH Friedman, SM Mumenthaler, and P Macklin, #
#     PhysiCell: an Open Source Physics-Based Cell Simulator for Multicellu-  #
#     lar Systems, PLoS Comput. Biol. 14(2): e1005991, 2018                   #
#     DOI: 10.1371/journal.pcbi.1005991                                       #
#                                                                             #
# [2] A Ghaffarizadeh, SH Friedman, and P Macklin, BioFVM: an efficient para- #
#     llelized diffusive transport solver for 3-D biological simulations,     #
#     Bioinformatics 32(8): 1256-8, 2016. DOI: 10.1093/bioinformatics/btv730  #
#                                                                             #
###############################################################################
#                                                                             #
# BSD 3-Clause License (see https://opensource.org/licenses/BSD-3-Clause)     #
#                                                                             #
# Copyright (c) 2015-2021, Paul Macklin and the PhysiCell Project             #
# All rights reserved.                                                        #
#                                                                             #
# Redistribution and use in source and binary forms, with or without          #
# modification, are permitted provided that the following conditions are met: #
#                                                                             #
# 1. Redistributions of source code must retain the above copyright notice,   #
# this list of conditions and the following disclaimer.                       #
#                                                                             #
# 2. Redistributions in binary form must reproduce the above copyright        #
# notice, this list of conditions and the following disclaimer in the         #
# documentation and/or other materials provided with the distribution.        #
#                                                                             #
# 3. Neither the name of the copyright holder nor the names of its            #
# contributors may be used to endorse or promote products derived from this   #
# software without specific prior written permission.                         #
#                                                                             #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" #
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE   #
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE  #
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE   #
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR         #
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF        #
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS    #
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN     #
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)     #
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE  #
# POSSIBILITY OF SUCH DAMAGE.                                                 #
#                                                                             #
###############################################################################
*/

#include "./custom.h"
// #include <fstream>

double total_dead_tumor_cells = 0.0;
double previous_dead_tumor_cells = 0.0;

double total_parallel_time_in_T_Cell_recruitment = 0.0;

double get_dead_tumor_cells() {
    return total_dead_tumor_cells;
}

double get_previous_dead_tumor_cells() {
    return previous_dead_tumor_cells;
}

// Genera una posición aleatoria dentro de un anillo definido por los radios interno y externo
std::pair<double, double> random_position_in_annulus(double inner_radius, double outer_radius)
{
    double theta = 2 * M_PI * UniformRandom(); 
    double r = inner_radius + (outer_radius - inner_radius) * UniformRandom(); 

    double x = r * cos(theta);
    double y = r * sin(theta);
    return std::make_pair(x, y);
}

void recruit_cell(std::string cell_name, int number, double min_pos, double max_pos) {
    for (int i = 0; i < number; i++) {
        std::pair<double, double> pos = random_position_in_annulus(min_pos, max_pos);
        double new_x = pos.first;
        double new_y = pos.second;
        double new_z = 0.0;

        Cell* pNewCell = create_cell(get_cell_definition(cell_name));
        pNewCell->assign_position(new_x, new_y, new_z);
    }
}


void update_T_cell_recruitment(double dt) {
    static double ka = parameters.doubles("ka");
	static double r1 = parameters.doubles("r1");
    static double ki = parameters.doubles("ki");
    static double min_position_cells = parameters.doubles("min_position_cells");
    static double max_position_cells = parameters.doubles("max_position_cells");
	
    double delta_CC = get_dead_tumor_cells() - get_previous_dead_tumor_cells();

	// Michaelis-Menten term
    double recruitment_rate = (ka * delta_CC * r1) / (1 / ki + delta_CC);

    int new_naive_T_cells = std::max(1, static_cast<int>(std::round(recruitment_rate * 5)));

	int tumor_ID = get_cell_definition("tumor").type;
	int num_tumor_cells = 0;
	int live_tumor_cells = 0;

	double parallel_time_in_this_call = 0.0; // tiempo solo de esta llamada
    double start, end;
	
	start = omp_get_wtime();

	#pragma omp parallel for reduction(+:num_tumor_cells, live_tumor_cells)
	for( int i=0; i < (*all_cells).size(); i++ )
	{
		Cell* pC = (*all_cells)[i]; 

		// if (pC->phenotype.death.dead == false && pC->type == tumor_ID) {
		// 	num_tumor_cells++;
		// }

		if( pC->type == tumor_ID )
		{
			num_tumor_cells++;

			if( pC->phenotype.death.dead == false )
			{
				live_tumor_cells++;
			}
		}

	}

	end = omp_get_wtime();
	parallel_time_in_this_call += (end - start);

	int new_M0_cells = int(num_tumor_cells * 0.05 / 24);
	
	recruit_cell("naive T cell", new_naive_T_cells, min_position_cells, max_position_cells);
	recruit_cell("M0 macrophage", new_M0_cells, min_position_cells, max_position_cells);

	std::cout << std::endl << "Se agregaron " << new_naive_T_cells << " naive T cells y " << new_M0_cells << " M0 macrophages." << std::endl; 
	std::cout << "Quedan " << num_tumor_cells << " tumor cells totales." << std::endl; 
	std::cout << "Quedan " << live_tumor_cells << " tumor cells vivas.\n" << std::endl; 

	total_parallel_time_in_T_Cell_recruitment += parallel_time_in_this_call;
}


void create_cell_types( void )
{
	// set the random seed 
	if (parameters.ints.find_index("random_seed") != -1)
	{
		SeedRandom(parameters.ints("random_seed"));
	}
	
	/* 
	   Put any modifications to default cell definition here if you 
	   want to have "inherited" by other cell types. 
	   
	   This is a good place to set default functions. 
	*/ 
	
	initialize_default_cell_definition(); 
	cell_defaults.phenotype.secretion.sync_to_microenvironment( &microenvironment ); 
	
	cell_defaults.functions.volume_update_function = standard_volume_update_function;
	cell_defaults.functions.update_velocity = standard_update_cell_velocity;

	cell_defaults.functions.update_migration_bias = NULL; 
	cell_defaults.functions.update_phenotype = NULL; // update_cell_and_death_parameters_O2_based; 
	cell_defaults.functions.custom_cell_rule = NULL; 
	cell_defaults.functions.contact_function = NULL; 
	
	cell_defaults.functions.add_cell_basement_membrane_interactions = NULL; 
	cell_defaults.functions.calculate_distance_to_membrane = NULL; 
	
	/*
	   This parses the cell definitions in the XML config file. 
	*/
	
	initialize_cell_definitions_from_pugixml(); 

	/*
	   This builds the map of cell definitions and summarizes the setup. 
	*/
		
	build_cell_definitions_maps(); 

	/*
	   This intializes cell signal and response dictionaries 
	*/

	setup_signal_behavior_dictionaries(); 	

	/*
       Cell rule definitions 
	*/

	setup_cell_rules(); 

	/* 
	   Put any modifications to individual cell definitions here. 
	   
	   This is a good place to set custom functions. 
	*/ 
	
	cell_defaults.functions.update_phenotype = phenotype_function; 
	cell_defaults.functions.custom_cell_rule = custom_function; 
	cell_defaults.functions.contact_function = contact_function; 
	
	/*
	   This builds the map of cell definitions and summarizes the setup. 
	*/
		
	display_cell_definitions( std::cout ); 
	
	return; 
}

void setup_microenvironment( void )
{
	// set domain parameters 
	
	// put any custom code to set non-homogeneous initial conditions or 
	// extra Dirichlet nodes here. 
	
	// initialize BioFVM 
	
	initialize_microenvironment(); 	
	
	return; 
}

void setup_tissue(void)
{
	double Xmin = microenvironment.mesh.bounding_box[0];
	double Ymin = microenvironment.mesh.bounding_box[1];
	double Zmin = microenvironment.mesh.bounding_box[2];

	double Xmax = microenvironment.mesh.bounding_box[3];
	double Ymax = microenvironment.mesh.bounding_box[4];
	double Zmax = microenvironment.mesh.bounding_box[5];

	if (default_microenvironment_options.simulate_2D == true)
	{
		Zmin = 0.0;
		Zmax = 0.0;
	}

	double Xrange = Xmax - Xmin;
	double Yrange = Ymax - Ymin;
	double Zrange = Zmax - Zmin;

	double Xmiddle = 0.5*(Xmin+Xmax);
	double Ymiddle = 0.5*(Ymin+Ymax);
	double Zmiddle = 0.5*(Zmin+Zmax);

	std::vector<double> center = {Xmiddle,Ymiddle,Zmiddle}; 

	double radius = std::min( Xrange, Yrange ); 
	if( Zrange > microenvironment.mesh.dz - 1e-5 )
	{ radius = std::min( radius, Zrange ); }
	radius *= 0.5; 
	
	// create some of each type of cell 
	
	Cell* pC;

	double r1_default = 0; 
	double r2_default = radius; 

	std::string optional_parameter_name = "min_position_cells"; 
	if( parameters.doubles.find_index(optional_parameter_name) > -1 )
	{ r1_default = parameters.doubles(optional_parameter_name); }

	optional_parameter_name = "max_position_cells"; 
	if( parameters.doubles.find_index(optional_parameter_name) > -1 )
	{ r2_default = parameters.doubles(optional_parameter_name); }

	for( int k=0; k < cell_definitions_by_index.size() ; k++ )
	{
		Cell_Definition* pCD = cell_definitions_by_index[k]; 

		int number_of_cells = parameters.ints("number_of_cells"); 

		// optional: number_of_{cell type X} : number of cells of this particular type 

		optional_parameter_name = "number_of_" + pCD->name; 
		spaces_to_underscore( optional_parameter_name ); 
		if( parameters.ints.find_index(optional_parameter_name) > -1 )
		{ number_of_cells = parameters.ints(optional_parameter_name); }

		std::cout << "Placing " << number_of_cells << " cells of type " << pCD->name << " ... " << std::endl; 

		double r1 = r1_default; 
		optional_parameter_name = "min_position_" + pCD->name; 
		spaces_to_underscore( optional_parameter_name ); 
		if( parameters.doubles.find_index(optional_parameter_name) > -1 )
		{ r1 = parameters.doubles(optional_parameter_name); }

		double r2 = r2_default; 
		optional_parameter_name = "max_position_" + pCD->name; 
		spaces_to_underscore( optional_parameter_name ); 
		if( parameters.doubles.find_index(optional_parameter_name) > -1 )
		{ r2 = parameters.doubles(optional_parameter_name); }

		for( int n = 0 ; n < number_of_cells ; n++ )
		{
			std::vector<double> position; 
			if( default_microenvironment_options.simulate_2D )
			{ position = UniformInAnnulus( r1, r2); }
			else
			{ position = UniformInShell( r1, r2); }

			position += center; 
			/*
			position[0] = Xmin + UniformRandom()*Xrange; 
			position[1] = Ymin + UniformRandom()*Yrange; 
			position[2] = Zmin + UniformRandom()*Zrange; 
			*/

			pC = create_cell( *pCD ); 
			pC->assign_position( position );
		}
	}
	std::cout << std::endl; 
	
	// load cells from your CSV file (if enabled)
	load_cells_from_pugixml();
	set_parameters_from_distributions();

	return; 
}

std::vector<std::string> my_coloring_function( Cell* pCell )
{ return paint_by_number_cell_coloring(pCell); }

void phenotype_function( Cell* pCell, Phenotype& phenotype, double dt )
{ 
	return; 
}

void custom_function(Cell* pCell, Phenotype& phenotype, double dt) 
{ 
    return; 
}


void contact_function( Cell* pMe, Phenotype& phenoMe , Cell* pOther, Phenotype& phenoOther , double dt )
{ return; } 


void print_parallel_timings(double total_time)
{
    std::vector<std::pair<std::string, double>> timings = {
        {"update_all_cells", total_parallel_time_in_update_all_cells},
        {"time_secretion_uptake", time_secretion_uptake},
        {"time_intracellular_update", time_intracellular_update},
        {"time_bundled_phenotype_update", time_bundled_phenotype_update},
        {"time_interactions", time_interactions},
        {"time_custom_rules", time_custom_rules},
        {"time_update_velocities", time_update_velocities},
        {"time_dynamic_spring_attachments", time_dynamic_spring_attachments},
		{"time_standard_elastic_contact_function", time_standard_elastic_contact_function},
        {"time_standard_cell_interactions", time_standard_cell_interactions},
        {"time_update_positions", time_update_positions},
    };

    double total = total_parallel_time_in_update_all_cells;

    std::cout << "\n\n";
    // for (const auto& timing : timings)
    // {
    //     double percentage = (total > 0.0) ? (timing.second / total * 100.0) : 0.0;
    //     std::cout << "[" << timing.first << "] Tiempo TOTAL: " 
    //               << timing.second << " s (" << percentage << "%)" << std::endl;
    // }

    std::cout << "\n[T_cell_recruitment] Tiempo TOTAL: " 
              << total_parallel_time_in_T_Cell_recruitment << " s \t" << total_parallel_time_in_T_Cell_recruitment * 100.0 / total_time << "%)" << std::endl;

	std::cout << "\n[Update_all_cells] Tiempo TOTAL: " 
			  << total_parallel_time_in_update_all_cells << " s \t" << total_parallel_time_in_update_all_cells * 100.0 / total_time << "%)" << std::endl;

	// std::cout << "\n[BioFVM_microenvironment] Tiempo TOTAL: " 
    //           << total_parallel_time_in_BioFVM_microenvironment << " s" << std::endl;

	std::cout << "\n[BioFVM_solvers] Tiempo TOTAL: " 
			  << total_parallel_time_in_BioFVM_solvers << " s \t" << total_parallel_time_in_BioFVM_solvers * 100.0 / total_time << "%)" << "%)" << std::endl;

	std::cout << "Time for LOD_2D_x: " << time_LOD_2D_x << std::endl;
	std::cout << "Time for LOD_2D_y: " << time_LOD_2D_y << std::endl;
}


void save_parallel_timings_to_csv(std::string filename)
{
    std::ofstream file(filename);

    if (!file.is_open())
    {
        std::cout << "Error: No se pudo abrir el archivo " << filename << " para escritura." << std::endl;
        return;
    }

    file << "Seccion,Tiempo(segundos),Porcentaje(%)\n"; // Cabecera del CSV

    double total = total_parallel_time_in_update_all_cells;

    auto write_row = [&](std::string name, double value)
    {
        double percentage = (total > 0.0) ? (value / total * 100.0) : 0.0;
        file << name << "," << value << "," << percentage << "\n";
    };

    write_row("update_all_cells_total", total_parallel_time_in_update_all_cells);
    write_row("secretion_uptake", time_secretion_uptake);
    write_row("intracellular_update", time_intracellular_update);
    write_row("bundled_phenotype_update", time_bundled_phenotype_update);
    write_row("interactions", time_interactions);
    write_row("custom_rules", time_custom_rules);
    write_row("update_velocities", time_update_velocities);
    write_row("dynamic_spring_attachments", time_dynamic_spring_attachments);
	write_row("standard_elastic_contact_function", time_standard_elastic_contact_function);
    write_row("standard_cell_interactions", time_standard_cell_interactions);
    write_row("update_positions", time_update_positions);

    // No entra en el porcentaje:
    file << "T_cell_recruitment," << total_parallel_time_in_T_Cell_recruitment << ",0\n";
	file << "BioFVM_microenvironment," << total_parallel_time_in_BioFVM_microenvironment << ",0\n";
	file << "BioFVM_solvers," << total_parallel_time_in_BioFVM_solvers << ",0\n";

    file.close();
    std::cout << "Tiempos paralelos guardados en: " << filename << std::endl;
}
