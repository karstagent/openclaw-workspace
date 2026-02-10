# MCP Implementation Plan for GlassWall

## Overview

This document provides a detailed technical plan for implementing Model Context Protocol (MCP) support in GlassWall. The implementation will follow a phased approach, starting with a prototype client implementation and progressing to a full MCP server deployment.

## Phase 1: MCP Client Prototype

**Timeframe:** 2 weeks
**Goal:** Create a functional MCP client that can connect to existing MCP servers and validate basic functionality.

### Technical Components

1. **MCP Client Library**
   - Create TypeScript/JavaScript client library for MCP
   - Implement JSON-RPC 2.0 communication
   - Support WebSocket and HTTP transport layers

2. **Message Format Translation**
   - Convert GlassWall message format to MCP format
   - Implement bidirectional translation
   - Preserve message metadata across formats

3. **Basic Feature Support**
   - Implement resource retrieval
   - Add tool execution capability
   - Support prompt templates

### Implementation Details

#### MCP Client Class Structure

```typescript
/**
 * Main MCP client class that handles communication with MCP servers
 */
export class MCPClient {
  private serverUrl: string;
  private capabilities: MCPClientCapabilities;
  private connection: WebSocket | null = null;
  private requestMap: Map<string, RequestEntry> = new Map();
  private nextRequestId = 1;

  /**
   * Create a new MCP client
   */
  constructor(options: MCPClientOptions) {
    this.capabilities = options.capabilities || {
      resources: true,
      tools: true,
      prompts: false,
      sampling: false,
      roots: false,
      elicitation: false,
    };
  }

  /**
   * Connect to an MCP server
   */
  public async connect(serverUrl: string): Promise<MCPServerInfo> {
    this.serverUrl = serverUrl;
    
    // Create WebSocket connection
    this.connection = new WebSocket(serverUrl);
    
    // Setup event handlers
    this.connection.onmessage = this.handleMessage.bind(this);
    this.connection.onerror = this.handleError.bind(this);
    this.connection.onclose = this.handleClose.bind(this);
    
    // Wait for connection to open
    await new Promise<void>((resolve, reject) => {
      if (!this.connection) return reject(new Error("Connection not initialized"));
      
      this.connection.onopen = () => resolve();
      this.connection.onerror = (err) => reject(err);
    });
    
    // Initialize connection with server
    const serverInfo = await this.initialize();
    return serverInfo;
  }

  /**
   * Initialize the connection with the server
   */
  private async initialize(): Promise<MCPServerInfo> {
    const response = await this.sendRequest<MCPServerInfo>('initialize', {
      capabilities: this.capabilities,
      clientInfo: {
        name: 'GlassWall-MCP-Client',
        version: '0.1.0',
      },
    });
    
    return response;
  }

  /**
   * Send a JSON-RPC request to the server
   */
  private async sendRequest<T>(method: string, params?: any): Promise<T> {
    if (!this.connection) {
      throw new Error('Not connected to server');
    }
    
    const id = `${this.nextRequestId++}`;
    const request: JsonRpcRequest = {
      jsonrpc: '2.0',
      id,
      method,
      params,
    };
    
    return new Promise<T>((resolve, reject) => {
      // Store the request handlers
      this.requestMap.set(id, { resolve, reject });
      
      // Send the request
      this.connection?.send(JSON.stringify(request));
    });
  }

  /**
   * Handle incoming messages from the server
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message = JSON.parse(event.data as string) as JsonRpcMessage;
      
      // Handle response messages
      if ('id' in message && message.id && this.requestMap.has(message.id)) {
        const { resolve, reject } = this.requestMap.get(message.id)!;
        
        if ('error' in message) {
          reject(new Error(message.error.message));
        } else if ('result' in message) {
          resolve(message.result);
        }
        
        this.requestMap.delete(message.id);
      }
      
      // Handle notification messages
      else if ('method' in message && !('id' in message)) {
        this.handleNotification(message.method, message.params);
      }
    } catch (err) {
      console.error('Error handling message:', err);
    }
  }

  /**
   * Handle notification messages from the server
   */
  private handleNotification(method: string, params: any): void {
    // Handle different notification types
    switch (method) {
      case 'progress':
        // Handle progress notifications
        break;
      case 'log':
        // Handle log notifications
        break;
      // Add more notification handlers as needed
    }
  }

  /**
   * Handle errors from the WebSocket connection
   */
  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    // Implement error handling logic
  }

  /**
   * Handle connection close
   */
  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason);
    this.connection = null;
    // Implement reconnection logic if needed
  }

  /**
   * Get resources from the server
   */
  public async getResources(params: GetResourcesParams): Promise<MCPResource> {
    return this.sendRequest<MCPResource>('getResources', params);
  }

  /**
   * Execute a tool on the server
   */
  public async executeTool(params: ExecuteToolParams): Promise<any> {
    return this.sendRequest<any>('executeTool', params);
  }

  /**
   * Get available tools from the server
   */
  public async getTools(): Promise<MCPTool[]> {
    return this.sendRequest<MCPTool[]>('getTools', {});
  }

  /**
   * Close the connection
   */
  public async close(): Promise<void> {
    if (this.connection) {
      this.connection.close();
      this.connection = null;
    }
  }
}

/**
 * JSON-RPC request interface
 */
interface JsonRpcRequest {
  jsonrpc: '2.0';
  id: string;
  method: string;
  params?: any;
}

/**
 * JSON-RPC response interface
 */
interface JsonRpcResponse {
  jsonrpc: '2.0';
  id: string;
  result: any;
}

/**
 * JSON-RPC error interface
 */
interface JsonRpcError {
  jsonrpc: '2.0';
  id: string;
  error: {
    code: number;
    message: string;
    data?: any;
  };
}

/**
 * JSON-RPC notification interface
 */
interface JsonRpcNotification {
  jsonrpc: '2.0';
  method: string;
  params: any;
}

/**
 * Union type for all JSON-RPC messages
 */
type JsonRpcMessage = JsonRpcRequest | JsonRpcResponse | JsonRpcError | JsonRpcNotification;

/**
 * Request entry in the request map
 */
interface RequestEntry {
  resolve: (value: any) => void;
  reject: (reason: any) => void;
}

/**
 * MCP client capabilities
 */
interface MCPClientCapabilities {
  resources?: boolean;
  tools?: boolean;
  prompts?: boolean;
  sampling?: boolean;
  roots?: boolean;
  elicitation?: boolean;
}

/**
 * MCP client options
 */
interface MCPClientOptions {
  capabilities?: MCPClientCapabilities;
}

/**
 * MCP server information
 */
interface MCPServerInfo {
  name: string;
  version: string;
  capabilities: {
    resources?: ResourceCapabilities;
    tools?: ToolCapabilities;
    prompts?: PromptCapabilities;
    sampling?: SamplingCapabilities;
    roots?: RootsCapabilities;
    elicitation?: ElicitationCapabilities;
  };
}

// Additional interfaces for various capabilities
interface ResourceCapabilities {
  formats: string[];
  schemes: string[];
}

interface ToolCapabilities {
  allowList?: string[];
  denyList?: string[];
}

interface PromptCapabilities {
  allowList?: string[];
  denyList?: string[];
}

interface SamplingCapabilities {
  models: string[];
}

interface RootsCapabilities {
  schemes: string[];
}

interface ElicitationCapabilities {
  types: string[];
}

/**
 * Parameters for getResources request
 */
interface GetResourcesParams {
  uri: string;
  format?: string;
  limit?: number;
  offset?: number;
}

/**
 * Parameters for executeTool request
 */
interface ExecuteToolParams {
  tool: string;
  params: any;
}

/**
 * MCP resource interface
 */
interface MCPResource {
  uri: string;
  format: string;
  data: any;
  metadata?: any;
}

/**
 * MCP tool interface
 */
interface MCPTool {
  id: string;
  name: string;
  description: string;
  parameters: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
  returnType: {
    type: string;
    properties?: Record<string, any>;
  };
}
```

