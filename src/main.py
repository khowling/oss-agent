from agent_framework.devui import serve
from agent import create_agent

agent = create_agent()

if __name__ == "__main__":
    serve(entities=[agent], port=8080, host="0.0.0.0", auto_open=False)
