const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const MarkdownIt = require('markdown-it'); // Requires npm install
const googleTTS = require('google-tts-api'); // Requires npm install
const ffmpeg = require('fluent-ffmpeg'); // Requires npm install

const md = new MarkdownIt();
const PUBLIC_DIR = path.join(__dirname, '../../public');
if (!fs.existsSync(PUBLIC_DIR)) fs.mkdirSync(PUBLIC_DIR, { recursive: true });

// Puppeteer Config (Shared)
const IS_MAC = process.platform === 'darwin';
const PUPPETEER_OPTIONS = {
    executablePath: IS_MAC
        ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        : '/usr/bin/chromium-browser',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
};

// ==========================================
// 1. PDF DOCUMENT GENERATOR
// ==========================================
async function createPDF(markdownContent, filename) {
    const htmlContent = `
    <html>
        <head>
            <style>
                body { font-family: 'Helvetica', sans-serif; padding: 40px; line-height: 1.6; }
                h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }
                h2 { color: #555; margin-top: 30px; }
                code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
                pre { background: #f4f4f4; padding: 15px; overflow-x: auto; }
            </style>
        </head>
        <body>
            ${md.render(markdownContent)}
        </body>
    </html>`;

    const outputPath = path.join(PUBLIC_DIR, filename);
    let browser = null;

    try {
        browser = await puppeteer.launch(PUPPETEER_OPTIONS);
        const page = await browser.newPage();
        await page.setContent(htmlContent);
        await page.pdf({ path: outputPath, format: 'A4', printBackground: true });
        console.log(`📄 PDF Generado: ${outputPath}`);
        return filename; // Return relative path for URL
    } catch (error) {
        console.error("PDF Error:", error);
        throw error;
    } finally {
        if (browser) await browser.close();
    }
}

// ==========================================
// 2. VIDEO GENERATOR (Simple News Brief)
// ==========================================
async function createVideo(textScript, filename) {
    // 1. Generate Audio (TTS)
    // Google TTS API allows max 200 chars per request, need to chunk or use library's logic
    // The library handles splitting if validation is correct, but let's keep it short for V1
    const audioUrl = googleTTS.getAudioUrl(textScript, {
        lang: 'es',
        slow: false,
        host: 'https://translate.google.com',
    });

    const audioPath = path.join(PUBLIC_DIR, 'temp_audio.mp3');
    const videoPath = path.join(PUBLIC_DIR, filename);
    const bgImage = path.join(PUBLIC_DIR, 'img/video_bg.png'); // Need to ensure this exists

    // Download Audio
    const audioBuffer = await downloadFile(audioUrl);
    fs.writeFileSync(audioPath, audioBuffer);

    // Create a simple Background Image if not exists
    if (!fs.existsSync(bgImage)) {
        // Can't easily create image with fs, so we assume it exists OR use a color source in ffmpeg
    }

    // FFMPEG: Image + Audio = Video
    return new Promise((resolve, reject) => {
        ffmpeg()
            .input('color=c=black:s=1280x720')
            .inputOptions('-f lavfi')
            .input(audioPath)
            .outputOptions([
                '-c:v libx264',
                '-tune stillimage',
                '-c:a aac',
                '-b:a 192k',
                '-pix_fmt yuv420p',
                '-shortest'
            ])
            .save(videoPath)
            .on('end', () => {
                console.log(`🎬 Video Generado: ${videoPath}`);
                fs.unlinkSync(audioPath); // Cleanup
                resolve(filename);
            })
            .on('error', (err) => {
                console.error("FFMPEG Error:", err);
                reject(err);
            });
    });
}

// Helper
async function downloadFile(url) {
    const { default: axios } = await import('axios'); // Dynamic import if needed or regular require
    const response = await axios({
        method: 'GET',
        url: url,
        responseType: 'arraybuffer'
    });
    return response.data;
}

module.exports = { createPDF, createVideo };
