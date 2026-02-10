import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const taskStatusFilePath = path.resolve('/Users/karst/.openclaw/workspace/current-task-status.json');

export async function GET() {
  try {
    // Check if the file exists, if not create it with default content
    if (!fs.existsSync(taskStatusFilePath)) {
      const defaultContent = {
        currentTaskStatus: 'No active task',
        lastUpdated: new Date().toISOString()
      };
      fs.writeFileSync(taskStatusFilePath, JSON.stringify(defaultContent, null, 2));
    }
    
    // Read the file
    const fileContent = fs.readFileSync(taskStatusFilePath, 'utf8');
    
    // Parse the JSON
    const data = JSON.parse(fileContent);
    
    // Return the data
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error reading current-task-status.json:', error);
    return NextResponse.json(
      { error: 'Failed to read current task status', currentTaskStatus: 'Error loading task status' },
      { status: 500 }
    );
  }
}