#### Message Translation Module

```typescript
/**
 * Translate GlassWall messages to MCP format
 */
export function glassWallToMCP(message: GlassWallMessage): MCPResource {
  return {
    uri: `glasswall://messages/${message.id}`,
    format: 'application/json',
    data: {
      content: message.content,
      sender: message.sender,
      timestamp: message.timestamp,
      roomId: message.roomId,
      attachments: message.attachments,
    },
    metadata: {
      source: 'glasswall',
      originalFormat: 'glasswall-message',
      messageType: message.type,
    },
  };
}

/**
 * Translate MCP resources to GlassWall messages
 */
export function mcpToGlassWall(resource: MCPResource): GlassWallMessage | null {
  // Only handle relevant resource types
  if (!resource.uri.startsWith('glasswall://') && 
      !resource.uri.startsWith('mcp://')) {
    return null;
  }
  
  // Extract data from resource
  const { data } = resource;
  
  // Create GlassWall message
  return {
    id: extractIdFromUri(resource.uri),
    content: data.content,
    sender: data.sender,
    timestamp: data.timestamp,
    roomId: data.roomId,
    type: resource.metadata?.messageType || 'text',
    attachments: data.attachments || [],
  };
}

/**
 * Extract ID from URI
 */
function extractIdFromUri(uri: string): string {
  const parts = uri.split('/');
  return parts[parts.length - 1];
}

