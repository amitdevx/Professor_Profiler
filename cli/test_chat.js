const { spawn } = require('child_process');

const child = spawn('node', ['dist/index.js', 'chat'], {
    cwd: __dirname,
});

let output = '';

child.stdout.on('data', (data) => {
    const chunk = data.toString();
    output += chunk;
    process.stdout.write(chunk);
    
    // Once the prompt appears, we send our first message
    if (chunk.includes('prof ›')) {
        if (!output.includes('@test.txt')) {
            console.log('Sending file attachment command...');
            child.stdin.write('@test.txt What is this file about?\n');
        } else if (!output.includes('Goodbye')) {
            console.log('Sending exit command...');
            child.stdin.write('/exit\n');
        }
    }
});

child.stderr.on('data', (data) => {
    process.stderr.write(data);
});

child.on('close', (code) => {
    console.log('Child process exited with code ' + code);
});
