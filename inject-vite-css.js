// inject-vite-css.js
const fs = require('fs')
const path = require('path')

// 1. Pfade
const distDir = path.join(__dirname, 'frontend', 'dist')
const hdocsDir = path.join(__dirname, 'frontend', 'public', 'hdocs')
const manifestPath = path.join(distDir, 'manifest.json')

// 2. Manifest lesen
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'))

// 3. CSS-Datei ermitteln
const entry = Object.values(manifest).find(e => e.isEntry)
const cssFiles = entry?.css || []

if (cssFiles.length === 0) {
  console.error('❌ No CSS-files found in manifest.')
  process.exit(1)
}

// 4. CSS-Link einfügen
const cssLinkTag = `<link rel="stylesheet" href="/${cssFiles[0]}">`

fs.readdirSync(hdocsDir)
  .filter(file => file.endsWith('.html'))
  .forEach(file => {
    const filePath = path.join(hdocsDir, file)
    let html = fs.readFileSync(filePath, 'utf-8')

    if (html.includes(cssFiles[0])) {
      console.log(`✔️  ${file} contains staysheet.`)
      return
    }

    html = html.replace(/<head[^>]*>/i, match => `${match}\n  ${cssLinkTag}`)
    fs.writeFileSync(filePath, html, 'utf-8')
    console.log(`✅ CSS in ${file} included.`)
  })
