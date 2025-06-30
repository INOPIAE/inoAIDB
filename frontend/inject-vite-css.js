const fs = require('fs')
const path = require('path')

const distDir = path.join(__dirname, 'dist')
const hdocsDir = path.join(__dirname, 'public', 'hdocs')
const manifestPath = path.join(distDir, '.vite', 'manifest.json')

const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'))

const entry = Object.values(manifest).find(e => e.isEntry)
const cssFiles = entry?.css || []

if (cssFiles.length === 0) {
  console.error('❌ No CSS-files found in manifest.')
  process.exit(1)
}

const cssLinkTag = `<link rel="stylesheet" href="/dist/${cssFiles[0]}">`

fs.readdirSync(hdocsDir)
  .filter(file => file.endsWith('.html'))
  .forEach(file => {
    const filePath = path.join(hdocsDir, file)
    let html = fs.readFileSync(filePath, 'utf-8')

    if (html.includes(cssFiles[0])) {
      console.log(`✔️  ${file} contains stylesheet.`)
      return
    }

    html = html.replace(/<head[^>]*>/i, match => `${match}\n  ${cssLinkTag}`)
    fs.writeFileSync(filePath, html, 'utf-8')
    console.log(`✅ CSS in ${file} included.`)
  })
