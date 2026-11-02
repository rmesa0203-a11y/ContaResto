#!/usr/bin/env python3
"""
BistroConta Android APK Packager & Signer (Official Android DevOps & Java Pipeline)

1. Automates complete artifact clean-up and fresh build:
   - Step A: Complete clean-up of previous dist/ directory and old APKs.
   - Step B: Enforced execution of 'npm run build' (compiles TypeScript & Vite).
             Fails fast if any compiler error occurs, preventing partial/corrupt APKs.
   - Step C: Clean asset injection from fresh dist/ into assets/www/ of base APK wrapper,
             stamping unique build_timestamp cache-busters for Android WebView.

2. Strict 4-byte zipalign and official Android signature:
   - Standard Java tooling (uber-apk-signer.jar / apksigner + zipalign).
   - Dual-scheme signing: v1 (JAR Signature Scheme) + v2 (APK Signature Scheme v2) + v3.
   - Zero manual binary parsing or handcrafted padding hacks.
   - Final strict verification (apksigner / uber-apk-signer --verify).
"""

import os
import sys
import shutil
import zipfile
import subprocess
import tempfile
import urllib.request
import re
from datetime import datetime, timezone

CWD = os.path.abspath(os.getcwd())
DIST_DIR = os.path.join(CWD, 'dist')
PUBLIC_DIR = os.path.join(CWD, 'public')
BIN_DIR = os.path.join(CWD, 'bin')
KEYSTORE_DIR = os.path.join(CWD, 'keystore')

BASE_TEMPLATE_APK = os.path.join(BIN_DIR, 'base-wrapper.apk')
UBER_APK_SIGNER_JAR = os.path.join(BIN_DIR, 'uber-apk-signer.jar')
KEYSTORE_JKS = os.path.join(KEYSTORE_DIR, 'bistroconta.jks')

DIST_APK = os.path.join(DIST_DIR, 'BistroConta-v2.0-Android.apk')
PUBLIC_APK = os.path.join(PUBLIC_DIR, 'BistroConta-v2.0-Android.apk')
PUBLIC_COMPAT_APK = os.path.join(PUBLIC_DIR, 'BistroConta_POS.apk')

UBER_DOWNLOAD_URL = "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar"

def log(msg):
    print(f"[buildApk] {msg}", flush=True)

