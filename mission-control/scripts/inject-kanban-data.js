const fs = require('fs');
const path = require('path');

// Function to safely read the kanban data from different locations
function readKanbanData() {
  const possiblePaths = [
    // Primary location
    '/Users/karst/.openclaw/workspace/kanban-board.json',
    // Fallback to local data directory if it exists
    path.resolve(__dirname, '../data/kanban-board.json')
  ];
  
  for (const filePath of possiblePaths) {
    try {
      if (fs.existsSync(filePath)) {
        console.log(`Reading kanban data from: ${filePath}`);
        return JSON.parse(fs.readFileSync(filePath, 'utf8'));
      }
    } catch (error) {
      console.warn(`Could not read kanban data from ${filePath}:`, error.message);
    }
  }
  
  // If no files found, return minimal structure
  console.log('No kanban data found, using minimal structure');
  return {
    "lastUpdated": new Date().toISOString(),
    "columns": [
      {
        "id": "backlog",
        "title": "To Do",
        "tasks": []
      },
      {
        "id": "in-progress",
        "title": "In Progress",
        "tasks": []
      },
      {
        "id": "testing",
        "title": "Review",
        "tasks": []
      },
      {
        "id": "completed",
        "title": "Done",
        "tasks": []
      }
    ]
  };
}

// Main function
async function injectKanbanData() {
  try {
    // Read the kanban data
    const kanbanData = readKanbanData();
    
    // Create the API directory if it doesn't exist
    const apiDir = path.resolve(__dirname, '../src/app/api/kanban-data');
    if (!fs.existsSync(apiDir)) {
      fs.mkdirSync(apiDir, { recursive: true });
    }
    
    // Create the API route file
    const apiRoutePath = path.resolve(apiDir, 'route.ts');
    const apiContent = `import { NextResponse } from 'next/server';

// Kanban data injected during build
const KANBAN_DATA = ${JSON.stringify(kanbanData, null, 2)};

export async function GET() {
  return NextResponse.json(KANBAN_DATA);
}

export async function POST(request: Request) {
  try {
    const data = await request.json();
    // In a real app, you would save the data to a database here
    return NextResponse.json({ success: true, message: 'Data received' });
  } catch (error) {
    return NextResponse.json({ success: false, message: 'Error processing request' }, { status: 400 });
  }
}
`;
    
    // Write to the API route file
    fs.writeFileSync(apiRoutePath, apiContent);
    console.log('Kanban data injected into API endpoint');
    
    // Create a local data directory and copy the file there as a backup
    const dataDir = path.resolve(__dirname, '../data');
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }
    
    fs.writeFileSync(
      path.resolve(dataDir, 'kanban-board.json'),
      JSON.stringify(kanbanData, null, 2)
    );
    console.log('Kanban data backed up to data directory');
    
    return true;
  } catch (error) {
    console.error('Error injecting kanban data:', error);
    process.exit(1);
  }
}

// Execute if run directly
if (require.main === module) {
  injectKanbanData();
}

module.exports = injectKanbanData;