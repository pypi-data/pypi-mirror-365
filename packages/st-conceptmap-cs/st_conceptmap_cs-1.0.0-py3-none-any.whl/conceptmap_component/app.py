import streamlit as st 
from contextmap_component import contextmap_component, parse_contextmap

cm_data = {
    "elements": [
        { "data": { "id": "a", "label": "Node A" } },
        { "data": { "id": "b", "label": "Node B" } },
        { "data": { "source": "a", "target": "b", "label": "A to B" } }
    ]
}

st.header("Scaffolding")

st.subheader("Task 1")
st.write("Create a context map!")

submit_requested = st.button("Submit")

cm_response = contextmap_component(cm_data=cm_data, submit_request=submit_requested, key="task_1")

if cm_response:
    st.write(parse_contextmap(cm_response))
    st.markdown("---")

    st.subheader("Task 2")
    st.write("Response: ")
    st.write("Make changes in your context map based on the response")
    contextmap_component(cm_data=cm_response, key="task_2")
