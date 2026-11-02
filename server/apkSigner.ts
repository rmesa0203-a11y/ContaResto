import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import JSZip from 'jszip';

const SUPABASE_URL = process.env.VITE_SUPABASE_URL || 'https://yohpvligtqppphjrmxeq.supabase.co';
const SUPABASE_ANON_KEY = process.env.VITE_SUPABASE_ANON_KEY || 'sb_publishable_couMOQUQA8PDOqHvY1XvnA_jG_3_E8W';

export async function packageAndSignApk(): Promise<string> {
  const projectRoot = process.cwd();
  const buildScript = path.join(projectRoot, 'server', 'buildApk.py');
  const publicApkPath = path.join(projectRoot, 'public', 'BistroConta-v2.0-Android.apk');

  if (fs.existsSync(buildScript)) {
    try {
      console.log('[Build Server] Forzando compilación web fresca con Vite...');
      execSync('npm run build', { stdio: 'inherit' });
      console.log('[packageAndSignApk] Running pristine APK builder (aapt + javac + dx + zipalign + apksigner)...');
      execSync(`python3 "${buildScript}"`, { stdio: 'inherit' });
      return publicApkPath;
    } catch (err: any) {
      console.error('[packageAndSignApk] Error running buildApk.py:', err?.message || err);
      if (fs.existsSync(publicApkPath)) {
        console.log('[packageAndSignApk] Falling back to verified signed APK in public.');
        return publicApkPath;
      }
      throw err;
    }
  }

  const distApkPath = path.join(process.cwd(), 'dist', 'BistroConta-v2.0-Android.apk');
  const keystorePath = path.join(process.cwd(), 'keystore', 'bistroconta.jks');
  const javaSrc = path.join(process.cwd(), 'server', 'android', 'MainActivity.java');
  const androidJar = '/usr/lib/android-sdk/platforms/android-23/android.jar';
  const dxBinary = '/usr/lib/android-sdk/build-tools/debian/dx';

  if (!fs.existsSync(publicApkPath)) {
    throw new Error('Base APK template not found in public/');
  }

  // 1. Compile native Android Activity to classes.dex if tools and source exist
  let compiledDexBuf: Buffer | null = null;
  const tempDexDir = `/tmp/bistro-dex-${Date.now()}`;
  try {
    if (fs.existsSync(javaSrc) && fs.existsSync(androidJar) && fs.existsSync(dxBinary)) {
      const binDir = path.join(tempDexDir, 'bin');
      fs.mkdirSync(binDir, { recursive: true });

      execSync(`javac -source 8 -target 8 -cp "${androidJar}" -d "${binDir}" "${javaSrc}"`);
      const dexOut = path.join(tempDexDir, 'classes.dex');
      execSync(`"${dxBinary}" --dex --output="${dexOut}" "${binDir}"`);

      if (fs.existsSync(dexOut)) {
        compiledDexBuf = fs.readFileSync(dexOut);
        console.log('[packageAndSignApk] Native classes.dex successfully compiled with local asset & universal CORS support');
      }
    }
  } catch (err: any) {
    console.warn('[packageAndSignApk] Java compilation notice:', err?.message || err);
  } finally {
    try { fs.rmSync(tempDexDir, { recursive: true, force: true }); } catch (_) {}
  }

  const baseApkBuf = fs.readFileSync(publicApkPath);
  const zip = await JSZip.loadAsync(baseApkBuf);

  // Remove old signatures
  Object.keys(zip.files).forEach((f) => {
    if (f.startsWith('META-INF/')) {
      zip.remove(f);
    }
  });

  // Inject updated classes.dex if compiled
  if (compiledDexBuf) {
    zip.file('classes.dex', compiledDexBuf);
  }

  // Inject latest dist files into assets/www
  const distDir = path.join(process.cwd(), 'dist');
  if (fs.existsSync(path.join(distDir, 'index.html'))) {
    let distHtml = fs.readFileSync(path.join(distDir, 'index.html'), 'utf8');

    // Pre-seed Supabase credentials in localStorage so APK connects immediately on first boot
    const supaScript = `
    <script>
      try {
        if (!localStorage.getItem('bistro_supabase_url')) {
          localStorage.setItem('bistro_supabase_url', ${JSON.stringify(SUPABASE_URL)});
        }
        if (!localStorage.getItem('bistro_supabase_anon_key')) {
          localStorage.setItem('bistro_supabase_anon_key', ${JSON.stringify(SUPABASE_ANON_KEY)});
        }
      } catch (e) {
        console.warn('Storage pre-seed error:', e);
      }
    </script>
    `;

    if (distHtml.includes('</head>')) {
      distHtml = distHtml.replace('</head>', `${supaScript}</head>`);
    } else {
      distHtml = supaScript + distHtml;
    }

    zip.file('assets/www/index.html', distHtml);
  }

  const distAssetsDir = path.join(distDir, 'assets');
  if (fs.existsSync(distAssetsDir)) {
    // Clear outdated assets
    Object.keys(zip.files).forEach((f) => {
      if (f.startsWith('assets/www/assets/')) {
        zip.remove(f);
      }
    });

    const assetFiles = fs.readdirSync(distAssetsDir);
    for (const file of assetFiles) {
      const data = fs.readFileSync(path.join(distAssetsDir, file));
      zip.file(`assets/www/assets/${file}`, data);
    }
  }

  // Inject PWA icons and manifest if present in dist
  ['manifest.json', 'icon.svg', 'apple-touch-icon.png', 'pwa-192x192.png', 'pwa-512x512.png'].forEach((fileName) => {
    const fPath = path.join(distDir, fileName);
    if (fs.existsSync(fPath)) {
      zip.file(`assets/www/${fileName}`, fs.readFileSync(fPath));
    }
  });

  const tempUnaligned = `/tmp/bistro-unaligned-${Date.now()}.apk`;
  const tempAligned = `/tmp/bistro-aligned-${Date.now()}.apk`;

  const unalignedBuf = await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' });
  fs.writeFileSync(tempUnaligned, unalignedBuf);

  try {
    // 1. Zipalign (4-byte alignment mandatory for Android)
    execSync(`zipalign -p -f 4 "${tempUnaligned}" "${tempAligned}"`);

    // 2. Apksigner (v1 + v2 + v3 full Android scheme signature)
    execSync(
      `apksigner sign --ks "${keystorePath}" --ks-key-alias bistroconta --ks-pass pass:bistroconta123 --key-pass pass:bistroconta123 --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true "${tempAligned}"`
    );

    // 3. Verify
    execSync(`apksigner verify "${tempAligned}"`);

    // Copy to destinations
    const finalBuffer = fs.readFileSync(tempAligned);
    fs.writeFileSync(publicApkPath, finalBuffer);
    fs.writeFileSync(distApkPath, finalBuffer);

    console.log('[packageAndSignApk] APK successfully packaged, aligned and signed (v1, v2, v3)');
    return publicApkPath;
  } finally {
    try { if (fs.existsSync(tempUnaligned)) fs.unlinkSync(tempUnaligned); } catch (_) {}
    try { if (fs.existsSync(tempAligned)) fs.unlinkSync(tempAligned); } catch (_) {}
  }
}