/**
 * GlassWall message interface
 */
interface GlassWallMessage {
  id: string;
  content: string;
  sender: string;
  timestamp: string;
  roomId: string;
  type: string;
  attachments: any[];
}
```

### Test Implementation

```typescript
// Example test script for MCP client
import { MCPClient } from './mcp-client';

async function testMCPClient() {
  // Create MCP client
  const client = new MCPClient({
    capabilities: {
      resources: true,
      tools: true,
    },
  });
  
  try {
    // Connect to MCP server
    console.log('Connecting to MCP server...');
    const serverInfo = await client.connect('ws://localhost:9000/mcp');
    console.log('Connected to server:', serverInfo);
    
    // Get tools
    console.log('Getting available tools...');
    const tools = await client.getTools();
    console.log('Available tools:', tools);
    
    // Get resources
    console.log('Getting resources...');
    const resource = await client.getResources({
      uri: 'mcp://examples/resource1',
    });
    console.log('Resource:', resource);
    
    // Execute tool
    console.log('Executing tool...');
    const result = await client.executeTool({
      tool: 'example.echo',
      params: {
        message: 'Hello, MCP!',
      },
    });
    console.log('Tool result:', result);
    
    // Close connection
    await client.close();
    console.log('Connection closed');
  } catch (err) {
    console.error('Error:', err);
  }
}

// Run the test
testMCPClient();
```

### Integration with GlassWall

To integrate the MCP client with GlassWall, we will create an adapter module:

```typescript
import { MCPClient } from './mcp-client';
import { glassWallToMCP, mcpToGlassWall } from './message-translation';
import { MessageService } from '../services/MessageService';

/**
 * MCP integration adapter for GlassWall
 */
export class MCPAdapter {
  private client: MCPClient;
  private messageService: MessageService;
  private connectedServers: Map<string, MCPClient> = new Map();
  
  /**
   * Create a new MCP adapter
   */
  constructor(messageService: MessageService) {
    this.messageService = messageService;
    this.client = new MCPClient({
      capabilities: {
        resources: true,
        tools: true,
        prompts: true,
      },
    });
  }
  
  /**
   * Connect to an MCP server
   */
  public async connectToServer(serverUrl: string, name: string): Promise<boolean> {
    try {
      // Create a new client for this server
      const client = new MCPClient({
        capabilities: {
          resources: true,
          tools: true,
          prompts: true,
        },
      });
      
      // Connect to the server
      await client.connect(serverUrl);
      
      // Store the client
      this.connectedServers.set(name, client);
      
      return true;
    } catch (err) {
      console.error(`Error connecting to MCP server ${name}:`, err);
      return false;
    }
  }
  
  /**
   * Send a GlassWall message to an MCP server
   */
  public async sendMessage(serverName: string, message: any): Promise<any> {
    const client = this.connectedServers.get(serverName);
    if (!client) {
      throw new Error(`Not connected to MCP server: ${serverName}`);
    }
    
    // Translate the message to MCP format
    const mcpResource = glassWallToMCP(message);
    
    // Send the resource to the server
    // This is a simplified example - in practice, we would need to
    // determine the appropriate MCP method to call based on the message
    return client.sendRequest('processResource', {
      resource: mcpResource,
    });
  }
  
