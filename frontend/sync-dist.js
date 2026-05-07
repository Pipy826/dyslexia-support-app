/**
 * 构建后同步脚本：将 dist/build/h5/ 的内容复制到 dist/
 * 使 HBuilderX 8080 端口服务的 dist/ 目录保持最新
 */
const fs = require('fs')
const path = require('path')

const src = path.join(__dirname, 'dist', 'build', 'h5')
const dst = path.join(__dirname, 'dist')

if (!fs.existsSync(src)) {
  console.log('sync-dist: src not found, skip')
  process.exit(0)
}

function copyRecursive(srcDir, dstDir) {
  if (!fs.existsSync(dstDir)) {
    fs.mkdirSync(dstDir, { recursive: true })
  }
  const entries = fs.readdirSync(srcDir, { withFileTypes: true })
  for (const entry of entries) {
    const srcPath = path.join(srcDir, entry.name)
    const dstPath = path.join(dstDir, entry.name)
    if (entry.isDirectory()) {
      copyRecursive(srcPath, dstPath)
    } else {
      fs.copyFileSync(srcPath, dstPath)
    }
  }
}

copyRecursive(src, dst)
console.log('sync-dist: dist/build/h5 -> dist OK')
