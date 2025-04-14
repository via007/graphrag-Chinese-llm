import time
import os
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px


class KnowledgeGraphGenerator:
    def __init__(self, base_path):
        self.base_path = base_path
        self.temp_path = os.path.join(base_path, "temp")
        self.entities_path = os.path.join(self.temp_path, "entities.csv")
        self.relations_path = os.path.join(self.temp_path, "relations.csv")
        self.output_html = os.path.join(self.temp_path, "knowledge_graph.html")
        self.df_entities = None
        self.df_relationships = None
        self.G = None

    def convert_parquet_to_csv(self):
        """Convert parquet files to CSV"""
        df_nodes = pd.read_parquet(os.path.join(self.base_path, "index", "entities.parquet"))
        df_edges = pd.read_parquet(os.path.join(self.base_path, "index", "relationships.parquet"))

        os.makedirs(self.temp_path, exist_ok=True)

        df_nodes.to_csv(self.entities_path, index=False)
        df_edges.to_csv(self.relations_path, index=False)

        time.sleep(1)

    def load_data(self):
        """Load CSV files into dataframes"""
        self.df_entities = pd.read_csv(self.entities_path)
        self.df_relationships = pd.read_csv(self.relations_path)

    def process_type(self, t):
        """Process type column values"""
        if pd.isna(t) or t == "":
            return "OTHER"
        elif len(str(t)) > 50:
            return "OTHER"
        else:
            return t

    def prepare_data(self):
        """Prepare data for graph visualization"""
        # Process types and assign colors
        self.df_entities['type_processed'] = self.df_entities['type'].apply(self.process_type)
        unique_types = self.df_entities['type_processed'].unique()
        color_scale = px.colors.qualitative.Plotly
        colors = color_scale * (len(unique_types) // len(color_scale) + 1)
        self.type_to_color = {t: colors[i % len(color_scale)] for i, t in enumerate(unique_types)}

    def create_graph(self):
        """Create NetworkX graph"""
        self.G = nx.Graph()

        # Add nodes
        for _, row in self.df_entities.iterrows():
            self.G.add_node(row['title'],
                            description=row['description'],
                            type=row['type_processed'])

        # Add edges
        for _, row in self.df_relationships.iterrows():
            self.G.add_edge(row['source'],
                            row['target'],
                            description=row['description'],
                            weight=row['weight'])

    def generate_visualization(self):
        """Generate and save the visualization"""
        # Generate layout
        pos = nx.spring_layout(self.G)

        # Prepare edge data
        edge_x, edge_y, edge_text = [], [], []
        for edge in self.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_text.append(self.G.edges[edge]['description'])

        # Prepare node data
        node_x, node_y, node_text, node_colors = [], [], [], []
        for node in self.G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"{node}<br>{self.G.nodes[node]['description']}")
            node_colors.append(self.type_to_color[self.G.nodes[node]['type']])

        # Create Plotly figure
        fig = go.Figure()

        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='text',
            text=edge_text,
            mode='lines'
        ))

        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(size=10, color=node_colors),
            text=[node for node in self.G.nodes()],
            textposition='top center',
            hoverinfo='text',
            hovertext=node_text
        ))

        # Update layout
        fig.update_layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            title="知识图谱"
        )

        # Save to HTML
        fig.write_html(self.output_html)

    def generate(self):
        """Execute the complete graph generation process"""
        self.convert_parquet_to_csv()
        self.load_data()
        self.prepare_data()
        self.create_graph()
        self.generate_visualization()

        return 'ok'


if __name__ == "__main__":
    base_path = ".\my_pkb"
    graph_gen = KnowledgeGraphGenerator(base_path)
    graph_gen.generate()
