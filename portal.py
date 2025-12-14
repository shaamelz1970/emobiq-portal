# eMOBIQ PARTNER PORTAL - SINGLE FILE VERSION
import streamlit as st
import pandas as pd
import datetime

# PAGE SETUP
st.set_page_config(page_title="eMOBIQ Portal", layout="wide")

# INITIALIZE DATA
if 'data' not in st.session_state:
    st.session_state.data = {
        'credits': {'total': 1000, 'used': 450},
        'clients': [
            {'name': 'Acme Corp', 'allocated': 200, 'used': 150, 'status': 'Active'},
            {'name': 'Globex', 'allocated': 150, 'used': 120, 'status': 'Active'},
            {'name': 'Stark Inc', 'allocated': 100, 'used': 25, 'status': 'Active'}
        ],
        'pipeline': [
            {'company': 'Umbrella Corp', 'stage': 'Lead', 'value': 5000},
            {'company': 'Cyberdyne', 'stage': 'Qualified', 'value': 8000},
            {'company': 'Tyrell Corp', 'stage': 'Demo', 'value': 12000}
        ]
    }

# SIDEBAR
with st.sidebar:
    st.title("🤝 eMOBIQ")
    st.divider()
    
    # NAVIGATION
    page = st.radio("MENU", ["Dashboard", "Clients", "Credits", "Pipeline", "Resources"])
    
    # STATS
    st.divider()
    available = st.session_state.data['credits']['total'] - st.session_state.data['credits']['used']
    active_clients = len([c for c in st.session_state.data['clients'] if c['status'] == 'Active'])
    
    st.metric("💰 Credits", f"${available}")
    st.metric("👥 Clients", active_clients)
    
    st.divider()
    st.caption("Simple Portal v1.0")

# ==================== DASHBOARD ====================
if page == "Dashboard":
    st.header("📊 Dashboard")
    
    # STATS ROW
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Credits", f"${st.session_state.data['credits']['total']}")
    with col2: st.metric("Used", f"${st.session_state.data['credits']['used']}")
    with col3: st.metric("Available", f"${available}")
    with col4: st.metric("Active Clients", active_clients)
    
    st.divider()
    
    # CLIENTS TABLE
    st.subheader("Client Allocations")
    clients_df = pd.DataFrame(st.session_state.data['clients'])
    st.dataframe(clients_df, use_container_width=True)
    
    # CREDIT CHART
    st.subheader("Credit Usage")
    chart_data = pd.DataFrame({
        'Type': ['Allocated', 'Available'],
        'Amount': [st.session_state.data['credits']['used'], available]
    })
    st.bar_chart(chart_data.set_index('Type'))

