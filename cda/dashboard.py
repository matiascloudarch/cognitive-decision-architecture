import streamlit as st
import sqlite3
import json
import os

# Determine the base path of the project
base_dir = "/Users/matiass/Desktop/CDA/cognitive-decision-architecture"
db_path = os.path.join(base_dir, "cda_gate.db")

# Connection to the Forensic Audit Ledger database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
except sqlite3.Error as e:
    st.error(f"Error connecting to the database: {e}")
    st.stop()


# Function to get decision counts
def get_decision_counts():
    try:
        cursor.execute("SELECT decision, COUNT(*) FROM forensic_audit_trail GROUP BY decision")
        counts = cursor.fetchall()
        return dict(counts)
    except sqlite3.Error as e:
        st.warning(f"Error getting decision counts: {e}")
        return {}

# Function to get logs
def get_all_logs():
    try:
        cursor.execute("SELECT rowid, * FROM forensic_audit_trail ORDER BY executed_at DESC")
        logs = cursor.fetchall()
        # Obtener nombres de las columnas para crear diccionarios
        col_names = [description[0] for description in cursor.description]
        return [dict(zip(col_names, log)) for log in logs]
    except sqlite3.Error as e:
        st.warning(f"Error getting logs: {e}")
        return []

# Function to get details of a specific log
def get_log_details(rowid):
    try:
        cursor.execute("SELECT rowid, * FROM forensic_audit_trail WHERE rowid = ?", (rowid,))
        log = cursor.fetchone()
        if log:
            col_names = [description[0] for description in cursor.description]
            return dict(zip(col_names, log))
        return None
    except sqlite3.Error as e:
        st.warning(f"Error getting log details: {e}")
        return None

# Function to verify an Attestation Envelope (simulated)
def verify_attestation_envelope_simulated(attestation_envelope):
    # This is a simulation. In a real scenario, pyseto would be used.
    # For now, we check if it looks like a local PASETO v4
    if attestation_envelope and attestation_envelope.startswith("v4.local."):
        # Here, real cryptographic verification logic would be added
        return True, "Valid v4.local. Attestation Envelope format (simulated)"
    return False, "Invalid or unsupported Attestation Envelope format for simulation."

# Streamlit App
st.set_page_config(layout="wide", page_title="CDA Forensic Audit Ledger Dashboard")

st.title("CDA Forensic Audit Ledger Dashboard")
st.markdown("---")

# Secciones del Dashboard
col1, col2, col3 = st.columns(3)

with col1:
    st.header("Traffic Monitor (Decisions)")
    decision_counts = get_decision_counts()
    
    allow_count = decision_counts.get('ALLOW', 0)
    review_count = decision_counts.get('REQUIRES_HUMAN_REVIEW', 0)
    deny_count = decision_counts.get('DENY', 0)

    st.metric(label="✅ APPROVED (ALLOW)", value=allow_count)
    st.metric(label="⚠️ REQUIRES HUMAN REVIEW", value=review_count)
    st.metric(label="🚫 DENIED (DENY)", value=deny_count)

with col2:
    st.header("Intent Inspector")
    all_logs = get_all_logs()
    
    if all_logs:
        log_options = {f"Log ID: {log['rowid']} - {log['action']} ({log['executed_at']})": log['rowid'] for log in all_logs}
        selected_log_display = st.selectbox("Select an audit log entry:", list(log_options.keys()))
        selected_log_rowid = log_options[selected_log_display]
        
        log_details = get_log_details(selected_log_rowid)
        if log_details:
            st.subheader(f"Log Details {log_details['rowid']}")
            st.json(log_details)
            
            # Display the reason for denial if it's DENY or REQUIRES_HUMAN_REVIEW
            if log_details.get('decision') == 'DENY' or log_details.get('decision') == 'REQUIRES_HUMAN_REVIEW':
                st.warning(f"**Decision Reason:** {log_details.get('reason', 'Not specified')}")
    else:
        st.info("No entries in the Forensic Audit Ledger yet.")

with col3:
    st.header("Cryptographic Integrity Verifier")
    attestation_input = st.text_area("Enter the Attestation Envelope (PASETO v4) here:", height=150)
    if st.button("Verify Attestation Envelope"):
        if attestation_input:
            is_valid, message = verify_attestation_envelope_simulated(attestation_input)
            if is_valid:
                st.success(message)
                # Intenta decodificar el payload si es un PASETO v4.local simulado
                try:
                    # In a real scenario, pyseto would be used here to decode
                    # This is just a simulation to display a JSON payload
                    parts = attestation_input.split('.')
                    if len(parts) > 2: # Asumiendo v4.local.<payload>.<footer>
                        simulated_payload_base64 = parts[2]
                        # El payload en PASETO no es Base64 estándar, sino Base64url
                        # Para una demostración simple, podríamos simular esto mejor
                        st.info("Payload decoding (simulated):")
                        st.json({"simulated_data": "Attestation Envelope content (simulated)"})
                except Exception as e:
                    st.error(f"Error simulating payload decoding: {e}")
            else:
                st.error(message)
        else:
            st.warning("Please enter an Attestation Envelope to verify.")

st.markdown("---")
st.caption("CDA Monitoring Dashboard - Aligned with ITU-T FG-TIDA.")
