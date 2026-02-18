# Agent Architecture Options

## Option 1: Azure AI Foundry Agent (Managed)

```mermaid
graph TB
    subgraph Barclays["Barclays Environment"]
        U1[Web App Users] --> WA

        subgraph Client["Client Application"]
            WA[Web App<br/><i>@azure/ai-projects SDK</i>]
        end

        subgraph Foundry["Azure AI Foundry (Managed)"]
            FA[Foundry Agent<br/><i>Hosted in Azure</i>]
            FM[Foundry Memory<br/><i>Managed Thread Storage</i>]
            LLM1[LLM<br/><i>Azure OpenAI</i>]
            FA --> FM
            FA --> LLM1
        end

        WA -->|"@azure/ai-projects<br/>API calls"| FA
    end

    subgraph LSEG["LSEG Environment"]
        PAD1[ ]
        MCP1[MCP Server<br/><i>Hosted by LSEG</i><br/><i>LSEG Tools & Data</i>]
        PAD2[ ]
        PAD1 ~~~ MCP1 ~~~ PAD2
    end

    FA -->|"MCP Protocol"| MCP1

    style FA fill:#0078D4,color:#fff
    style FM fill:#0078D4,color:#fff
    style LLM1 fill:#0078D4,color:#fff
    style WA fill:#5C2D91,color:#fff
    style MCP1 fill:#00A651,color:#fff
    style Barclays fill:#1E3A5F,stroke:#4A90D9,color:#fff
    style LSEG fill:#1B4332,stroke:#52B788,color:#fff
    style PAD1 fill:none,stroke:none,color:none
    style PAD2 fill:none,stroke:none,color:none
```

**Key characteristics:**
- Azure manages agent runtime, memory, and LLM
- Web app is a thin client using `@azure/ai-projects` SDK
- MCP Server hosted/controlled by LSEG
- Minimal code, maximum Azure dependency

---

## Option 2: Microsoft Agent Framework (Self-Hosted)

```mermaid
graph TB
    subgraph Barclays["Barclays Environment"]
        U2A[Web App Users] --> UI
        U2B[API Consumers] --> UI

        subgraph Container["Container"]
            UI[Chat UI or API Layer<br/><i>REST / AG-UI</i>]
            AF[Microsoft Agent Framework<br/><i>C# or Python</i>]
            MEM[In-Memory Storage<br/><i>Thread/Session State</i>]
            UI --> AF
            AF --> MEM
        end

        LLM2[LLM Endpoint<br/><i>Azure OpenAI / OpenAI / Any Provider</i>]
        AF -->|"Chat Completions API"| LLM2
    end

    subgraph LSEG["LSEG Environment"]
        PAD1[ ]
        MCP2[MCP Server<br/><i>Hosted by LSEG</i><br/><i>LSEG Tools & Data</i>]
        PAD2[ ]
        PAD1 ~~~ MCP2 ~~~ PAD2
    end

    AF -->|"MCP Protocol"| MCP2

    style AF fill:#5C2D91,color:#fff
    style MEM fill:#5C2D91,color:#fff
    style LLM2 fill:#0078D4,color:#fff
    style UI fill:#FF6F00,color:#fff
    style MCP2 fill:#00A651,color:#fff
    style Barclays fill:#1E3A5F,stroke:#4A90D9,color:#fff
    style LSEG fill:#1B4332,stroke:#52B788,color:#fff
    style PAD1 fill:none,stroke:none,color:none
    style PAD2 fill:none,stroke:none,color:none
```

**Key characteristics:**
- Self-hosted in a container — deploy anywhere
- Full control over agent logic, memory, and orchestration
- Built-in MCP client for LSEG tools
- Exposes UI or API (or both)
- C# or Python only (no TypeScript)

---

## Option 3: Copilot Studio (Low-Code, M365 Native)

