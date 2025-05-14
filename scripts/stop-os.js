#!/usr/bin/env node

/**
 * OS-specific stop script for Emotika
 * This script detects the operating system and runs the appropriate stop script
 */

const { execSync } = require('child_process');
const os = require('os');
const fs = require('fs');
const path = require('path');

// Get the platform
const platform = os.platform();

console.log(`Detected platform: ${platform}`);

// Run the appropriate script based on the platform
if (platform === 'win32') {
  // Windows
  console.log('\x1b[36m%s\x1b[0m', 'Running Windows stop script...');
  
  // Check if PowerShell script exists
  if (fs.existsSync(path.join(__dirname, '..', 'stop.ps1'))) {
    try {
      execSync('powershell -ExecutionPolicy Bypass -File stop.ps1', { stdio: 'inherit' });
    } catch (error) {
      console.error('\x1b[31m%s\x1b[0m', 'Error running PowerShell script. Falling back to npm run stop');
      execSync('npm run stop', { stdio: 'inherit' });
    }
  } else {
    console.log('\x1b[33m%s\x1b[0m', 'PowerShell script not found. Using npm run stop');
    execSync('npm run stop', { stdio: 'inherit' });
  }
} else {
  // Linux/macOS
  console.log('\x1b[36m%s\x1b[0m', 'Running Linux/macOS stop script...');
  
  // Check if bash script exists
  if (fs.existsSync(path.join(__dirname, '..', 'stop.sh'))) {
    try {
      // Make the script executable
      execSync('chmod +x stop.sh', { stdio: 'ignore' });
      execSync('./stop.sh', { stdio: 'inherit' });
    } catch (error) {
      console.error('\x1b[31m%s\x1b[0m', 'Error running bash script. Falling back to npm run stop');
      execSync('npm run stop', { stdio: 'inherit' });
    }
  } else {
    console.log('\x1b[33m%s\x1b[0m', 'Bash script not found. Using npm run stop');
    execSync('npm run stop', { stdio: 'inherit' });
  }
} 