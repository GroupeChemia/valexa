//This will run transcrypt on serve or build
const child_process = require('child_process');
const path = require('path')

let cmd_parts = [
    'python -m transcrypt',
    '--nomin',
    //'--map',
    'canvas'
];
let cmd_options = {
    
    'cwd': path.join(__dirname, "src/ploting"),
};
try {
    let stdout = child_process.execSync(cmd_parts.join(' '), cmd_options).toString();
} catch (err) {
    throw Error(err.stdout.toString() + '\n' + err.stderr.toString());
} 
  
module.exports = {
    configureWebpack: {
      plugins: []
    }
  }