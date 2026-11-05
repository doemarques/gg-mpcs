# MCP Integration Architecture

## 1. Purpose

The MCP integration layer provides the chatbot with tools that allow an agent to act outside the conversation.

It consists of:

- MCP servers that expose tools to the chatbot.
- Custom client tools developed for individual client projects.
- The MCP client integration in the chatbot backend, which connects to configured servers and makes their tools available to the agent.

The goal is to allow a client chatbot to use custom tools through the Model Context Protocol (MCP), while keeping the chatbot backend independent of individual tool implementations.

The initial focus is on custom client tools that are self-hosted. The architecture should later support any MCP server operated by the client or by us.

The implementation is designed to remain simple: the chatbot backend connects to configured MCP servers and converts their available tools into agent-compatible tools. The protocol integration is implemented once and reused across clients.

---

## 2. Architectural Decision

### Separate repository for MCP servers

The MCP servers will live in a repository separate from the chatbot accelerator.

The MCP client integration will be implemented within the existing backend structure. Its precise placement within `agents/` or `core/` remains an implementation decision.

Each MCP server is independently built, versioned, and deployed.

The chatbot backend remains the MCP client. It connects to configured servers and exposes their tools to the agent.

```
┌────────────────────────────────────┐
│       Chatbot Accelerator Repo   │
│                                  │
│  frontend/                       │
│                                  │
│  backend/                        │
│                                  │
│  docs/                           │
└──────────────────┬─────────────────┘
                  │
                  │ MCP
                  ▼
┌────────────────────────────────────┐
│           MCP Repository         │
│                                  │
│  MCP Server(s)                   │
│  Custom Client Tools             │
│  Docker Images                   │
│  Independent CI/CD               │
└──────────────────┬─────────────────┘
                  │
                  ▼
            Client Systems
```

---

## 3. Responsibilities

The architecture has two main components with a one-directional dependency.

### 3.1 Chatbot accelerator repository — MCP client

The backend is the MCP client and the point where configuration meets code.

Its responsibilities are:

- Load and validate MCP server configuration.
- Establish connections to configured MCP servers.
- Use LangChain's MCP support, including `MCPAdapter`, to obtain tools.
- Convert connected server tools into agent-compatible tools.
- Register the resulting tools with the agent.
- Expose the relevant configuration or tool-call state to the frontend through the existing configuration interface.

The MCP integration belongs within the existing backend structure.

The feature is controlled through `customer.yaml`, like other optional capabilities. A client that does not enable MCP should not need to use the integration.

Agents obtain tools through the normal tool-registration path. They should not import individual vendor or server implementations.

### 3.2 MCP repository — MCP servers

The MCP servers live in their own repository, with independent:

- Source code.
- Docker images.
- CI/CD.
- Deployment.
- Versioning.

The servers are self-hosted from the start. Each server runs in the target environment, such as the client's cluster, and the backend connects to it through the transport it exposes.

The MCP repository is responsible for implementing and deploying the tools.

From the chatbot repository's point of view, MCP servers are configured and connected to; they are not built or deployed.

---

## 4. MCP Client Integration

The MCP client integration is implemented in the chatbot backend.

It is responsible for turning configured MCP servers into tools that can be registered with the agent.

The integration consists of three logical responsibilities:

1. **Configuration:** Defines which MCP servers are enabled and how to connect to them.
2. **Client:** Establishes connections to the configured MCP servers.
3. **Tool factory:** Converts the available MCP tools into tools that the agent can use.

The client integration should be reusable across client projects.

Adding a new MCP server should primarily require configuration rather than new protocol-handling code.

The implementation should use the existing backend organization:

- `backend/core/` for shared backend functionality, where appropriate.
- `backend/agents/` for agent-specific integration, where appropriate.

This is a logical mapping of responsibilities, not a proposed change to the repository structure. The final placement should follow the existing code conventions.

---

## 5. Configuration