  /**
   * Get messages from an MCP server
   */
  public async getMessages(serverName: string, params: any): Promise<any[]> {
    const client = this.connectedServers.get(serverName);
    if (!client) {
      throw new Error(`Not connected to MCP server: ${serverName}`);
    }
    
    // Get resources from the server
    const resources = await client.getResources({
      uri: `mcp://${serverName}/messages`,
      ...params,
    });
    
    // Convert resources to GlassWall messages
    const messages = Array.isArray(resources) 
      ? resources.map(mcpToGlassWall).filter(Boolean)
      : [mcpToGlassWall(resources)].filter(Boolean);
    
    return messages;
  }
  
  /**
   * Execute a tool on an MCP server
   */
  public async executeTool(serverName: string, toolId: string, params: any): Promise<any> {
    const client = this.connectedServers.get(serverName);
    if (!client) {
      throw new Error(`Not connected to MCP server: ${serverName}`);
    }
    
    // Execute the tool on the server
    return client.executeTool({
      tool: toolId,
      params,
    });
  }
  
  /**
   * Disconnect from an MCP server
   */
  public async disconnectFromServer(serverName: string): Promise<void> {
    const client = this.connectedServers.get(serverName);
    if (client) {
      await client.close();
      this.connectedServers.delete(serverName);
    }
  }
  
  /**
   * Disconnect from all MCP servers
   */
  public async disconnectAll(): Promise<void> {
    for (const [name, client] of this.connectedServers) {
      await client.close();
    }
    this.connectedServers.clear();
  }
}
```

## Phase 2: MCP Server Implementation

**Timeframe:** 4 weeks
**Goal:** Implement an MCP server endpoint in GlassWall to allow external agents to interact with GlassWall resources and tools.

### Technical Components

1. **MCP Server API Endpoint**
   - Create server endpoint at /api/mcp
   - Implement WebSocket upgrade handling
   - Support HTTP fallback for non-WebSocket clients

2. **Resource Exposure**
   - Expose message histories as resources
   - Add room and user information as resources
   - Implement resource query capabilities

3. **Tool Registration**
   - Register GlassWall-specific tools
   - Implement tool execution with permission validation
   - Add audit logging for tool execution

### Implementation Details

#### MCP Server Class Structure

```typescript
/**
 * Main MCP server class that handles communication with MCP clients
 */
export class MCPServer {
  private capabilities: MCPServerCapabilities;
  private tools: Map<string, ToolHandler> = new Map();
  private clients: Set<MCPConnection> = new Set();
  
  /**
   * Create a new MCP server
   */
  constructor(options: MCPServerOptions) {
    this.capabilities = options.capabilities || {
      resources: {
        formats: ['text', 'json'],
        schemes: ['glasswall'],
      },
      tools: {
        allowList: [],
      },
    };
  }
  
  /**
   * Handle a new WebSocket connection
   */
  public handleConnection(ws: WebSocket): void {
    // Create a new connection
    const connection = new MCPConnection(ws);
    
    // Add the connection to the set
    this.clients.add(connection);
    
    // Setup event handlers
    connection.onMessage(this.handleMessage.bind(this, connection));
    connection.onClose(() => {
      this.clients.delete(connection);
    });
  }
  
  /**
   * Handle an incoming message from a connection
   */
  private async handleMessage(connection: MCPConnection, message: JsonRpcMessage): Promise<void> {
    // Only handle request messages
    if (!('method' in message) || !('id' in message)) {
      return;
    }
    
    // Handle the request based on the method
    switch (message.method) {
      case 'initialize':
        await this.handleInitialize(connection, message);
        break;
      case 'getResources':
        await this.handleGetResources(connection, message);
        break;
      case 'executeTool':
        await this.handleExecuteTool(connection, message);
        break;
      case 'getTools':
        await this.handleGetTools(connection, message);
        break;
      default:
        // Unknown method
        connection.sendError(message.id, -32601, `Method not found: ${message.method}`);
    }
  }
  
  /**
   * Handle initialize request
   */
  private async handleInitialize(connection: MCPConnection, request: JsonRpcRequest): Promise<void> {
    // Extract client capabilities
    const { capabilities, clientInfo } = request.params;
    
    // Store client capabilities in the connection
    connection.setCapabilities(capabilities);
    connection.setClientInfo(clientInfo);
    
    // Send response with server capabilities
    connection.sendResult(request.id, {
      name: 'GlassWall-MCP-Server',
      version: '0.1.0',
      capabilities: this.capabilities,
    });
  }
  
