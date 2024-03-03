from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

from basic_rag import chain as basic_rag_chain
from basic_agent import agent_chain as basic_agent_chain
from basic_agent.schemas import Input, Output


app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Chains
add_routes(app, basic_rag_chain, path="/basic-rag")
add_routes(
    app,
    basic_agent_chain.with_types(input_type=Input, output_type=Output),
    path="/basic-agent",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