MCP is an optional feature controlled through the client configuration.

The server definitions are configured under:

```
integrations:
  mcp:
    servers:
      # Configured MCP servers
```

The backend loads and validates the configuration, establishes the required connections, and makes the resulting tools available to the agent.

The configuration should describe the MCP servers required by the client deployment.

The exact configuration schema, including transport and authentication details, remains an implementation item.

---

## 6. Tool Flow

The MCP integration follows the existing agent tool-registration path.

```
customer.yaml
integrations.mcp.servers
        │
        │ Backend loads and validates
        ▼
Backend MCP Client
        │
        │ LangChain MCPAdapter
        ▼
Self-hosted MCP Server
        │
        │ MCP tools
        ▼
LangChain Tools
        │
        ▼
Agent tool registration
        │
        ▼
Agent calls the tool
        │
        ▼
Tool result
        │
        ▼
Chat response
```

The MCP server provides the tool implementation. The backend obtains the tool through the MCP client and registers it with the agent.

The agent uses the tool through the same path as its other registered tools.

The existing chat execution flow handles the tool result and continues the conversation.

---

## 7. Custom Client Tools

The first MCP implementations will be custom client tools.

These are MCP servers built for a specific client and self-hosted in the client's environment.

The client retains ownership of the capability, while the chatbot gains access to it through MCP.

A custom client tool is implemented as:

- A FastMCP server.
- The tools required by the client.
- A deployment in the target environment.

The chatbot backend should not need to change when a new client tool is added.

The new server is developed and deployed in the MCP repository, and the chatbot deployment is configured to connect to it.

This establishes a reusable pattern for future client tools and other MCP servers.

---

## 8. Implementation Plan

### Step 1 — MCP repository

Create the MCP repository and scaffold the initial server or servers.

The repository should include:

- FastMCP server implementation.
- Dockerfile.

The servers should be self-hosted from the beginning.

### Step 2 — Backend integration

Implement the MCP client integration within the existing backend structure.

This includes:

- Adding the required MCP dependency.
- Adding the MCP feature flag.
- Adding the server configuration to `customer.yaml`.
- Implementing the MCP client within the appropriate existing backend module.
- Implementing the tool factory within the appropriate existing backend module.
- Registering the tools with the agent.
- Exposing the relevant state through `GET /config`.
- Adding integration tests under `backend/tests/`.

No additional top-level backend folders are required.

### Step 3 — Wiring

Configure a self-hosted MCP server for a chatbot deployment.

Verify that:

- The backend connects to the MCP server.
- The agent receives the server's tools.
- The agent can call a tool.
- The tool result is returned to the agent.
- The frontend renders the tool call appropriately.

### Step 4 — Generalization

Adapt the implementation to support additional client tools and MCP servers.

The protocol integration should remain the same. New tools should be introduced through server implementation and deployment configuration rather than new protocol-handling code in the chatbot backend.

---

## 10. Open Items

The following items remain unresolved and should be addressed during implementation.

### Aegra MCP support

Aegra's own MCP support has been announced but is not yet available.

Revisit the implementation before building anything that depends on Aegra's MCP support.

### Transport and authentication

Determine the transport and authentication mechanism between the backend and self-hosted MCP servers.

The current direction is:

- Streamable HTTP for separately hosted servers.
- `stdio` for local servers.

The authentication approach should use the client's credentials and deployment requirements.

### Tool permissions and approval

Define:

- Tool allow-lists.
- Which tools are available to each client agent.
- Whether user approval is required for tools that act in the client's environment.

These controls should be considered part of the integration design rather than left to individual tool implementations.

## 11. Technology Choices and Rationale

This section explains the technologies selected for the MCP integration and the reasons for using them.

The choices aim to provide a standardized integration interface, reusable server implementations, and independent deployment and maintenance of client-specific tools.

### 11.1 FastMCP

**Technology:** FastMCP

FastMCP is selected as the framework for implementing custom MCP servers.

