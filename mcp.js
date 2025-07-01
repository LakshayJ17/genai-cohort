import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { z } from 'zod'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'


const server = new McpServer({
    name: 'genai-cohort',
    version: '1.0.0'
})

server.registerTool('addTwoNumbers',
    {
        title: 'Add Numbers',
        description: 'Adds two numbers',
        inputSchema: { a: z.number(), b: z.number() },
    },
    async function ({ a, b }) {
        return { content: [{ type: 'text', text: String(a + b) }] }
    }
)

const transport = new StdioServerTransport()

server.connect(transport)
