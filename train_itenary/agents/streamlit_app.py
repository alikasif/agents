import streamlit as st
import asyncio
import os
import sys
from datetime import timedelta
from dotenv import load_dotenv
from irctc_agent import run_mcp_agent

load_dotenv(override=True)

st.set_page_config(page_title="IRCTC Agent", page_icon="🚆", layout="wide")

st.title("🚆 IRCTC AI Agent")
st.markdown("Ask about train schedules, routes, and availability.")

# Sidebar for configuration or info
with st.sidebar:
    st.info("Ensure the MCP Server is running on localhost:8282")
    st.code("python irctc_mcp_server.py", language="bash")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Enter your query here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Run the async agent function
                result = asyncio.run(run_mcp_agent(prompt))
                
                # Try to extract tool output from the result
                # We assume result has a way to access tool outputs or messages
                # Since we don't know the exact structure, we'll try to find a dict in the messages or tool outputs
                
                structured_data = None
                
                # Check if result has 'messages' attribute
                if hasattr(result, 'messages'):
                    for msg in reversed(result.messages):
                        if hasattr(msg, 'role') and msg.role == 'tool':
                            # This might be the tool output
                            if isinstance(msg.content, dict):
                                structured_data = msg.content
                                break
                            elif isinstance(msg.content, str):
                                # Try to parse JSON if it's a string
                                try:
                                    import json
                                    # Clean up the string if needed (sometimes LLMs add markdown code blocks)
                                    content_str = msg.content.strip()
                                    if content_str.startswith("```json"):
                                        content_str = content_str[7:]
                                    if content_str.endswith("```"):
                                        content_str = content_str[:-3]
                                    
                                    structured_data = json.loads(content_str.strip())
                                    if isinstance(structured_data, dict):
                                        break
                                except:
                                    pass
                
                # If we didn't find it in messages, check if result itself has it
                if not structured_data:
                    if isinstance(result, dict):
                        structured_data = result
                    elif hasattr(result, 'final_output') and isinstance(result.final_output, str):
                         # Try parsing final_output as JSON
                        try:
                            import json
                            content_str = result.final_output.strip()
                            if content_str.startswith("```json"):
                                content_str = content_str[7:]
                            if content_str.endswith("```"):
                                content_str = content_str[:-3]
                            structured_data = json.loads(content_str.strip())
                        except:
                            pass

                # Handle response type
                if structured_data and isinstance(structured_data, dict) and ("direct_routes" in structured_data or "multi_hop_routes" in structured_data):
                    response = structured_data
                    # Display Summary
                    if "summary" in response:
                        summary = response["summary"]
                        st.subheader(f"Journey: {summary.get('from_station')} ➡️ {summary.get('to_station')}")
                        st.caption(f"Date: {summary.get('journey_date')} | Total Routes: {summary.get('total_routes')}")
                    
                    # Display Direct Routes
                    if response.get("direct_routes"):
                        st.subheader("🚄 Direct Routes")
                        for route in response["direct_routes"]:
                            with st.expander(f"{route['train_name']} ({route['train_number']}) | ⏱️ {route['total_journey_time']}"):
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.caption("Departs")
                                    st.write(route['departure_time'])
                                with col2:
                                    st.caption("Arrives")
                                    st.write(route['arrival_time'])
                                with col3:
                                    st.caption("Duration")
                                    st.write(route['total_journey_time'])
                                with col4:
                                    st.caption("Train No")
                                    st.write(route['train_number'])
                    
                    # Display Multi-Hop Routes
                    if response.get("multi_hop_routes"):
                        st.subheader("🔀 Multi-Hop Routes")
                        for idx, route in enumerate(response["multi_hop_routes"]):
                            with st.expander(f"Option {idx+1}: {route['total_hops']} Hops | ⏱️ {route['total_journey_time']}"):
                                st.caption("Via Stations")
                                st.write(', '.join(route['intermediate_stations']))
                                
                                # Create a table for legs
                                legs_data = []
                                for leg in route['legs']:
                                    legs_data.append({
                                        "Leg": leg['leg_number'],
                                        "Train No": leg['train_number'],
                                        "Train Name": leg['train_name'],
                                        "From": leg['from_station'],
                                        "To": leg['to_station'],
                                        "Dep": leg['departure_time'],
                                        "Arr": leg['arrival_time'],
                                        "Layover": leg.get('layover_before_this_leg', '-')
                                    })
                                st.dataframe(legs_data, hide_index=True, use_container_width=True)

                    # Add raw JSON view for debugging or extra details
                    # with st.expander("View Raw Data"):
                    #     st.json(response)
                        
                    st.session_state.messages.append({"role": "assistant", "content": "Here are the routes I found."})

                else:
                    # Fallback for text response
                    if hasattr(result, 'final_output'):
                        response_text = result.final_output
                    else:
                        response_text = str(result)
                        
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

            except Exception as e:
                st.error(f"An error occurred: {e}")
