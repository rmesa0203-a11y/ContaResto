const esbuild = require('esbuild');
const fs = require('fs');

const text = fs.readFileSync('apply_clean_deduction.cjs', 'utf8');
const start_block = text.indexOf('const block = `') + 'const block = `'.length;
const end_block = text.lastIndexOf('`;');
const block = text.slice(start_block, end_block);

// Let's test lines by lines or binary search where the error is
try {
  esbuild.transformSync("function wrap() {" + block + "}", { loader: "js" });
  console.log("SUCCESS!");
} catch (e) {
  console.error("Error:", e.message);
  // print exact location
  const lines = ("function wrap() {" + block + "}").split("\n");
  console.log("Lines count:", lines.length);
  for (let i = 0; i < lines.length; i++) {
    try {
      esbuild.transformSync("function wrap() {" + lines.slice(0, i + 1).join("\n") + "}", { loader: "js" });
    } catch (e2) {
      console.log(`Failed at line ${i + 1}: ${lines[i]}`);
      break;
    }
  }
}
