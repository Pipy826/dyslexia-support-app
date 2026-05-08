/**
 * 开发模式启动脚本
 * 启动 Vite H5 开发服务器，并在终端打印访问二维码
 *
 * 用法：
 *   node dev-qr.js              → 局域网二维码（同 WiFi 可用）
 *   node dev-qr.js --tunnel     → 公网二维码（任何人可用，需先启动 ngrok/cpolar）
 *   node dev-qr.js --url <url>  → 指定公网地址生成二维码
 */

const { spawn } = require('child_process');
const os = require('os');
const http = require('http');

const PORT = 5173;
const args = process.argv.slice(2);
const useTunnel = args.includes('--tunnel');
const customUrl = args.includes('--url') ? args[args.indexOf('--url') + 1] : null;

// 获取局域网 IP
function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return 'localhost';
}

// 从 ngrok API 获取公网地址
function getNgrokUrl() {
  return new Promise((resolve, reject) => {
    http.get('http://localhost:4040/api/tunnels', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          const tunnel = json.tunnels.find(t => t.proto === 'https') || json.tunnels[0];
          resolve(tunnel ? tunnel.public_url : null);
        } catch {
          resolve(null);
        }
      });
    }).on('error', () => resolve(null));
  });
}

// 打印二维码
function printQR(url, label) {
  try {
    const qrcode = require('qrcode-terminal');
    console.log('\n' + '='.repeat(52));
    console.log(`  📱 ${label}`);
    console.log('='.repeat(52));
    qrcode.generate(url, { small: true });
    console.log(`  地址：${url}`);
    console.log('='.repeat(52) + '\n');
  } catch {
    console.log('\n' + '='.repeat(52));
    console.log(`  📱 ${label}`);
    console.log(`  地址：${url}`);
    console.log('='.repeat(52) + '\n');
  }
}

// 启动 Vite
const vite = spawn('npm', ['run', 'dev:h5'], {
  stdio: 'inherit',
  shell: true,
});

// 等待 Vite 启动后显示二维码
setTimeout(async () => {
  if (customUrl) {
    // 用户手动指定了公网地址
    printQR(customUrl, '公网访问二维码（任何人可扫）');
  } else if (useTunnel) {
    // 尝试从 ngrok 获取公网地址
    console.log('\n⏳ 正在获取 ngrok 公网地址...');
    const ngrokUrl = await getNgrokUrl();
    if (ngrokUrl) {
      printQR(ngrokUrl, '公网访问二维码（任何人可扫）');
    } else {
      console.log('\n❌ 未检测到 ngrok，请先在另一个终端运行：');
      console.log('   ngrok http 5173\n');
      console.log('   然后重新运行：node dev-qr.js --tunnel\n');
      // 降级为局域网二维码
      const localUrl = `http://${getLocalIP()}:${PORT}`;
      printQR(localUrl, '局域网二维码（仅同 WiFi 可用）');
    }
  } else {
    // 默认：局域网二维码
    const localUrl = `http://${getLocalIP()}:${PORT}`;
    printQR(localUrl, '局域网二维码（需连接同一 WiFi）');
    console.log('  💡 想让任何人都能访问？运行：node dev-qr.js --tunnel');
    console.log('     （需先安装并启动 ngrok 或 cpolar）\n');
  }
}, 3000);

vite.on('close', (code) => process.exit(code));