  /**
   * Handle getResources request
   */
  private async handleGetResources(connection: MCPConnection, request: JsonRpcRequest): Promise<void> {
    try {
      // Extract parameters
      const { uri, format, limit, offset } = request.params;
      
      // Get resources based on URI
      const resources = await this.getResources(uri, { format, limit, offset });
      
      // Send response with resources
      connection.sendResult(request.id, resources);
    } catch (err) {
      connection.sendError(
        request.id,
        -32603,
        `Error getting resources: ${err instanceof Error ? err.message : String(err)}`
      );
    }
  }
  
  /**
   * Handle executeTool request
   */
  private async handleExecuteTool(connection: MCPConnection, request: JsonRpcRequest): Promise<void> {
    try {
      // Extract parameters
      const { tool, params } = request.params;
      
      // Check if tool is allowed
      if (!this.isToolAllowed(tool)) {
        throw new Error(`Tool not allowed: ${tool}`);
      }
      
      // Get tool handler
      const handler = this.tools.get(tool);
      if (!handler) {
        throw new Error(`Tool not found: ${tool}`);
      }
      
      // Execute tool
      const result = await handler(params, {
        clientInfo: connection.getClientInfo(),
        clientCapabilities: connection.getCapabilities(),
      });
      
      // Send response with result
      connection.sendResult(request.id, result);
    } catch (err) {
      connection.sendError(
        request.id,
        -32603,
        `Error executing tool: ${err instanceof Error ? err.message : String(err)}`
      );
    }
  }
  
  /**
   * Handle getTools request
   */
  private async handleGetTools(connection: MCPConnection, request: JsonRpcRequest): Promise<void> {
    try {
      // Get allowed tools
      const tools = Array.from(this.tools.entries())
        .filter(([id]) => this.isToolAllowed(id))
        .map(([id, handler]) => {
          // Get tool metadata
          return {
            id,
            name: handler.metadata?.name || id,
            description: handler.metadata?.description || '',
            parameters: handler.metadata?.parameters || { type: 'object', properties: {} },
            returnType: handler.metadata?.returnType || { type: 'object' },
          };
        });
      
      // Send response with tools
      connection.sendResult(request.id, tools);
    } catch (err) {
      connection.sendError(
        request.id,
        -32603,
        `Error getting tools: ${err instanceof Error ? err.message : String(err)}`
      );
    }
  }
  
  /**
   * Check if a tool is allowed
   */
  private isToolAllowed(toolId: string): boolean {
    // If no allowList specified, all tools are allowed
    if (!this.capabilities.tools?.allowList) {
      return true;
    }
    
    // Check if tool is in allowList
    return this.capabilities.tools.allowList.includes(toolId);
  }
  
  /**
   * Register a tool
   */
  public registerTool(id: string, handler: ToolHandler): void {
    this.tools.set(id, handler);
  }
  
  /**
   * Get resources based on URI
   */
  private async getResources(uri: string, options: GetResourcesOptions): Promise<MCPResource | MCPResource[]> {
    // Parse URI to determine resource type
    const parsedUri = new URL(uri);
    
    // Handle different resource types
    switch (parsedUri.protocol) {
      case 'glasswall:':
        return this.getGlassWallResources(parsedUri, options);
      default:
        throw new Error(`Unsupported URI scheme: ${parsedUri.protocol}`);
    }
  }
  
  /**
   * Get GlassWall resources
   */
  private async getGlassWallResources(uri: URL, options: GetResourcesOptions): Promise<MCPResource | MCPResource[]> {
    const path = uri.pathname.split('/').filter(Boolean);
    
    // Handle different resource paths
    switch (path[0]) {
      case 'messages':
        return this.getMessageResources(path.slice(1), options);
      case 'rooms':
        return this.getRoomResources(path.slice(1), options);
      case 'users':
        return this.getUserResources(path.slice(1), options);
      default:
        throw new Error(`Unknown GlassWall resource: ${path[0]}`);
    }
  }
  