# ==================== CLIENTS ====================
elif page == "Clients":
    st.header("👥 Client Management")
    
    # ADD CLIENT FORM
    with st.form("add_client"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Company Name", placeholder="Acme Corporation")
        with col2:
            email = st.text_input("Contact Email", placeholder="contact@company.com")
        
        if st.form_submit_button("➕ Add Client"):
            st.session_state.data['clients'].append({
                'name': name,
                'allocated': 0,
                'used': 0,
                'status': 'Active'
            })
            st.success(f"✅ Added {name}")
            st.rerun()
    
    st.divider()
    
    # CLIENTS TABLE WITH EDITING
    st.subheader("Your Clients")
    for idx, client in enumerate(st.session_state.data['clients']):
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
        with col1:
            st.write(f"**{client['name']}**")
        with col2:
            st.write(f"${client['allocated']}")
        with col3:
            st.write(f"${client['used']}")
        with col4:
            st.write(client['status'])
        with col5:
            if st.button("Edit", key=f"edit_{idx}"):
                st.session_state.editing = idx
    
    # EDIT FORM
    if 'editing' in st.session_state:
        client = st.session_state.data['clients'][st.session_state.editing]
        st.divider()
        st.subheader(f"Editing {client['name']}")
        
        new_alloc = st.number_input("Allocated Credits", value=client['allocated'])
        new_status = st.selectbox("Status", ["Active", "Pending", "Suspended"])
        
        if st.button("Save Changes"):
            st.session_state.data['clients'][st.session_state.editing]['allocated'] = new_alloc
            st.session_state.data['clients'][st.session_state.editing]['status'] = new_status
            del st.session_state.editing
            st.success("✅ Client updated!")
            st.rerun()

# ==================== CREDITS ====================
elif page == "Credits":
    st.header("💰 Credit Management")
    
    col1, col2 = st.columns(2)
    
    # ALLOCATION FORM
    with col1:
        st.subheader("Allocate Credits")
        
        # Client dropdown
        client_options = [c['name'] for c in st.session_state.data['clients'] if c['status'] == 'Active']
        
        if client_options:
            selected = st.selectbox("Select Client", client_options)
            amount = st.number_input("Amount ($)", 10, available, 100)
            
            if st.button("💳 Allocate Now", type="primary"):
                # Update credits
                st.session_state.data['credits']['used'] += amount
                
                # Update client
                for client in st.session_state.data['clients']:
                    if client['name'] == selected:
                        client['allocated'] += amount
                
                st.success(f"✅ ${amount} allocated to {selected}")
                st.balloons()
        else:
            st.info("No active clients available")
    
    # BALANCE DISPLAY
    with col2:
        st.subheader("Credit Balance")
        
        # Progress bar
        used_pct = (st.session_state.data['credits']['used'] / st.session_state.data['credits']['total']) * 100
        st.progress(used_pct/100, text=f"{used_pct:.1f}% used")
        
        # Metrics
        st.metric("Total Pool", f"${st.session_state.data['credits']['total']}")
        st.metric("Allocated", f"${st.session_state.data['credits']['used']}")
        st.metric("Remaining", f"${available}")
        
        # Allocation history
        with st.expander("Recent Allocations"):
            st.write("1. Acme Corp - $200")
            st.write("2. Globex - $150")
            st.write("3. Stark Inc - $100")

# ==================== PIPELINE ====================
elif page == "Pipeline":
    st.header("📈 Sales Pipeline")
    
    # KANBAN BOARD
    stages = ["Lead", "Qualified", "Demo", "Proposal", "Negotiation"]
    cols = st.columns(len(stages))
    
    for idx, stage in enumerate(stages):
        with cols[idx]:
            # Stage header
            deals = [d for d in st.session_state.data['pipeline'] if d['stage'] == stage]
            st.subheader(f"{stage} ({len(deals)})")
            
            # Deals in this stage
            for deal in deals:
                with st.container():
                    st.markdown(f"**{deal['company']}**")
                    st.caption(f"${deal['value']:,}")
                    if st.button("➡️ Next", key=f"move_{deal['company']}"):
                        st.info(f"Moving {deal['company']} to next stage")
    
    st.divider()
    
    # ADD NEW DEAL
    with st.form("add_deal"):
        st.subheader("Add New Opportunity")
        col1, col2, col3 = st.columns(3)
        with col1:
            company = st.text_input("Company Name")
        with col2:
            value = st.number_input("Deal Value ($)", 1000, 100000, 5000)
        with col3:
            stage = st.selectbox("Stage", stages)
        
        if st.form_submit_button("➕ Add to Pipeline"):
            st.session_state.data['pipeline'].append({
                'company': company,
                'value': value,
                'stage': stage
            })
            st.success(f"✅ Added {company} to pipeline")

# ==================== RESOURCES ====================
else:  # Resources page
    st.header("📚 Resource Library")
    
    # CATEGORIES
    categories = ["Sales", "Training", "Marketing", "Admin"]
    selected_cat = st.radio("Category", categories, horizontal=True)
    
    # RESOURCE LIST
    resources = {
        "Sales": [
            {"title": "Platform Demo Script", "type": "PDF", "size": "2.1MB"},
            {"title": "Objection Handling Guide", "type": "PDF", "size": "1.5MB"},
            {"title": "Sales Playbook", "type": "PDF", "size": "3.4MB"}
        ],
        "Training": [
            {"title": "Credit Allocation Tutorial", "type": "Video", "size": "45MB"},
            {"title": "Client Onboarding", "type": "Video", "size": "62MB"},
            {"title": "Platform Setup Guide", "type": "PDF", "size": "4.2MB"}
        ],
        "Marketing": [
            {"title": "Product Brochure", "type": "PDF", "size": "5.3MB"},
            {"title": "Case Studies", "type": "PDF", "size": "3.8MB"},
            {"title": "Email Templates", "type": "DOCX", "size": "1.2MB"}
        ]
    }
    
    # DISPLAY RESOURCES
    for res in resources.get(selected_cat, []):
        with st.expander(f"{res['title']} ({res['type']} - {res['size']})"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Type:** {res['type']}")
                st.write(f"**Size:** {res['size']}")
                st.write("Click buttons to view or download")
            with col2:
                if st.button("👀 View", key=f"view_{res['title']}"):
                    st.info(f"Opening {res['title']}...")
                if st.button("📥 Download", key=f"dl_{res['title']}"):
                    st.success(f"Downloading {res['title']}...")

# FOOTER
st.divider()
st.caption(f"© 2024 eMOBIQ Partner Portal | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")