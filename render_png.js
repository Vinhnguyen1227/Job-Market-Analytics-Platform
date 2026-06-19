const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

const files = fs.readdirSync(__dirname).filter(f => f.match(/chapter_\d+_thesis_2\.md$/));

if (!fs.existsSync('thesis_2_images')) {
    fs.mkdirSync('thesis_2_images', { recursive: true });
}

files.forEach(file => {
    const content = fs.readFileSync(file, 'utf8');
    const regex = /```mermaid\n([\s\S]*?)```/g;
    let match;
    let counter = 1;
    while ((match = regex.exec(content)) !== null) {
        const diagramContent = match[1];
        const chapterName = file.replace('.md', '');
        const tempName = `${chapterName}_diagram_${counter}.mmd`;
        const outName = `thesis_2_images/${chapterName}_diagram_${counter}.png`;
        
        fs.writeFileSync(tempName, diagramContent);
        console.log(`Rendering ${tempName} to ${outName}...`);
        try {
            execSync(`npx -y @mermaid-js/mermaid-cli -i ${tempName} -o ${outName} -s 4 -p puppeteer-config.json`, { stdio: 'inherit' });
        } catch (e) {
            console.error(`Failed to render ${tempName}`);
            try {
                execSync(`npx -y @mermaid-js/mermaid-cli -i ${tempName} -o ${outName} -s 4 -p puppeteer-config.json`, { stdio: 'inherit' });
            } catch (e2) {
                console.error('Failed again:', e2.message);
            }
        }
        // cleanup temp
        if (fs.existsSync(tempName)) fs.unlinkSync(tempName);
        counter++;
    }
});