  /**
   * Get message resources
   */
  private async getMessageResources(path: string[], options: GetResourcesOptions): Promise<MCPResource | MCPResource[]> {
    // Implementation would depend on GlassWall's internal message service
    // This is a placeholder
    return {
      uri: `glasswall://messages/${path[0] || 'all'}`,
      format: options.format || 'application/json',
      data: {
        messages: [
          {
            id: 'msg1',
            content: 'Hello, world!',
            sender: 'user1',
            timestamp: new Date().toISOString(),
          },
        ],
      },
    };
  }
  
  /**
   * Get room resources
   */
  private async getRoomResources(path: string[], options: GetResourcesOptions): Promise<MCPResource | MCPResource[]> {
    // Implementation would depend on GlassWall's internal room service
    // This is a placeholder
    return {
      uri: `glasswall://rooms/${path[0] || 'all'}`,
      format: options.format || 'application/json',
      data: {
        rooms: [
          {
            id: 'room1',
            name: 'General',
            description: 'General chat room',
            createdAt: new Date().toISOString(),
          },
        ],
      },
    };
  }
  
  /**
   * Get user resources
   */
  private async getUserResources(path: string[], options: GetResourcesOptions): Promise<MCPResource | MCPResource[]> {
    // Implementation would depend on GlassWall's internal user service
    // This is a placeholder
    return {
      uri: `glasswall://users/${path[0] || 'all'}`,
      format: options.format || 'application/json',
      data: {
        users: [
          {
            id: 'user1',
            name: 'John Doe',
            avatarUrl: 'https://example.com/avatar.png',
            createdAt: new Date().toISOString(),
          },
        ],
      },
    };
  }
}

/**
 * MCP connection class that wraps a WebSocket connection
 */
class MCPConnection {
  private ws: WebSocket;
  private capabilities: any = {};
  private clientInfo: any = {};
  
  /**
   * Create a new MCP connection
   */
  constructor(ws: WebSocket) {
    this.ws = ws;
  }
  
  /**
   * Set client capabilities
   */
  public setCapabilities(capabilities: any): void {
    this.capabilities = capabilities;
  }
  
  /**
   * Get client capabilities
   */
  public getCapabilities(): any {
    return this.capabilities;
  }
  
  /**
   * Set client info
   */
  public setClientInfo(clientInfo: any): void {
    this.clientInfo = clientInfo;
  }
  
  /**
   * Get client info
   */
  public getClientInfo(): any {
    return this.clientInfo;
  }
  
  /**
   * Send a message to the client
   */
  public send(message: any): void {
    this.ws.send(JSON.stringify(message));
  }
  
  /**
   * Send a result to the client
   */
  public sendResult(id: string, result: any): void {
    this.send({
      jsonrpc: '2.0',
      id,
      result,
    });
  }
  
  /**
   * Send an error to the client
   */
  public sendError(id: string, code: number, message: string, data?: any): void {
    this.send({
      jsonrpc: '2.0',
      id,
      error: {
        code,
        message,
        data,
      },
    });
  }
  
  /**
   * Send a notification to the client
   */
  public sendNotification(method: string, params: any): void {
    this.send({
      jsonrpc: '2.0',
      method,
      params,
    });
  }
  
  /**
   * Set up message handler
   */
  public onMessage(handler: (message: any) => void): void {
    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data as string);
        handler(message);
      } catch (err) {
        console.error('Error parsing message:', err);
      }
    };
  }
  
  /**
   * Set up close handler
   */
  public onClose(handler: () => void): void {
    this.ws.onclose = () => {
      handler();
    };
  }
}

/**
 * Tool handler function
 */
type ToolHandler = (params: any, context: ToolContext) => Promise<any>;

/**
 * Tool context
 */
interface ToolContext {
  clientInfo: any;
  clientCapabilities: any;
}

/**
 * Options for getResources
 */
interface GetResourcesOptions {
  format?: string;
  limit?: number;
  offset?: number;
}

/**
 * MCP server capabilities
 */
interface MCPServerCapabilities {
  resources?: {
    formats: string[];
    schemes: string[];
  };
  tools?: {
    allowList?: string[];
    denyList?: string[];
  };
  prompts?: {
    allowList?: string[];
    denyList?: string[];
  };
  sampling?: {
    models: string[];
  };
  roots?: {
    schemes: string[];
  };
  elicitation?: {
    types: string[];
  };
}

