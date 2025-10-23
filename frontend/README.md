# Google ADK Multi-Agent Interface

A comprehensive Next.js frontend for managing Google ADK agents, tools, and real-time conversations.

## Features

### 🤖 Agent Management
- **Create Agents**: Support for Standard, ReAct Planner, Sequential, and Parallel agents
- **Dynamic Tool Assignment**: Attach/detach tools in real-time
- **Agent as Tools**: Use other agents as tools for hierarchical workflows
- **CRUD Operations**: Full create, read, update, delete functionality
- **Agent Analytics**: Usage statistics and performance metrics

### 🛠️ Tool Management
- **Tool Discovery**: Browse available tools by category
- **Dynamic Assignment**: Real-time tool attachment/detachment
- **Usage Analytics**: Track which agents use which tools
- **Bulk Operations**: Manage multiple tool assignments at once

### 💬 Real-time Chat
- **Streaming Responses**: Server-Sent Events (SSE) for real-time communication
- **Event Visualization**: Distinct handling of different event types:
  - `content` - Regular text responses
  - `tool_call` - Tool invocation events
  - `tool_response` - Tool completion events
  - `thinking` - Agent reasoning process
  - `error` - Error handling
- **Session Management**: Persistent conversation sessions
- **Multi-Agent Chat**: Switch between different agents seamlessly

### 🎨 Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live data synchronization
- **Interactive Components**: Smooth animations and transitions
- **Accessibility**: WCAG compliant interface

## Architecture

### Components Structure
```
src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard/Home page
│   ├── agents/            # Agent management
│   ├── tools/             # Tool management
│   └── chat/              # Chat interface
├── components/            # Reusable UI components
│   └── agents/           # Agent-specific components
├── services/             # API service layers
│   ├── auth.service.ts   # Authentication
│   ├── agent.service.ts  # Agent operations
│   └── chat.service.ts   # Chat & streaming
└── types/               # TypeScript definitions
    ├── agent.types.ts   # Agent interfaces
    └── chat.types.ts    # Chat interfaces
```

### Service Layer
- **AuthService**: JWT + API Key authentication
- **AgentService**: Full agent CRUD operations
- **ChatService**: Streaming chat with event handling

## Getting Started

### Prerequisites
- Node.js 18+ 
- Google ADK Backend running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## API Integration

### Authentication Flow
1. Login with username/password → JWT token
2. Create API key using JWT → Long-lived API key
3. Use API key for all subsequent requests

### Streaming Implementation
```typescript
// Real-time chat with event handling
const eventHandler = ChatService.createEventHandler(
  (content, eventType) => {
    // Handle different event types
    switch (eventType) {
      case StreamingEventType.CONTENT:
        // Regular text content
        break;
      case StreamingEventType.TOOL_CALL:
        // Tool invocation
        break;
      case StreamingEventType.TOOL_RESPONSE:
        // Tool completion
        break;
    }
  }
);

await ChatService.sendMessage(sessionId, message, eventHandler);
```

### Dynamic Tool Management
```typescript
// Attach tools to agent
await AgentService.attachTools(agentId, ['google_search', 'calculator']);

// Detach tools from agent
await AgentService.detachTools(agentId, ['google_search']);

// Use agents as tools
await AgentService.attachTools(agentId, ['agent:other_agent_id']);
```

## Key Features Demonstrated

### 1. Agent Types Support
- **Standard Agents**: Basic conversational agents
- **ReAct Planners**: Structured reasoning agents
- **Sequential Agents**: Step-by-step processing
- **Parallel Agents**: Concurrent task handling

### 2. Hierarchical Agent Architecture
- Agents can use other agents as tools
- Complex workflow orchestration
- Multi-level delegation patterns

### 3. Real-time Event Streaming
- Server-Sent Events (SSE) implementation
- Distinct event type handling
- Live conversation updates
- Tool execution visualization

### 4. Dynamic Tool Ecosystem
- Runtime tool attachment/detachment
- Tool usage analytics
- Category-based organization
- Bulk management operations

## Development

### Adding New Components
```typescript
// Example: New agent component
export default function NewAgentComponent({ agent }: { agent: Agent }) {
  return (
    <div className="agent-component">
      {/* Component implementation */}
    </div>
  );
}
```

### Extending Services
```typescript
// Example: Adding new service method
class AgentServiceClass {
  async newMethod(params: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/new-endpoint`, {
      headers: AuthService.getAuthHeaders(),
      // ... request configuration
    });
    return response.json();
  }
}
```

## Production Deployment

### Build for Production
```bash
npm run build
npm start
```

### Environment Configuration
```bash
# Production environment
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## Contributing

1. Follow the existing code structure
2. Use TypeScript for type safety
3. Implement proper error handling
4. Add loading states for async operations
5. Maintain responsive design principles

## License

This project is part of the Google ADK Multi-Agent system.