```mermaid
graph TB
    subgraph "Users"
        U3A[Web App Users]
        U3B[Teams Users]
        U3C[M365 Copilot Users]
    end

    subgraph "Microsoft Copilot Studio (Managed)"
        CS[Copilot Studio Agent<br/><i>Low-Code / Declarative</i>]
        CSM[Copilot Memory<br/><i>Managed by Copilot Studio</i>]
        LLM3[LLM<br/><i>Azure OpenAI via Copilot</i>]
        CS --> CSM
        CS --> LLM3
    end

    subgraph "Microsoft 365 Platform"
        TEAMS[Microsoft Teams<br/><i>Channel</i>]
        M365[M365 Copilot<br/><i>Plugin</i>]
        WEBCH[Web Channel<br/><i>Embedded Widget</i>]
    end

    subgraph "LSEG Infrastructure"
        MCP3[MCP Server<br/><i>Hosted by LSEG</i><br/><i>LSEG Tools & Data</i>]
    end

    U3A --> WEBCH
    U3B --> TEAMS
    U3C --> M365
    WEBCH --> CS
    TEAMS --> CS
    M365 --> CS
    CS -->|"MCP Protocol"| MCP3

    style CS fill:#008272,color:#fff
    style CSM fill:#008272,color:#fff
    style LLM3 fill:#008272,color:#fff
    style TEAMS fill:#6264A7,color:#fff
    style M365 fill:#6264A7,color:#fff
    style WEBCH fill:#FF6F00,color:#fff
    style MCP3 fill:#00A651,color:#fff
```

**Key characteristics:**
- Low-code / no-code agent built in Copilot Studio
- Native deployment to Teams, M365 Copilot, and Web channel
- MCP Server connector for LSEG tools
- Fully managed by Microsoft — minimal infrastructure
- Least control, most convenience

---

## Side-by-Side Comparison

```mermaid
graph LR
    subgraph "Option 1: Foundry"
        direction TB
        F1[Azure Managed Agent]
        F2[Foundry Memory]
        F3[Web App Client]
    end

    subgraph "Option 2: Agent Framework"
        direction TB
        A1[Self-Hosted Agent]
        A2[In-Memory Storage]
        A3[Container + UI/API]
    end

    subgraph "Option 3: Copilot Studio"
        direction TB
        C1[Low-Code Agent]
        C2[Managed Memory]
        C3[Teams + M365 + Web]
    end

    MCP[LSEG MCP Server<br/><i>Shared Across All Options</i>]

    F1 --> MCP
    A1 --> MCP
    C1 --> MCP

    style MCP fill:#00A651,color:#fff
    style F1 fill:#0078D4,color:#fff
    style A1 fill:#5C2D91,color:#fff
    style C1 fill:#008272,color:#fff
```

| | Option 1: Foundry | Option 2: Agent Framework | Option 3: Copilot Studio |
|---|---|---|---|
| **Agent hosting** | Azure managed | Self-hosted (container) | Microsoft managed |
| **Code required** | Thin client SDK calls | Full agent code (C#/Python) | Low-code / no-code |
| **Memory** | Foundry managed | In-memory (self-managed) | Copilot Studio managed |
| **MCP Server** | LSEG MCP ✅ | LSEG MCP ✅ | LSEG MCP ✅ |
| **LLM** | Azure OpenAI (Foundry) | Any provider | Azure OpenAI (Copilot) |
| **Teams/M365** | Needs Teams SDK layer | Needs Teams SDK layer | ✅ Native (built-in) |
| **Web App** | ✅ Via SDK | ✅ Via container UI/API | ✅ Via web channel |
| **TypeScript** | ✅ (client SDK) | ❌ C#/Python only | N/A (low-code) |
| **Portability** | Azure only | Any cloud / on-prem | Microsoft only |
| **Control** | Medium | Full | Low |
| **Complexity** | Low | Medium-High | Very Low |
| **Vendor lock-in** | High (Azure) | Low | High (Microsoft) |
