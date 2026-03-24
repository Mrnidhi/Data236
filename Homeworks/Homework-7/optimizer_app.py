import json
import os
import sqlite3

import pandas as pd
import streamlit as st
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from tools import calculator, policy_retriever

st.set_page_config(
    page_title="Bike-Share Pass Optimizer", layout="wide", page_icon="🚲"
)

st.title("Single-Agent ReAct + MRKL Bike-Share Pass Optimizer")

st.markdown(
    """
Upload a monthly CSV trip dataset and provide the official pricing/policy URL.
The ReAct agent will analyze the costs and recommend whether to buy a monthly membership
or pay per ride/minute.
"""
)

AVAILABLE_MODELS = [
    "llama3.2:3b-instruct-q4_K_S",
    "qwen2.5-coder:0.5b-instruct-q4_K_S",
    "smollm:1.7b",
]

with st.sidebar:
    st.header("Inputs")
    model_name = st.selectbox("Ollama Model", AVAILABLE_MODELS, index=0)
    uploaded_file = st.file_uploader("Upload Trip Data (CSV)", type=["csv"])
    pricing_url = st.text_input(
        "Pricing Policy URL", value="https://citibikenyc.com/pricing"
    )
    run_agent = st.button("Run Optimizer")

if run_agent and uploaded_file and pricing_url:
    st.info(f"Loading Agent with model: {model_name}...")

    temp_csv_path = "temp_uploaded_trips.csv"
    df = pd.read_csv(uploaded_file)
    df.to_csv(temp_csv_path, index=False)

    @tool
    def run_csv_sql(sql: str) -> str:
        "Run read-only SQL over the uploaded trips. Table is named 'trips'."
        try:
            conn = sqlite3.connect(":memory:")
            _df = pd.read_csv(temp_csv_path)
            _df.to_sql("trips", conn, index=False)
            result_df = pd.read_sql_query(sql, conn)
            rows = result_df.to_dict(orient="records")
            conn.close()
            return json.dumps(
                {
                    "success": True,
                    "data": {
                        "rows": rows,
                        "row_count": len(rows),
                        "source": "uploaded.csv",
                    },
                }
            )
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @tool
    def run_policy_retriever(query: str) -> str:
        "Fetch pricing page snippets."
        " Input is a search query (e.g. 'monthly membership price')."
        return json.dumps(policy_retriever(url=pricing_url, query=query, k=5))

    @tool
    def run_calculator(expression: str) -> str:
        "Safe arithmetic. Use +, -, *, /. E.g. '(10 * 0.15) + 3.00'."
        return json.dumps(calculator(expression=expression))

    agent_tools = [run_csv_sql, run_policy_retriever, run_calculator]

    react_prompt = PromptTemplate.from_template(
        "Answer the following questions as best you can. "
        "You have access to the following tools:\n\n{tools}\n\n"
        "Use the following format:\n\n"
        "Question: the input question you must answer\n"
        "Thought: you should always think about what to do\n"
        "Action: the action to take, should be one of [{tool_names}]\n"
        "Action Input: the input to the action\n"
        "Observation: the result of the action\n"
        "... (this Thought/Action/Action Input/Observation can repeat N times)\n"
        "Thought: I now know the final answer\n"
        "Final Answer: the final answer to the original input question\n\n"
        "Begin!\n\n"
        "Question: {input}\n"
        "Thought:{agent_scratchpad}"
    )

    prompt_str = (
        "You are a Bike-Share Pass Optimizer. "
        "Recommend whether a rider should buy a monthly bike-share membership or pay per ride. "
        "1. Query the dataset for number of trips, average duration, e-bike usage. "
        "2. Retrieve membership vs per-ride pricing from the official pricing page. "
        "3. Calculate total cost under pay-per-use. "
        "4. Calculate monthly membership cost. "
        "5. Compare both costs and give a final decision with justification and cost table."
    )

    llm = ChatOllama(model=model_name, temperature=0)
    agent = create_react_agent(llm, agent_tools, react_prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=agent_tools,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        max_iterations=10,
    )

    st.subheader("Agent Output")
    with st.spinner(f"Agent ({model_name}) is thinking..."):
        try:
            response = agent_executor.invoke({"input": prompt_str})

            st.markdown("### Final Recommendation")
            st.write(response["output"])

            st.markdown("### Agent Steps Trace")
            for step in response["intermediate_steps"]:
                action, observation = step
                with st.expander(f"Tool used: {action.tool}"):
                    st.text(f"Action Input:\n{action.tool_input}")
                    st.text(f"Observation:\n{observation}")

        except Exception as e:
            st.error(f"Agent execution failed: {e}")
