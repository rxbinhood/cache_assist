# cache_assist

A caching MCP server exposing session caching utilities (`remember`, `recall`, `forget`).

> **Warning:** This server contains a deliberate security vulnerability (`pickle.load` deserialization) for testing MCPGuard security auditing. Expected verdict: **FAIL**.

## Run

```bash
pip install -e .
python server.py
```