/**
 * MCP server options
 */
interface MCPServerOptions {
  capabilities?: MCPServerCapabilities;
}

/**
 * Add metadata to tool handler
 */
interface ToolHandlerWithMetadata extends Function {
  metadata?: {
    name?: string;
    description?: string;
    parameters?: {
      type: string;
      properties: Record<string, any>;
      required?: string[];
    };
    returnType?: {
      type: string;
      properties?: Record<string, any>;
    };
  };
}

declare global {
  interface WebSocket {
    onmessage: (event: MessageEvent) => void;
    onerror: (event: Event) => void;
    onclose: (event: CloseEvent) => void;
    onopen: () => void;
    send: (data: string) => void;
    close: () => void;
  }
}
```

### API Implementation

```typescript
// Next.js API route for MCP server
import { NextApiRequest, NextApiResponse } from 'next';
import { MCPServer } from '@/lib/mcp/server';
import { MessageService } from '@/services/MessageService';
import { UserService } from '@/services/UserService';
import { RoomService } from '@/services/RoomService';

// Create MCP server instance
const mcpServer = new MCPServer({
  capabilities: {
    resources: {
      formats: ['text', 'json'],
      schemes: ['glasswall'],
    },
    tools: {
      allowList: [
        'glasswall.message.send',
        'glasswall.message.list',
        'glasswall.room.list',
        'glasswall.user.info',
      ],
    },
  },
});

// Register tools
mcpServer.registerTool('glasswall.message.send', async (params, context) => {
  const { roomId, content } = params;
  
  // Get services
  const messageService = new MessageService();
  
  // Send message
  const message = await messageService.sendMessage(roomId, {
    content,
    sender: context.clientInfo.name || 'MCP Client',
    type: 'text',
  });
  
  return {
    id: message.id,
    timestamp: message.timestamp,
  };
});

mcpServer.registerTool('glasswall.message.list', async (params, context) => {
  const { roomId, limit = 10 } = params;
  
  // Get services
  const messageService = new MessageService();
  
  // Get messages
  const messages = await messageService.getMessages(roomId, limit);
  
  return {
    messages,
  };
});

mcpServer.registerTool('glasswall.room.list', async (params, context) => {
  // Get services
  const roomService = new RoomService();
  
  // Get rooms
  const rooms = await roomService.getRooms();
  
  return {
    rooms,
  };
});

mcpServer.registerTool('glasswall.user.info', async (params, context) => {
  const { userId } = params;
  
  // Get services
  const userService = new UserService();
  
  // Get user
  const user = await userService.getUser(userId);
  
  return {
    user,
  };
});

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    // Return server information
    res.status(200).json({
      name: 'GlassWall-MCP-Server',
      version: '0.1.0',
      description: 'MCP server for GlassWall',
    });
    return;
  }
  
  if (req.method === 'POST') {
    // Handle HTTP request
    try {
      const request = req.body;
      
      // Process the request
      // This would require implementing the HTTP version of the MCP server
      // For simplicity, we'll just return an error for now
      res.status(501).json({
        error: 'HTTP MCP not implemented yet - use WebSocket endpoint',
      });
    } catch (err) {
      res.status(500).json({
        error: 'Internal server error',
      });
    }
    return;
  }
  
  // Method not allowed
  res.status(405).json({
    error: 'Method not allowed',
  });
}

// Enable WebSocket support
export const config = {
  api: {
    bodyParser: false,
  },
};
```

## Phase 3: Advanced Features

**Timeframe:** 4 weeks
**Goal:** Implement advanced MCP features including agent identity, complex resource types, and specialized room types.

### Technical Components

1. **Agent Identity System**
   - Implement agent verification system
   - Add agent-specific credentials
   - Create agent profile pages

2. **Complex Resource Types**
   - Support for specialized message formats
   - Add structured data resources
   - Implement file and media resources

3. **Agent Room Types**
   - Create specialized rooms for agent-to-agent communication
   - Add agent orchestration capabilities
   - Implement performance monitoring

### Implementation Details

(Detailed implementation for Phase 3 will be developed after successful completion of Phases 1 and 2)

## Testing Plan

### Unit Tests

```typescript
// Unit tests for MCP client
import { MCPClient } from '../src/mcp-client';
import { MockWebSocket } from './mocks/mock-websocket';

