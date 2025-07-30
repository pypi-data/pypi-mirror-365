import pandas as pd
import numpy as np
from pathlib import Path
from taxontabletools2.utilities import filter_taxontable
import plotly.graph_objects as go
import plotly.express as px
from scipy.spatial.distance import pdist, squareform

def alpha_boxplot(path_to_outdirs, taxon_table_xlsx, taxon_table_df, samples, metadata_df, selected_metadata,
                   traits_df, selected_traits, user_settings, tool_settings):

    # Make copies of input dataframes to prevent altering the originals
    taxon_table_df = taxon_table_df.copy()
    metadata_df = metadata_df.copy()
    traits_df = traits_df.copy()

    # Extract relevant settings from the tool settings
    selected_metadata = tool_settings['selected_metadata']
    taxonomic_level = tool_settings['taxonomic_level']

    # Get unique taxa at the specified taxonomic level and exclude empty values
    all_taxa = taxon_table_df[taxonomic_level].dropna().unique()

    # Initialize result dictionary
    res = {}
    if selected_metadata == 'All samples':
        for sample in samples:
            res[sample] = len([i for i in taxon_table_df[[taxonomic_level, sample]].groupby(taxonomic_level).sum().loc[lambda x: x[sample] > 0].index.tolist() if i != ''])

    else:
        # Case where specific categories from metadata are selected
        categories = [i for i in metadata_df[selected_metadata].dropna().unique() if i != '']

        # Filter metadata to keep relevant columns only
        metadata_df = metadata_df[['Sample', selected_metadata]]

        for category in categories:
            # Get the samples belonging to the current category
            category_samples = metadata_df.loc[metadata_df[selected_metadata] == category, 'Sample'].tolist()
            category_list = []
            for sample in category_samples:
                category_list.append(len([i for i in taxon_table_df[[taxonomic_level, sample]].groupby(taxonomic_level).sum().loc[lambda x: x[sample] > 0].index.tolist() if i != '']))
            res[category] = category_list

    # Use color map based on user settings
    colorscale_name = user_settings.get('colorsequence', 'Plotly')
    colors = getattr(px.colors.qualitative, colorscale_name, px.colors.qualitative.Plotly)*100
    color=0

    # Initialize and populate the figure
    fig = go.Figure()

    if selected_metadata == 'All samples':
        x_values = list(res.keys())
        y_values = list(res.values())
        fig.add_trace(go.Bar(x=x_values, y=y_values, marker_color=colors[color]))

    else:
        for key, values in res.items():
            if str(type(values)) != "<class 'list'>":
                values = [values]
                fig.add_trace(go.Box(y=values, name=key, marker_color=colors[color]))
            color+=1

    # Update layout
    fig.update_yaxes(rangemode='tozero')
    fig.update_layout(barmode='stack',
                      title=f'Alpha diversity: {taxonomic_level}, {selected_metadata}',
                      template=user_settings['template'],
                      font_size=user_settings['font_size'],
                      width=user_settings['plot_width'],
                      height=user_settings['plot_height'],
                      showlegend=False,
                      yaxis_title=f'Number of Taxa ({taxonomic_level})',
                      yaxis_title_font=dict(size=user_settings['font_size']),
                      yaxis_tickfont=dict(size=user_settings['font_size']),
                      xaxis_title_font=dict(size=user_settings['font_size']),
                      xaxis_tickfont=dict(size=user_settings['font_size']))

    return fig