def ensure_tools():
    """Ensure Java, uber-apk-signer.jar, and Android Keystore exist."""
    # 1. Ensure Java runtime
    java_bin = shutil.which('java')
    if not java_bin:
        for candidate in [
            '/usr/bin/java',
            '/usr/lib/jvm/java-17-openjdk-amd64/bin/java',
            '/usr/lib/jvm/default-java/bin/java'
        ]:
            if os.path.exists(candidate):
                java_bin = candidate
                os.environ['PATH'] = os.path.dirname(candidate) + ':' + os.environ.get('PATH', '')
                break

    if not java_bin:
        log("Java binary not found in PATH. Attempting automatic installation via apt...")
        try:
            subprocess.run(['apt-get', 'update', '-qq'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['apt-get', 'install', '-y', '--no-install-recommends', 'default-jre-headless'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            java_bin = shutil.which('java')
        except Exception as e:
            log(f"Notice: apt-get install failed ({e}).")

    if not java_bin:
        log("Error: Java binary is required for official Android APK packaging and signing.")
        sys.exit(1)

    os.makedirs(BIN_DIR, exist_ok=True)
    os.makedirs(KEYSTORE_DIR, exist_ok=True)

    # 2. Ensure uber-apk-signer.jar
    if not os.path.exists(UBER_APK_SIGNER_JAR):
        log("Downloading official uber-apk-signer.jar from GitHub...")
        try:
            urllib.request.urlretrieve(UBER_DOWNLOAD_URL, UBER_APK_SIGNER_JAR)
            log("uber-apk-signer.jar downloaded successfully.")
        except Exception as e:
            log(f"Warning downloading via urllib ({e}). Trying curl...")
            subprocess.run(['curl', '-L', '-s', '-o', UBER_APK_SIGNER_JAR, UBER_DOWNLOAD_URL], check=True)

    # 3. Ensure Android Keystore
    if not os.path.exists(KEYSTORE_JKS):
        log("Generating official Android 2048-bit RSA keystore (bistroconta.jks)...")
        keytool_bin = shutil.which('keytool') or 'keytool'
        try:
            cmd = [
                keytool_bin, '-genkeypair', '-v',
                '-keystore', KEYSTORE_JKS,
                '-alias', 'bistroconta',
                '-keyalg', 'RSA',
                '-keysize', '2048',
                '-validity', '10000',
                '-storepass', 'bistroconta',
                '-keypass', 'bistroconta',
                '-dname', 'CN=BistroConta, OU=BistroConta, O=BistroConta, L=Havana, ST=Havana, C=CU'
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            log("Android keystore created successfully.")
        except Exception as e:
            log(f"Notice generating keystore: {e}")

    # 4. Ensure base wrapper APK exists
    if not os.path.exists(BASE_TEMPLATE_APK):
        for candidate in [PUBLIC_APK, DIST_APK, PUBLIC_COMPAT_APK]:
            if os.path.exists(candidate):
                log(f"Preserving base Android wrapper template to {BASE_TEMPLATE_APK}...")
                shutil.copyfile(candidate, BASE_TEMPLATE_APK)
                break

    if not os.path.exists(BASE_TEMPLATE_APK):
        log("Error: Base APK wrapper template (base-wrapper.apk) not found.")
        sys.exit(1)

    return True

def clean_previous_artifacts():
    """
    Paso A: Limpieza total de artefactos previos:
    - Elimina la carpeta dist/ anterior para evitar mezclar archivos viejos.
    - Elimina los APKs previos en dist/ y public/.
    """
    log("Paso A: Limpieza total de artefactos previos...")

    # Backup base template before clearing
    if not os.path.exists(BASE_TEMPLATE_APK):
        for candidate in [PUBLIC_APK, DIST_APK, PUBLIC_COMPAT_APK]:
            if os.path.exists(candidate):
                shutil.copyfile(candidate, BASE_TEMPLATE_APK)
                break

    # Remove old dist/
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR, ignore_errors=True)
        log("Carpeta dist/ anterior eliminada.")

    # Remove old APKs in public/
    if os.path.exists(PUBLIC_DIR):
        for fname in os.listdir(PUBLIC_DIR):
            if fname.endswith('.apk'):
                try:
                    os.remove(os.path.join(PUBLIC_DIR, fname))
                    log(f"APK previo eliminado de public/: {fname}")
                except Exception as e:
                    log(f"Notice deleting {fname}: {e}")

    os.makedirs(DIST_DIR, exist_ok=True)
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    log("Directorios dist/ y public/ inicializados en limpio.")

def compile_fresh_frontend():
    """
    Paso B: Ejecución forzada de compilación Vite:
    - Ejecuta 'npm run build' capturando cualquier error de TypeScript o Vite.
    - Si la compilación falla, aborta inmediatamente sin generar un APK corrupto.
    """
    log("Paso B: Ejecutando compilación forzada de frontend (npm run build)...")
    res = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
    if res.returncode != 0:
        log("ERROR FATAL: La compilación del frontend (npm run build) falló.")
        print(res.stdout, file=sys.stderr)
        print(res.stderr, file=sys.stderr)
        log("Proceso abortado inmediatamente para evitar generar un APK corrupto.")
        sys.exit(1)

    dist_index = os.path.join(DIST_DIR, 'index.html')
    dist_assets = os.path.join(DIST_DIR, 'assets')
    if not os.path.exists(dist_index) or not os.path.exists(dist_assets):
        log("ERROR: dist/index.html o dist/assets/ no existen tras la compilación.")
        sys.exit(1)

    log("Compilación de frontend completada exitosamente.")

def sanitize_html_for_webview(html_content, build_timestamp):
    """
    Paso C: Inyección limpia de assets con Cache-Buster:
    1. Transforma rutas absolutas a relativas (./assets/...).
    2. Agrega query string ?v={build_timestamp} a scripts y estilos para invalidar la caché del WebView.
    3. Inyecta meta tags de build_timestamp y versión.
    4. Elimina atributos 'crossorigin' para prevenir bloqueos CORS locales en file:///.
    5. Inyecta guards de WebView Android y resolución de splash.
    """
    # Remove crossorigin
    html = re.sub(r'\s+crossorigin(?:="[^"]*"|(?=[\s>]))', '', html_content)

    # Ensure relative paths
    html = re.sub(r'(src|href)="(?:\.?/)+assets/', r'\1="./assets/', html)
    html = re.sub(r'(src|href)="(?:\.?/)+([^"]+\.(?:png|svg|ico|json))"', r'\1="./\2"', html)

    # Add cache-busting timestamp query parameter to JS and CSS links
    html = re.sub(r'(\./assets/[^"?]+\.(?:js|css))"', rf'\1?v={build_timestamp}"', html)

    meta_stamp = f"""
    <meta name="build-timestamp" content="{build_timestamp}">
    <meta name="app-version" content="2.0.{build_timestamp}">
    """

    webview_guard = f"""
    <!-- Android WebView Local Environment Bootstrap -->
    <script>
      window.__IS_ANDROID_APK__ = true;
      window.__BISTRO_BUILD_TIMESTAMP__ = "{build_timestamp}";
      window.__BISTRO_VERSION__ = "2.0.{build_timestamp}";
      if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {{
        try {{
          navigator.serviceWorker.register = function() {{
            return Promise.reject(new Error('ServiceWorker intentionally disabled in Android WebView APK shell.'));
          }};
        }} catch (_) {{}}
      }}
      try {{
        if (!localStorage.getItem('bistro_supabase_url')) {{
          localStorage.setItem('bistro_supabase_url', 'https://yohpvligtqppphjrmxeq.supabase.co');
        }}
        if (!localStorage.getItem('bistro_supabase_anon_key')) {{
          localStorage.setItem('bistro_supabase_anon_key', 'sb_publishable_couMOQUQA8PDOqHvY1XvnA_jG_3_E8W');
        }}
        if (!localStorage.getItem('bistro_tenant_id')) {{
          localStorage.setItem('bistro_tenant_id', 'biz-main');
        }}
      }} catch (_) {{}}
      window.addEventListener('load', function() {{
        setTimeout(function() {{
          var splash = document.getElementById('bistro-splash');
          var root = document.getElementById('root');
          if (splash && root && root.children.length > 1) {{
            splash.style.display = 'none';
          }}
        }}, 800);
      }});
      window.addEventListener('error', function(e) {{
        console.warn('[WebView Runtime Guard]', e.message);
        var splash = document.getElementById('bistro-splash');
        if (splash) {{
          splash.style.display = 'none';
        }}
      }});
    </script>
    """

    head_injection = f"{meta_stamp}\n{webview_guard}"
    if '</head>' in html:
        html = html.replace('</head>', f'{head_injection}\n</head>')
    else:
        html = head_injection + html

    return html

def inject_assets_to_unsigned_apk(unsigned_apk_path, build_timestamp):
    """
    Paso C: Inyección limpia de assets dentro de assets/www/ del APK base.
    """
    log(f"Paso C: Inyectando assets de dist/ en assets/www/ (Build Timestamp: {build_timestamp})...")

    dist_index = os.path.join(DIST_DIR, 'index.html')
    dist_assets = os.path.join(DIST_DIR, 'assets')

    with open(dist_index, 'r', encoding='utf-8') as f:
        raw_index_html = f.read()

    sanitized_html = sanitize_html_for_webview(raw_index_html, build_timestamp)

    with zipfile.ZipFile(BASE_TEMPLATE_APK, 'r') as src_zip, \
         zipfile.ZipFile(unsigned_apk_path, 'w', compression=zipfile.ZIP_DEFLATED) as dest_zip:

        # Copy base native files (AndroidManifest.xml, classes.dex, resources.arsc, res/...)
        # Omit old signatures and old assets/www
        for item in src_zip.infolist():
            name = item.filename
            if name.startswith('META-INF/') or name.startswith('assets/www/'):
                continue
            data = src_zip.read(name)
            # Critical for 4-byte zipalign: keep uncompressed files stored uncompressed
            if item.compress_type == zipfile.ZIP_STORED or name.endswith('.arsc') or name.endswith('.dex') or name.endswith('.png'):
                dest_zip.writestr(name, data, compress_type=zipfile.ZIP_STORED)
            else:
                dest_zip.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)

        # Write sanitized index.html with unique timestamp
        dest_zip.writestr('assets/www/index.html', sanitized_html.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)

        # Write timestamp verification file in assets/www/
        dest_zip.writestr('assets/www/build.json', f'{{"buildTimestamp":"{build_timestamp}","version":"2.0.{build_timestamp}"}}\n'.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)

        # Write all dist/assets
        asset_count = 0
        for root, _, fnames in os.walk(dist_assets):
            for fname in fnames:
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, DIST_DIR)
                with open(fpath, 'rb') as f:
                    dest_zip.writestr(f"assets/www/{rel}", f.read(), compress_type=zipfile.ZIP_DEFLATED)
                asset_count += 1
        log(f"Inyectados {asset_count} archivos compilados en assets/www/assets/")

        # Write PWA icons, manifest and extra root web assets
        for extra in ['manifest.json', 'icon.svg', 'apple-touch-icon.png', 'pwa-192x192.png', 'pwa-512x512.png', 'pwa-maskable-512x512.png']:
            extra_path = os.path.join(DIST_DIR, extra)
            if os.path.exists(extra_path):
                with open(extra_path, 'rb') as f:
                    dest_zip.writestr(f"assets/www/{extra}", f.read(), compress_type=zipfile.ZIP_DEFLATED)

def firmar_y_alinear(unsigned_apk_path, final_apk_path):
    """
    Paso D: Estandarización de zipalign (4 bytes) y firma Android oficial:
    - Sin cálculos binarios manuales de v2 ni paddings artesanales.
    - Utiliza uber-apk-signer.jar o apksigner oficial de Java con esquema dual v1 + v2 (+ v3).
    """
    log("Paso D: Zipalign estricto de 4 bytes y firmado oficial Android...")

    # 1. Herramienta principal oficial: uber-apk-signer (apksig integrado de Google Android SDK)
    if os.path.exists(UBER_APK_SIGNER_JAR):
        cmd = [
            'java', '-jar', UBER_APK_SIGNER_JAR,
            '--apks', unsigned_apk_path,
            '--ks', KEYSTORE_JKS,
            '--ksAlias', 'bistroconta',
            '--ksPass', 'bistroconta',
            '--ksKeyPass', 'bistroconta',
            '--allowResign',
            '--overwrite',
            '--verbose'
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            log(f"Error en uber-apk-signer: {res.stderr or res.stdout}")
            sys.exit(1)

        # uber-apk-signer with --overwrite signs and zipaligns in-place
        if not os.path.exists(unsigned_apk_path):
            log("Error: El archivo APK firmado no fue encontrado tras la ejecución.")
            sys.exit(1)

        shutil.copyfile(unsigned_apk_path, final_apk_path)
        log("Zipalign (4 bytes) y firmado dual (v1 + v2 + v3) completado exitosamente con uber-apk-signer.")
        return

    # 2. Alternativa con herramientas del SDK (zipalign + apksigner)
    zipalign_bin = shutil.which('zipalign')
    apksigner_bin = shutil.which('apksigner')

    if zipalign_bin and apksigner_bin:
        with tempfile.TemporaryDirectory() as tmp_align_dir:
            aligned_apk = os.path.join(tmp_align_dir, "aligned.apk")
            # zipalign -p -f 4
            cmd_align = [zipalign_bin, '-p', '-f', '4', unsigned_apk_path, aligned_apk]
            subprocess.run(cmd_align, check=True)

            # apksigner sign con esquema dual v1 + v2
            cmd_sign = [
                apksigner_bin, 'sign',
                '--ks', KEYSTORE_JKS,
                '--ks-pass', 'pass:bistroconta',
                '--ks-key-alias', 'bistroconta',
                '--v1-signing-enabled', 'true',
                '--v2-signing-enabled', 'true',
                '--out', final_apk_path,
                aligned_apk
            ]
            subprocess.run(cmd_sign, check=True)
            log("Zipalign y firmado dual (v1 + v2) completado con zipalign y apksigner del SDK.")
            return

    log("Error fatal: No se encontró herramienta oficial de firmado (uber-apk-signer.jar ni apksigner).")
    sys.exit(1)

def verificar_apk(apk_path):
    """
    Paso E: Verificación estricta de APK:
    Verifica que el APK final sea 100% válido y compatible con Android PackageParser
    antes de declarar éxito.
    """
    log("Paso E: Verificación estricta del APK final...")

    verified = False

    # 1. Verificación con uber-apk-signer
    if os.path.exists(UBER_APK_SIGNER_JAR):
        verify_cmd = [
            'java', '-jar', UBER_APK_SIGNER_JAR,
            '-y',
            '-a', apk_path,
            '--verbose'
        ]
        res = subprocess.run(verify_cmd, capture_output=True, text=True)
        if res.returncode == 0:
            verified = True
            log("Verificación uber-apk-signer CONFIRMADA:")
            for line in res.stdout.splitlines():
                if any(k in line.lower() for k in ['verified', 'zipalign', 'signature', 'subject', 'sha256']):
                    log(f"  {line.strip()}")
        else:
            log(f"Aviso en verificación uber-apk-signer: {res.stderr or res.stdout}")

    # 2. Verificación adicional con apksigner verify
    apksigner_bin = shutil.which('apksigner')
    if apksigner_bin:
        cmd = [apksigner_bin, 'verify', '--verbose', apk_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            verified = True
            log("Verificación apksigner CONFIRMADA:")
            for line in res.stdout.splitlines()[:10]:
                log(f"  {line.strip()}")
        else:
            log(f"Error en apksigner verify: {res.stderr or res.stdout}")
            sys.exit(1)

    if not verified:
        log("Error: La verificación de integridad y firma del APK no pudo ser confirmada.")
        sys.exit(1)

    apk_size = os.path.getsize(apk_path)
    log(f"APK verificado y listo para instalación inmediata en Android ({apk_size} bytes / {apk_size / (1024*1024):.2f} MB).")

def main():
    log("Iniciando pipeline DevOps de empaquetado y firmado Android...")
    ensure_tools()

    # Paso A: Limpieza total
    clean_previous_artifacts()

    # Paso B: Compilación forzada de frontend
    compile_fresh_frontend()

    # Timestamp único para el build
    build_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_unsigned_apk = os.path.join(tmpdir, "unsigned.apk")
        temp_final_apk = os.path.join(tmpdir, "final.apk")

        # Paso C: Inyección limpia de assets con cache-buster
        inject_assets_to_unsigned_apk(temp_unsigned_apk, build_timestamp)

        # Paso D: Zipalign 4 bytes y firmado oficial
        firmar_y_alinear(temp_unsigned_apk, temp_final_apk)

        # Copiar a destinos finales
        shutil.copyfile(temp_final_apk, DIST_APK)
        shutil.copyfile(temp_final_apk, PUBLIC_APK)
        shutil.copyfile(temp_final_apk, PUBLIC_COMPAT_APK)
        log(f"APK distribuido en: {DIST_APK}")
        log(f"APK distribuido en: {PUBLIC_APK}")
        log(f"APK distribuido en: {PUBLIC_COMPAT_APK}")

    # Paso E: Verificación final
    verificar_apk(DIST_APK)

    print("BUILD_APK_SUCCESS", flush=True)

if __name__ == '__main__':
    main()
