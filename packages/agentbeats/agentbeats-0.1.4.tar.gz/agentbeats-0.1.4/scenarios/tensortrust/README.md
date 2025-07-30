# README

## How-to run?

Run a game:

```
# Suppose you host your frontend / backend previously...

cd scenarios/tensortrust_mock
# Blue Agent
agentbeats run blue_agent_card.toml --launcher_host 0.0.0.0 --launcher_port 9010 --agent_host 0.0.0.0 --agent_port 9011 --backend http://localhost:9000
# Red Agent
agentbeats run red_agent_card.toml --launcher_host 0.0.0.0 --launcher_port 9020 --agent_host 0.0.0.0 --agent_port 9021 --backend http://localhost:9000
# Green Agent
agentbeats run green_agent/green_agent_card.toml --launcher_host 0.0.0.0 --launcher_port 9030 --agent_host 0.0.0.0 --agent_port 9031 --backend http://localhost:9000 --mcp http://localhost:9001/sse --tool green_agent/tools.py

# Then register agent & host battle in frontend plz.
```

## Changing Models:

```
agentbeats run blue_agent_card.toml --launcher_host 0.0.0.0 --launcher_port 9010 --agent_host 0.0.0.0 --agent_port 9011 --backend http://localhost:9000 --model_type openrouter --model_name anthropic/claude-3.5-sonnet
```

## Bonus: Agent-only mode

If you prefer agent-only mode (without wrapper server):
```
cd scenarios/tensortrust_mock
agentbeats run_agent agents/blue_agent/blue_agent_card.toml --agent_host 0.0.0.0 --agent_port 9011
agentbeats run_agent agents/red_agent/red_agent_card.toml --agent_host 0.0.0.0 --agent_port 9021
agentbeats run_agent agents/green_agent/green_agent_card.toml --agent_host 0.0.0.0 --agent_port 9031 --mcp ['http://localhost:9001/'] --tool 'agents/green_agent/tools.py'
```