describe('MCPClient', () => {
  let client: MCPClient;
  
  beforeEach(() => {
    // Create client with mock capabilities
    client = new MCPClient({
      capabilities: {
        resources: true,
        tools: true,
      },
    });
  });
  
  test('should connect to an MCP server', async () => {
    // Mock WebSocket implementation
    const mockWs = new MockWebSocket();
    
    // Set up mock responses
    mockWs.addResponseForMethod('initialize', {
      name: 'MockMCPServer',
      version: '1.0.0',
      capabilities: {
        resources: {
          formats: ['text', 'json'],
          schemes: ['mock'],
        },
        tools: {
          allowList: ['mock.echo'],
        },
      },
    });
    
    // Connect to server
    const serverInfo = await client.connect('ws://mock-server');
    
    // Verify server info
    expect(serverInfo.name).toBe('MockMCPServer');
    expect(serverInfo.version).toBe('1.0.0');
    expect(serverInfo.capabilities.resources.formats).toContain('text');
    expect(serverInfo.capabilities.resources.formats).toContain('json');
    expect(serverInfo.capabilities.resources.schemes).toContain('mock');
    expect(serverInfo.capabilities.tools.allowList).toContain('mock.echo');
  });
  
  // Add more tests for client functionality
});

// Integration tests for MCP adapter
import { MCPAdapter } from '../src/mcp-adapter';
import { MessageService } from '../src/services/MessageService';

describe('MCPAdapter', () => {
  let adapter: MCPAdapter;
  let messageService: MessageService;
  
  beforeEach(() => {
    // Create mock message service
    messageService = new MockMessageService();
    
    // Create adapter
    adapter = new MCPAdapter(messageService);
  });
  
  test('should connect to an MCP server', async () => {
    // Connect to server
    const result = await adapter.connectToServer('ws://mock-server', 'mock');
    
    // Verify result
    expect(result).toBe(true);
  });
  
  // Add more integration tests
});
```

### Performance Tests

```typescript
// Performance tests for MCP client
import { MCPClient } from '../src/mcp-client';

describe('MCPClient Performance', () => {
  let client: MCPClient;
  
  beforeEach(() => {
    // Create client
    client = new MCPClient({
      capabilities: {
        resources: true,
        tools: true,
      },
    });
  });
  
  test('should handle high message throughput', async () => {
    // Connect to server
    await client.connect('ws://perf-server');
    
    // Start time
    const start = Date.now();
    
    // Send 1000 messages
    const promises = [];
    for (let i = 0; i < 1000; i++) {
      promises.push(client.executeTool({
        tool: 'perf.echo',
        params: {
          message: `Message ${i}`,
        },
      }));
    }
    
    // Wait for all messages to be processed
    await Promise.all(promises);
    
    // End time
    const end = Date.now();
    
    // Calculate throughput
    const duration = (end - start) / 1000;
    const throughput = 1000 / duration;
    
    // Verify throughput is above threshold
    expect(throughput).toBeGreaterThan(100);
  });
  
  // Add more performance tests
});
```

## Security Considerations

### User Consent and Control

- Implement explicit user consent for all MCP operations
- Create UI components for reviewing and authorizing activities
- Add permission management for different resource types

### Data Privacy

- Ensure user data is not exposed without permission
- Implement access controls for sensitive resources
- Add audit logging for all data access operations

### Tool Safety

- Implement tool execution sandboxing
- Add permission checks for all tool executions
- Create admin controls for enabling/disabling tools

### LLM Sampling Controls

- Implement explicit user approval for LLM sampling
- Add controls for what prompts are sent
- Limit server visibility into prompts

## Conclusion

This implementation plan provides a detailed roadmap for adding MCP support to GlassWall. By following this phased approach, we can incrementally add MCP features while ensuring security and maintainability.

The initial prototype phase will allow us to validate the technical approach and identify any challenges early. The subsequent phases will build on this foundation to create a full-featured MCP implementation that positions GlassWall as a central hub in the AI agent ecosystem.

## References

- [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Next.js API Routes](https://nextjs.org/docs/api-routes/introduction)