def richness_per_taxon(taxon_table_df, samples, taxonomic_level_1, taxonomic_level_2, user_settings):
    # Make copies of input dataframes to prevent altering the originals
    taxon_table_df = taxon_table_df.copy()

    # Collect all unique taxa
    all_t1 = [i for i in sorted(taxon_table_df[taxonomic_level_1].unique()) if i != '']
    all_t2 = [i for i in sorted(taxon_table_df[taxonomic_level_2].unique()) if i != '']

    # Count t1 per t2 for each sample
    res_lst = []
    for sample in samples:
        sub_df = taxon_table_df[[taxonomic_level_1, taxonomic_level_2, sample]]
        sub_df = sub_df[sub_df[sample] != 0]
        # number of t1 per t2
        res = [sub_df[sub_df[taxonomic_level_2] == taxon][taxonomic_level_1].nunique() for taxon in all_t2]
        res_lst.append([sample] + res)

    # Create dataframe
    res_df = pd.DataFrame(res_lst, columns=['Sample'] + all_t2)

    # FIGURE 1: Absolute numbers
    fig1 = go.Figure()
    x_values = samples
    for taxon in all_t2:
        y_values = res_df[taxon].values
        fig1.add_trace(go.Bar(x=x_values, y=y_values, name=taxon))

    # Update layout
    fig1.update_xaxes(dtick='linear')
    fig1.update_yaxes(title=f'{taxonomic_level_1} richness')
    fig1.update_layout(title=f'Alpha diversity: {taxonomic_level_1} per {taxonomic_level_2}',
                      barmode='stack',
                      template=user_settings['template'],
                      font_size=user_settings['font_size'],
                      width=user_settings['plot_width'],
                      height=user_settings['plot_height'],
                      showlegend=user_settings['show_legend'],
                      yaxis_title_font=dict(size=user_settings['font_size']),
                      yaxis_tickfont=dict(size=user_settings['font_size']),
                      xaxis_title_font=dict(size=user_settings['font_size']),
                      xaxis_tickfont=dict(size=user_settings['font_size']))

    # FIGURE2: Relative proportions
    # Convert df to relative values
    # Set 'Sample' as index temporarily
    df_rel = res_df.set_index('Sample')
    # Calculate relative abundances per row
    df_rel = df_rel.div(df_rel.sum(axis=1), axis=0)
    # Optional: reset index to get 'Sample' back as a column
    df_rel = df_rel.reset_index()

    fig2 = go.Figure()
    x_values = samples
    for taxon in all_t2:
        y_values = [i*100 for i in df_rel[taxon].values]
        fig2.add_trace(go.Bar(x=x_values, y=y_values, name=taxon))

    # Update layout
    fig2.update_xaxes(dtick='linear')
    fig2.update_yaxes(title=f'{taxonomic_level_1} richness (%)')
    fig2.update_layout(title=f'Alpha diversity: {taxonomic_level_1} per {taxonomic_level_2}',
                      barmode='stack',
                      template=user_settings['template'],
                      font_size=user_settings['font_size'],
                      width=user_settings['plot_width'],
                      height=user_settings['plot_height'],
                      showlegend=user_settings['show_legend'],
                      yaxis_title_font=dict(size=user_settings['font_size']),
                      yaxis_tickfont=dict(size=user_settings['font_size']),
                      xaxis_title_font=dict(size=user_settings['font_size']),
                      xaxis_tickfont=dict(size=user_settings['font_size']))

    return res_df, df_rel, fig1, fig2


