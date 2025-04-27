#!/usr/bin/env node

/**
 * OS-specific start script for Emotika
 * This script detects the operating system and runs the appropriate start script
 */

const { execSync } = require('child_process');
const os = require('os');
const fs = require('fs');
const path = require('path');

// Get the platform
const platform = os.platform();

console.log(`Detected platform: ${platform}`);

// Check if Docker is running
try {
  execSync('docker info', { stdio: 'ignore' });
} catch (error) {
  console.error('\x1b[31m%s\x1b[0m', 'Docker is not running. Please start Docker and try again.');
  process.exit(1);
}

// Check if npm is installed
try {
  const npmVersion = execSync('npm --version').toString().trim();
  console.log(`\x1b[36m%s\x1b[0m`, `Using npm version ${npmVersion}`);
} catch (error) {
  console.error('\x1b[31m%s\x1b[0m', 'npm is not installed or not in PATH. Please install Node.js and try again.');
  process.exit(1);
}

// Run the appropriate script based on the platform
if (platform === 'win32') {
  // Windows
  console.log('\x1b[36m%s\x1b[0m', 'Running Windows start script...');
  
  // Check if PowerShell script exists
  if (fs.existsSync(path.join(__dirname, '..', 'start.ps1'))) {
    try {
      execSync('powershell -ExecutionPolicy Bypass -File start.ps1', { stdio: 'inherit' });
    } catch (error) {
      console.error('\x1b[31m%s\x1b[0m', 'Error running PowerShell script. Falling back to npm run dev');
      execSync('npm run dev', { stdio: 'inherit' });
    }
  } else {
    console.log('\x1b[33m%s\x1b[0m', 'PowerShell script not found. Using npm run dev');
    execSync('npm run dev', { stdio: 'inherit' });
  }
} else {
  // Linux/macOS
  console.log('\x1b[36m%s\x1b[0m', 'Running Linux/macOS start script...');
  
  // Check if bash script exists
  if (fs.existsSync(path.join(__dirname, '..', 'start.sh'))) {
    try {
      // Make the script executable
      execSync('chmod +x start.sh', { stdio: 'ignore' });
      execSync('./start.sh', { stdio: 'inherit' });
    } catch (error) {
      console.error('\x1b[31m%s\x1b[0m', 'Error running bash script. Falling back to npm run dev');
      execSync('npm run dev', { stdio: 'inherit' });
    }
  } else {
    console.log('\x1b[33m%s\x1b[0m', 'Bash script not found. Using npm run dev');
    execSync('npm run dev', { stdio: 'inherit' });
  }
} 