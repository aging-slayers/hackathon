from io import BytesIO
import requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import igraph as ig

from app.pipeline import process_pipeline

TITLE = "Age SLAYers Longevity Drug Search"
INSTRUCTIONS = """Welcome to the Age SLAYers Longevity Drug Search app!
This application allows you to explore and visualize networks of compounds, diseases, genes,
and side effects related to longevity research.
"""


# Configure page
st.set_page_config(
    page_title=TITLE,
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

@st.cache_data
def get_image(url):
    r = requests.get(url)
    return BytesIO(r.content)

def plot_igraph_with_plotly(g, layout_algorithm="fr", width=800, height=800):
    """
    Plot an igraph network using Plotly with node type coloring and interactivity
    
    Parameters:
    g: igraph.Graph object
    layout_algorithm: str, layout algorithm ('fr', 'kk', 'circle', 'grid', etc.)
    width, height: plot dimensions
    """
    
    # Get layout coordinates
    layout = g.layout(layout_algorithm)
    x_coords = [coord[0] for coord in layout]
    y_coords = [coord[1] for coord in layout]
    
    # Extract node information
    node_names = g.vs['name']
    node_types = [name.split('::')[0] for name in node_names]  # Extract type from name
    
    # Use label if available, else use name
    if 'label' in g.vs.attributes():
        node_labels = g.vs['label']
    else:
        node_labels = node_names
    
    # Define colors for different node types
    type_colors = {
        'Compound': '#FF6B6B',    # Red
        'Disease': '#9B59B6',     # Violet
        'Gene': '#45B7D1',        # Blue  
        'Side Effect': '#FFA07A'  # Orange
    }
    
    type_sizes = {
        'Compound': 28,
        'Disease': 8,
        'Gene': 14,
        'Side Effect': 8,
    }
    
    # Get node colors (use existing color attribute if available, else map by type)
    if 'color' in g.vs.attributes():
        node_colors = g.vs['color']
    else:
        node_colors = [type_colors.get(node_type, '#CCCCCC') for node_type in node_types]
    
    # Create edge traces
    edge_x = []
    edge_y = []
    edge_info = []
    
    for edge in g.es:
        x0, y0 = layout[edge.source]
        x1, y1 = layout[edge.target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Add edge information for hover
        source_name = g.vs[edge.source]['name']
        target_name = g.vs[edge.target]['name']
        relation = edge['relation'] if 'relation' in g.es.attributes() else 'connected to'
        edge_info.append(f"{source_name} → {target_name} ({relation})")
    
    # Create the figure
    fig = go.Figure()
    
    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=1.5, color='rgba(125,125,125,0.3)'),
        hoverinfo='none',
        showlegend=False,
        name='Edges'
    ))
    
    # Add nodes for each type separately (for legend)
    for node_type in set(node_types):
        # Filter nodes of this type
        type_indices = [i for i, nt in enumerate(node_types) if nt == node_type]
        type_x = [x_coords[i] for i in type_indices]
        type_y = [y_coords[i] for i in type_indices]
        type_names = [node_names[i] for i in type_indices]
        type_labels = [node_labels[i] for i in type_indices]
        
        # Create hover text
        hover_text = []
        for i, idx in enumerate(type_indices):
            # Count connections
            degree = g.degree(idx)
            in_degree = g.indegree(idx) if g.is_directed() else degree//2
            out_degree = g.outdegree(idx) if g.is_directed() else degree//2
            
            hover_text.append(
                f"<b>{type_labels[i]}</b><br>"
                f"Type: {node_type}<br>"
                f"Name: {type_names[i]}<br>"
                f"Connections: {degree}<br>"
                f"In: {in_degree}, Out: {out_degree}"
            )
        
        fig.add_trace(go.Scatter(
            x=type_x, y=type_y,
            mode='markers',
            marker=dict(
                size=[type_sizes.get(node_type, 10) for _ in type_indices],
                color=type_colors.get(node_type, '#CCCCCC'),
                line=dict(width=1, color='white'),
                opacity=0.8
            ),
            text=hover_text,
            hovertemplate='%{text}<extra></extra>',
            name=f'{node_type} ({len(type_indices)})',
            legendgroup=node_type
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': f"Network Graph: {g.vcount()} nodes, {g.ecount()} edges",
            'x': 0.5,
            'font': {'size': 16}
        },
        width=width,
        height=height,
        showlegend=True,
        hovermode='closest',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        ),
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            scaleanchor="y",
            scaleratio=1
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False
        ),
        plot_bgcolor='white',
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig


