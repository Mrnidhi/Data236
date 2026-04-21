# DATA-236 Homework 10

## Files
- `ge-eval2.py`: Kafka evaluator for the plan, draft, and final message flow.
- `sim_agents.py`: Sends a sample conversation through the pipeline.
- `test_evaluator.py`: Runs the sample flow and evaluator together.
- `DATA236_DEMO10/train_customer_model.py`: Trains the customer segmentation model.
- `DATA236_DEMO10/streamlit_ml_app.py`: Streamlit app for the customer model.

## Run
Install the required packages, start Kafka and Ollama, then run the scripts in this order:
1. `python DATA236_DEMO10/train_customer_model.py`
2. `python sim_agents.py`
3. `python ge-eval2.py`
4. `streamlit run DATA236_DEMO10/streamlit_ml_app.py`

Generated model files and local virtual environments are not checked in.