def distance_matrix(path_to_outdirs, taxon_table_xlsx, taxon_table_df, samples, metadata_df, selected_metadata,
                    traits_df, selected_traits, user_settings, tool_settings):
    # Make copies of input dataframes to prevent altering the originals
    taxon_table_df = taxon_table_df.copy()
    metadata_df = metadata_df.copy()
    traits_df = traits_df.copy()

    # Extract relevant settings from the tool settings
    selected_metadata = tool_settings['selected_metadata']
    taxonomic_level = tool_settings['taxonomic_level']
    metric = tool_settings['metric']

    # Get unique taxa at the specified taxonomic level and exclude empty values
    all_taxa = [i for i in taxon_table_df[taxonomic_level].dropna().unique() if i != '']

    # Initialize result dictionary
    res = {}

    if selected_metadata == 'All samples':
        # Case where all samples are used
        for sample in samples:
            # Sum the reads for each taxon in the current sample and filter for non-zero values
            sample_taxa = taxon_table_df[[taxonomic_level, sample]].groupby(taxonomic_level).sum()
            sample_taxa = sample_taxa.loc[sample_taxa[sample] > 0, sample]

            # Store binary presence/absence data if metric is 'Jaccard', otherwise store actual values
            if metric == 'Jaccard':
                res[sample] = [1 if taxon in sample_taxa.index else 0 for taxon in all_taxa]
            else:
                res[sample] = [sample_taxa[taxon] if taxon in sample_taxa.index else 0 for taxon in all_taxa]

        # Convert result dict into DataFrame (rows: taxa, columns: samples)
        presence_absence_df = pd.DataFrame(res, index=all_taxa).transpose()

        # Calculate distance between samples
        if metric == 'Jaccard':
            distances = pdist(presence_absence_df, metric=metric)
        else:
            distances = pdist(presence_absence_df, metric=metric)

        # Convert to square form distance matrix
        distance_matrix = squareform(distances)

        # Convert to a DataFrame for easier manipulation
        distance_matrix_df = pd.DataFrame(distance_matrix, index=samples, columns=samples)

    else:
        # Case where specific metadata categories are selected
        categories = [i for i in metadata_df[selected_metadata].dropna().unique() if i != '']

        # Filter metadata to keep relevant columns
        metadata_df = metadata_df[['Sample', selected_metadata]]

        for category in categories:
            # Get the samples belonging to the current category
            category_samples = metadata_df.loc[metadata_df[selected_metadata] == category, 'Sample'].tolist()

            # Sum reads across all samples in category for each taxon
            category_taxa = taxon_table_df[[taxonomic_level] + category_samples].groupby(taxonomic_level).sum()
            category_taxa = category_taxa.loc[category_taxa[category_samples].sum(axis=1) > 0].sum(axis=1)

            # Store binary presence/absence data if metric is 'Jaccard', otherwise store actual values
            if metric == 'Jaccard':
                res[category] = [1 if taxon in category_taxa.index else 0 for taxon in all_taxa]
            else:
                res[category] = [category_taxa[taxon] if taxon in category_taxa.index else 0 for taxon in all_taxa]

        # Convert result dict into DataFrame (rows: taxa, columns: categories)
        presence_absence_df = pd.DataFrame(res, index=all_taxa).transpose()

        # Calculate distance between categories
        if metric == 'Jaccard':
            distances = pdist(presence_absence_df, metric=metric)
        else:
            distances = pdist(presence_absence_df, metric=metric)

        # Convert to square form distance matrix
        distance_matrix = squareform(distances)

        # Convert to a DataFrame for easier manipulation
        distance_matrix_df = pd.DataFrame(distance_matrix, index=categories, columns=categories)


    # Use color map based on user settings
    colorscale_name = user_settings.get('colorscale', 'Viridis')

    # Initialize heatmap figure
    fig = go.Figure(data=go.Heatmap(
        z=distance_matrix_df.values.tolist(),
        x=distance_matrix_df.columns.tolist(),
        y=distance_matrix_df.index.tolist(),
        zmin=0,
        zmax=1,
        hoverongaps=False,
        colorscale=colorscale_name))

    # Update layout
    fig.update_xaxes(dtick='linear')
    fig.update_yaxes(dtick='linear')
    fig.update_layout(title=f'Beta diversity: {taxonomic_level}, {metric}',
                      template=user_settings['template'],
                      font_size=user_settings['font_size'],
                      width=user_settings['plot_width'],
                      height=user_settings['plot_height'],
                      showlegend=user_settings['show_legend'],
                      yaxis_title_font=dict(size=user_settings['font_size']),
                      yaxis_tickfont=dict(size=user_settings['font_size']),
                      xaxis_title_font=dict(size=user_settings['font_size']),
                      xaxis_tickfont=dict(size=user_settings['font_size']))

    return fig