def main():

    st.markdown("""
                <style>
                    .stApp {
                        background-color: #faf0f9;
                    }
                    .title_left {
                        font-size: 2rem;
                        font-weight: bold;
                        margin-left: 0rem;
                        margin-top: -2rem;
                    }
                    .title_right {
                        font-size: 2rem;
                        font-weight: bold;
                        margin-left: 0rem;
                        margin-top: -2rem;
                    }
                    .subtitle {
                        color: #a455d6;
                        font-size: 1rem;
                        margin-left: 0.5rem;
                    }
                </style>
                """, unsafe_allow_html=True)
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": INSTRUCTIONS}
        ]

    # Initialize session state for graph
    if "graph" not in st.session_state:
        st.session_state.graph = None
    
    col1, col_right = st.columns([1,1.2])

    with col1:
        st.markdown("""
                <div class="main-container">
                        <div class="title_left">
                        Longevity drug search<span class="subtitle"> By SLAYers 💅</span>
                        </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Chat container
        chat_container = st.container(height=500)

        with chat_container:
            # Display chat messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me about the network or compounds..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Add assistant response (placeholder for now)
            response = "I see your message! Graph functionality will be added soon."

            if "labubu" in prompt.lower():
                with col_right:
                    st.image(get_image("http://nb3.me/public/labubu.png"), caption="You've been laboobed!")

            response = process_pipeline(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response['text']})
            
            if response['graph'] is not None:
                st.session_state.graph = response['graph']
            else:
                st.session_state.graph = None
            
            # Rerun to show new messages
            st.rerun()
            

    with col_right:
        st.markdown("""
            <div class="right-container">
                <div class="title_right">Drug Network Map</div
            </div>
        """, unsafe_allow_html=True)

        top = st.container()
        bottom = st.container()

        with top:
            # Graph dimensions
            col1a, col1b, col1c = st.columns(3)
            with col1a:
            # Layout algorithm selector
                layout_algorithm = st.selectbox(
                    "Layout Algorithm",
                    ["fr", "kk", "drl", "circle", "grid"],
                    index=0,
                    help="Choose how to arrange the nodes"
            )
            with col1b:
                graph_width = st.slider("Width", 600, 1200, 800)
            with col1c:
                graph_height = st.slider("Height", 400, 800, 600)
            
            # # Upload graph file (placeholder)
            # uploaded_file = st.file_uploader(
            #     "Upload Graph File",
            #     type=['graphml', 'gml', 'json'],
            #     help="Upload your network graph file"
            # )
            
            # if uploaded_file is not None:
            #     st.success("File uploaded! Graph loading functionality coming soon.")

        with bottom:
            # Graph display area
            if st.session_state.graph is not None:
                # Plot the graph
                fig = plot_igraph_with_plotly(
                    st.session_state.graph, 
                    layout_algorithm=layout_algorithm,
                    width=graph_width,
                    height=graph_height
                )
                fig.update_layout(
                    height=400, 
                    width=400     
                )
                st.plotly_chart(fig, use_container_width=True)

            # else:
            #     # Placeholder when no graph is loaded
            #     st.info("📄 No graph loaded yet")
                
            #     # Create a sample graph for demonstration
            #     if st.button("Load Sample Graph", type="primary"):
            #         # Create a sample graph
            #         sample_graph = ig.Graph.Erdos_Renyi(n=20, p=0.15, directed=True)
                    
            #         # Add node names and types
            #         node_types = ['Gene', 'Compound', 'Disease', 'Side Effect']
            #         sample_graph.vs['name'] = [f"{np.random.choice(node_types)}::{i:04d}" for i in range(sample_graph.vcount())]
            #         sample_graph.es['relation'] = ['interacts_with'] * sample_graph.ecount()
                    
            #         st.session_state.graph = sample_graph
            #         st.rerun()
                
                # st.markdown("""
                # **Instructions:**
                # 1. Click "Load Sample Graph" to see a demonstration
                # 2. Or upload your own graph file (feature coming soon)
                # 3. Use the controls on the left to adjust the visualization
                # 4. Chat with me about the network structure and properties
                # """)


        
if __name__ == "__main__":
    main()