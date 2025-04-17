import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
import numpy as np

class JobVisualizer:
    def __init__(self, df):
        self.df = df
        
    def plot_salary_distribution(self):
        """
        Create interactive salary distribution plot
        """
        fig = px.histogram(
            self.df,
            x='avg_salary',
            nbins=30,
            title='Salary Distribution',
            labels={'avg_salary': 'Average Salary (USD)'}
        )
        fig.update_layout(
            xaxis_title='Average Salary (USD)',
            yaxis_title='Count',
            showlegend=False
        )
        return fig
    
    def plot_skill_network(self, skill_correlation, threshold=0.3):
        """
        Create interactive network graph of skill relationships
        """
        # Create graph from correlation matrix
        G = nx.Graph()
        
        # Add edges with weights above threshold
        for i in range(len(skill_correlation.columns)):
            for j in range(i+1, len(skill_correlation.columns)):
                if abs(skill_correlation.iloc[i,j]) > threshold:
                    G.add_edge(
                        skill_correlation.columns[i],
                        skill_correlation.columns[j],
                        weight=abs(skill_correlation.iloc[i,j])
                    )
        
        # Create edge trace
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Add edge positions
        for edge in G.edges():
            x0, y0 = G.nodes[edge[0]]['pos']
            x1, y1 = G.nodes[edge[1]]['pos']
            edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['y'] += tuple([y0, y1, None])
        
        # Create node trace
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=10,
                color=[],
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                )
            )
        )
        
        # Add node positions and text
        for node in G.nodes():
            x, y = G.nodes[node]['pos']
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['text'] += tuple([node])
        
        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title='Skill Network Graph',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        
        return fig
    
    def plot_cluster_summary(self, cluster_summary):
        """
        Create bar plot of cluster statistics
        """
        fig = go.Figure()
        
        # Add salary bars
        fig.add_trace(go.Bar(
            x=cluster_summary.index,
            y=cluster_summary[('avg_salary', 'mean')],
            name='Average Salary',
            error_y=dict(
                type='data',
                array=cluster_summary[('avg_salary', 'std')],
                visible=True
            )
        ))
        
        # Add skill count bars
        fig.add_trace(go.Bar(
            x=cluster_summary.index,
            y=cluster_summary[('skill_count', 'mean')],
            name='Average Skill Count',
            error_y=dict(
                type='data',
                array=cluster_summary[('skill_count', 'std')],
                visible=True
            )
        ))
        
        fig.update_layout(
            title='Cluster Summary Statistics',
            xaxis_title='Cluster',
            yaxis_title='Value',
            barmode='group'
        )
        
        return fig
    
    def plot_top_skills(self, skill_counts):
        """
        Create bar plot of top skills
        """
        fig = px.bar(
            x=skill_counts.index,
            y=skill_counts.values,
            title='Top Required Skills',
            labels={'x': 'Skill', 'y': 'Count'}
        )
        
        fig.update_layout(
            xaxis_title='Skill',
            yaxis_title='Number of Job Postings'
        )
        
        return fig
    
    def plot_salary_by_skill(self, skill_matrix):
        """
        Create box plot of salary distribution by skill
        """
        # Calculate average salary for each skill
        skill_salaries = []
        for skill in skill_matrix.columns:
            skill_salaries.append({
                'skill': skill,
                'salary': self.df.loc[skill_matrix[skill] == 1, 'avg_salary'].mean()
            })
        
        skill_salaries_df = pd.DataFrame(skill_salaries)
        
        fig = px.box(
            skill_salaries_df,
            x='skill',
            y='salary',
            title='Salary Distribution by Skill',
            labels={'skill': 'Skill', 'salary': 'Average Salary (USD)'}
        )
        
        fig.update_layout(
            xaxis_title='Skill',
            yaxis_title='Average Salary (USD)'
        )
        
        return fig 