import streamlit as st
import pandas as pd
import numpy as np
import subprocess
import glob, sys, time, statistics, os.path, random
from pathlib import Path
import psutil
import plotly.graph_objects as go
from taxontabletools2.start import TTT_variables
from taxontabletools2.utilities import load_df
from taxontabletools2.utilities import collect_replicates
from taxontabletools2.utilities import collect_sample_stats
from taxontabletools2.basic_stats import basic_stats_reads
from taxontabletools2.basic_stats import basic_stats_OTUs
from taxontabletools2.basic_stats import taxonomic_resolution
from taxontabletools2.basic_stats import taxonomic_richness
from taxontabletools2.utilities import collect_traits
from taxontabletools2.utilities import strip_traits
from taxontabletools2.utilities import export_plot
from taxontabletools2.utilities import export_table
from taxontabletools2.table_processing import replicate_merging
from taxontabletools2.table_processing import negative_control_subtraction
from taxontabletools2.table_processing import read_based_filter
from taxontabletools2.table_processing import read_based_normalisation
from taxontabletools2.table_processing import taxonomic_filtering
from taxontabletools2.table_processing import sample_filtering
from taxontabletools2.sample_comparison import venn
from taxontabletools2.diversity_analyses import alpha_boxplot
from taxontabletools2.diversity_analyses import richness_per_taxon
from taxontabletools2.diversity_analyses import distance_matrix
import streamlit as st
from taxontabletools2.start import start

# Call the sidebar function
settings = start()
users_settings = settings['new_user_preferences_dict']

## Page title
st.write(""" ## Diversity analyses """)

# Ensure the session state variables are retained across subpages
if 'TaXon_table_df' not in st.session_state:
    error1, error2, error3 = st.columns(3)
    with error2:
        st.write('##### Please load a TaXon table to continue!')

elif 'TaXon_table_xlsx' not in st.session_state:
    error1, error2, error3 = st.columns(3)
    with error2:
        st.write('##### Please load a TaXon table to continue!')

elif st.session_state['TaXon_table_df'].empty == True:
    error1, error2, error3 = st.columns(3)
    with error2:
        st.write('##### Please check your TaXon table. It seems to be empty!')

elif st.session_state['TaXon_table_xlsx'].is_file() == False:
    error1, error2, error3 = st.columns(3)
    with error2:
        st.write('##### The TaXon table does not exist in the selected project folder!')

########################################################################################################################

else:
    st.write('### Alpha diversity analyses')
    st.write('### Richness box plot')
    diversity1, diversity2 = st.columns(2)
    with diversity1:
        available_metadata = ['All samples']  + st.session_state['metadata_df'].columns.tolist()[1:]
        selected_metadata = st.selectbox('Select metadata to test:', available_metadata)
    with diversity2:
        taxonomic_level = st.selectbox('Select taxonomic level:', st.session_state['available_taxonomic_levels_list'], index=5)
    if st.button(f'Calculate {taxonomic_level} richness for {selected_metadata}'):
        fig_diversity_1 = alpha_boxplot(
            st.session_state['path_to_outdirs'],
            st.session_state['TaXon_table_xlsx'],
            st.session_state['TaXon_table_df'],
            st.session_state['samples'],
            st.session_state['metadata_df'],
            selected_metadata,
            st.session_state['traits_df'],
            '',
            users_settings,
            {'selected_metadata': selected_metadata, 'taxonomic_level': taxonomic_level}
        )
        st.plotly_chart(fig_diversity_1, use_container_width=True, config=st.session_state['config'])
        export_plot(st.session_state['TaXon_table_xlsx'], 'Alpha_diversity', 'alpha_boxplot', selected_metadata, fig_diversity_1, users_settings, 'plotly')

    st.write('### Richness per taxon')
    diversity3, diversity4 = st.columns(2)
    with diversity3:
        taxonomic_level_1 = st.selectbox('Select taxonomic level 1:', st.session_state['available_taxonomic_levels_list'], index=6)
        taxonomic_level_2 = st.selectbox('Select taxonomic level 2:', st.session_state['available_taxonomic_levels_list'], index=3)
    with diversity4:
        pass
    if st.button(f'Calculate {taxonomic_level_1} richness per {taxonomic_level_2}'):
        df_diversity_2, df_diversity_3, fig_diversity_2, fig_diversity_3 = richness_per_taxon(st.session_state['TaXon_table_df'], st.session_state['samples'], taxonomic_level_1, taxonomic_level_2, users_settings)

        st.plotly_chart(fig_diversity_2, use_container_width=True, config=st.session_state['config'])
        export_plot(st.session_state['TaXon_table_xlsx'], 'Alpha_diversity', f'{taxonomic_level_1}_per_{taxonomic_level_2}', selected_metadata, fig_diversity_2, users_settings, 'plotly')
        export_table(st.session_state['TaXon_table_xlsx'], 'Alpha_diversity', f'{taxonomic_level_1}_per_{taxonomic_level_2}', df_diversity_2, users_settings)

        st.plotly_chart(fig_diversity_3, use_container_width=True, config=st.session_state['config'])
        export_plot(st.session_state['TaXon_table_xlsx'], 'Alpha_diversity', f'{taxonomic_level_1}_per_{taxonomic_level_2}_rel', selected_metadata, fig_diversity_2, users_settings, 'plotly')
        export_table(st.session_state['TaXon_table_xlsx'], 'Alpha_diversity', f'{taxonomic_level_1}_per_{taxonomic_level_2}_rel', df_diversity_3, users_settings)


    st.write('### Beta diversity analyses')

    diversity3, diversity4, diversity5 = st.columns(3)

    with diversity3:
        available_metadata = ['All samples']  + st.session_state['metadata_df'].columns.tolist()[1:]
        selected_metadata = st.selectbox('Select metadata to test: ', available_metadata)

    with diversity4:
        taxonomic_level = st.selectbox('Select taxonomic level: ', st.session_state['available_taxonomic_levels_list'], index=5)

    with diversity5:
        distance_metric = st.selectbox('Select metric: ', ['Jaccard', 'Braycurtis'], index=0)

    if st.button(f'Calculate {taxonomic_level} distance matrix for {selected_metadata}, based on {distance_metric} similarity.'):

        fig_diversity_2 = distance_matrix(
            st.session_state['path_to_outdirs'],
            st.session_state['TaXon_table_xlsx'],
            st.session_state['TaXon_table_df'],
            st.session_state['samples'],
            st.session_state['metadata_df'],
            selected_metadata,
            st.session_state['traits_df'],
            '',
            users_settings,
            {'selected_metadata': selected_metadata, 'taxonomic_level': taxonomic_level, 'metric':distance_metric}
        )

        st.plotly_chart(fig_diversity_2, use_container_width=True, config=st.session_state['config'])
        export_plot(st.session_state['TaXon_table_xlsx'], 'Beta_diversity', 'heatmap', selected_metadata, fig_diversity_2, users_settings, 'plotly')
