#!/usr/bin/env node
/**
 * Mermaid Diagram Generator
 * Generate Mermaid diagrams from natural language descriptions
 */

const fs = require("fs");
const path = require("path");

function generateFlowchart(description) {
  // Parse description and generate Mermaid syntax
  // This is a simple template - could be enhanced with AI

  return `\`\`\`mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
\`\`\``;
}

function generateSequenceDiagram(description) {
  return `\`\`\`mermaid
sequenceDiagram
    participant User
    participant Nike
    participant System
    
    User->>Nike: Request
    Nike->>System: Process
    System-->>Nike: Response
    Nike-->>User: Result
\`\`\``;
}

function generateGantt(description) {
  return `\`\`\`mermaid
gantt
    title Project Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1
    Task 1           :a1, 2026-02-01, 7d
    Task 2           :after a1, 5d
    section Phase 2
    Task 3           :2026-02-10, 10d
\`\`\``;
}

function generateERDiagram(description) {
  return `\`\`\`mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
\`\`\``;
}

function generateClassDiagram(description) {
  return `\`\`\`mermaid
classDiagram
    class Agent {
        +String name
        +String role
        +execute()
        +learn()
    }
    class Task {
        +String title
        +String status
        +complete()
    }
    Agent --> Task : manages
\`\`\``;
}

// CLI interface
const args = process.argv.slice(2);
const command = args[0];
const description = args.slice(1).join(" ");

const generators = {
  flow: generateFlowchart,
  sequence: generateSequenceDiagram,
  gantt: generateGantt,
  er: generateERDiagram,
  class: generateClassDiagram,
};

if (!command || !generators[command]) {
  console.log("Usage: generate-diagram.js <type> [description]");
  console.log("");
  console.log("Types:");
  console.log("  flow      - Flowchart diagram");
  console.log("  sequence  - Sequence diagram");
  console.log("  gantt     - Gantt chart");
  console.log("  er        - Entity-Relationship diagram");
  console.log("  class     - Class diagram");
  console.log("");
  console.log("Example:");
  console.log('  generate-diagram.js flow "User login process"');
  process.exit(1);
}

const diagram = generators[command](description);
console.log(diagram);
console.log("");
console.log("💡 Copy this Mermaid code to:");
console.log("   - GitHub README.md");
console.log("   - Notion (paste as code block with language: mermaid)");
console.log("   - https://mermaid.live (visualize online)");