It provides an abstraction for defining MCP tools and exposing them through the MCP protocol. This reduces the amount of protocol-level code required to build and maintain a server.

The main reasons for using FastMCP are:

- **Simplified server development:** Developers can focus on implementing tool behavior rather than manually handling MCP messages and protocol details.
- **Python integration:** It fits naturally with Python-based client-specific tools and services.
- **Tool definitions:** It provides a structured way to define tool names, descriptions, and input parameters.
- **Protocol handling:** It handles the MCP server-side communication and tool invocation lifecycle.
- **Maintainability:** A consistent server framework encourages a common implementation pattern across client integrations.

FastMCP is appropriate for the initial scope because the MCP servers are custom-built services whose primary responsibility is to expose client capabilities as MCP tools.

The framework does not remove the need for testing, authentication, authorization, or input validation. Those responsibilities still need to be addressed in the server implementation and deployment.

Reference: [FastMCP documentation](https://gofastmcp.com/)

### 11.2 LangChain MCP Support and `MCPAdapter`

**Technology:** LangChain MCP support, including `MCPAdapter`

The backend uses LangChain's MCP support to connect to MCP servers and retrieve their available tools.

`MCPAdapter` provides a bridge between the MCP protocol and LangChain's tool format. This allows the backend to obtain tools from MCP servers without implementing a separate protocol-to-tool conversion layer.

The main reasons for using this integration are:

- **Reduced custom code:** MCP tool discovery and conversion are handled by an existing integration.
- **Consistent tool representation:** MCP tools are converted into a format compatible with the existing backend tool infrastructure.
- **Protocol abstraction:** The backend does not need to implement MCP message handling directly.
- **Interoperability:** Tools exposed by different MCP servers can be integrated through the same mechanism.
- **Easier maintenance:** Using a maintained integration reduces the amount of protocol-specific code owned by the accelerator.

This choice supports the objective of making MCP a reusable backend capability rather than implementing custom integration logic for every server.

The exact package and API should be verified against the versions used by the project. LangChain's MCP integration and API availability can vary by language and release.

Reference: [LangChain MCP tools documentation](https://docs.langchain.com/oss/python/langchain/mcp/tools)

### 11.3 Streamable HTTP

**Technology:** MCP Streamable HTTP transport

Streamable HTTP is the proposed transport for MCP servers that are deployed separately from the chatbot backend.

It allows an MCP server to run as an independent service and communicate with the backend over HTTP.

The main reasons for using Streamable HTTP are:

- **Remote communication:** The backend can connect to an MCP server deployed in a different container, service, or environment.
- **Deployment independence:** The server does not need to run as a subprocess of the backend.
- **Network compatibility:** HTTP-based communication fits common container and Kubernetes networking patterns.
- **Service-oriented deployment:** The MCP server can expose an endpoint that is configured by the chatbot backend.
- **Streaming support:** The transport can support streamed server responses where required by the MCP interaction.

Streamable HTTP is therefore the preferred transport for the architecture's independently deployed MCP servers.

The server endpoint, authentication mechanism, and network access rules remain deployment-specific configuration decisions.

Reference: [MCP Streamable HTTP specification](#)

### 11.4 `stdio` for Local Development

**Technology:** MCP `stdio` transport

The architecture identifies `stdio` as an option for local MCP server execution.

With this transport, the MCP client launches the server as a subprocess and exchanges protocol messages through standard input and output.

The main reasons for using `stdio` locally are:

- **Simple local setup:** Developers can run an MCP server without deploying it as a network service.
- **No network endpoint required:** The server does not need to expose an HTTP port.
- **Process lifecycle management:** The client can start and stop the server as part of its local execution.
- **Convenient development:** A developer can test an MCP server locally before packaging and deploying it.

`stdio` is intended for local or process-based execution. It is not the proposed transport for separately deployed MCP services in the target environment.

Reference: [MCP stdio specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)
