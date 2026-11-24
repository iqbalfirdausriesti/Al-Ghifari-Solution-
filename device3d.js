import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

function makeRoundedRectShape(w, h, r) {
  const s = new THREE.Shape();
  const hw = w / 2, hh = h / 2;
  const rad = Math.min(r, hw, hh);
  s.moveTo(-hw + rad, -hh);
  s.lineTo(hw - rad, -hh);
  s.quadraticCurveTo(hw, -hh, hw, -hh + rad);
  s.lineTo(hw, hh - rad);
  s.quadraticCurveTo(hw, hh, hw - rad, hh);
  s.lineTo(-hw + rad, hh);
  s.quadraticCurveTo(-hw, hh, -hw, hh - rad);
  s.lineTo(-hw, -hh + rad);
  s.quadraticCurveTo(-hw, -hh, -hw + rad, -hh);
  return s;
}

function makeExtrudedPlate(w, h, r, depth, bevel = 0.015, mat) {
  const shape = makeRoundedRectShape(w, h, r);
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: Math.max(0.002, depth - bevel * 2),
    bevelEnabled: bevel > 0,
    bevelThickness: bevel,
    bevelSize: bevel,
    bevelSegments: 4,
    curveSegments: 16
  });
  geo.center();
  return new THREE.Mesh(geo, mat);
}

function makeScreenTexture(p, mode) {
  const c1 = (p && p.col && p.col[0]) || '#1746d6';
  const c2 = (p && p.col && p.col[1]) || '#d8b46a';
  const brand = (p && p.b) || 'Gadget';
  const name = (p && p.n) || 'Flagship';
  const canvas = document.createElement('canvas');

  if (mode === 'laptop') {
    canvas.width = 1024;
    canvas.height = 640;
    const ctx = canvas.getContext('2d');
    const g = ctx.createLinearGradient(0, 0, 1024, 640);
    g.addColorStop(0, '#071128');
    g.addColorStop(0.5, c1);
    g.addColorStop(1, c2);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 1024, 640);

    // Abstract glowing waves
    for (let i = 0; i < 3; i++) {
      const rg = ctx.createRadialGradient(260 + i * 260, 220 + (i % 2) * 140, 20, 260 + i * 260, 220 + (i % 2) * 140, 320);
      rg.addColorStop(0, i === 1 ? 'rgba(216,180,106,0.45)' : 'rgba(255,255,255,0.22)');
      rg.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = rg;
      ctx.fillRect(0, 0, 1024, 640);
    }

    // Top bar & brand card
    ctx.fillStyle = 'rgba(10,16,32,0.45)';
    ctx.fillRect(0, 0, 1024, 34);
    ctx.fillStyle = '#eaf0ff';
    ctx.font = '600 16px "Segoe UI", sans-serif';
    ctx.fillText(brand.toUpperCase(), 24, 22);
    ctx.textAlign = 'right';
    ctx.fillText('09:41  •  Wi-Fi  •  100%', 1000, 22);

    ctx.textAlign = 'center';
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    ctx.font = '800 44px "Segoe UI", sans-serif';
    ctx.fillText(name.length > 28 ? name.slice(0, 26) + '…' : name, 512, 310);
    ctx.fillStyle = '#d8b46a';
    ctx.font = '700 18px "Segoe UI", sans-serif';
    ctx.fillText('AL GHIFARI SOLUTION • GARANSI RESMI', 512, 355);

    // Dock bar bottom
    ctx.fillStyle = 'rgba(255,255,255,0.16)';
    ctx.beginPath();
    ctx.roundRect(312, 578, 400, 44, 16);
    ctx.fill();
  } else if (mode === 'watch') {
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#050812';
    ctx.fillRect(0, 0, 512, 512);
    const rings = [
      { r: 175, c: '#ff3b6b', a: 1.85 },
      { r: 132, c: '#a3e635', a: 1.55 },
      { r: 89, c: '#22d3ee', a: 1.35 }
    ];
    rings.forEach((rg) => {
      ctx.strokeStyle = 'rgba(255,255,255,0.12)';
      ctx.lineWidth = 22;
      ctx.beginPath();
      ctx.arc(256, 286, rg.r, 0, Math.PI * 2);
      ctx.stroke();
      ctx.strokeStyle = rg.c;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.arc(256, 286, rg.r, -Math.PI / 2, -Math.PI / 2 + Math.PI * rg.a);
      ctx.stroke();
    });
    ctx.fillStyle = '#ffffff';
    ctx.font = '800 52px "Segoe UI", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('09:41', 256, 86);
  } else {
    canvas.width = 512;
    canvas.height = 1024;
    const ctx = canvas.getContext('2d');
    const g = ctx.createLinearGradient(0, 0, 512, 1024);
    g.addColorStop(0, '#070f24');
    g.addColorStop(0.45, c1);
    g.addColorStop(1, c2);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 512, 1024);

    // Glowing highlights
    const rg1 = ctx.createRadialGradient(140, 280, 20, 140, 280, 340);
    rg1.addColorStop(0, 'rgba(255,255,255,0.34)');
    rg1.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = rg1;
    ctx.fillRect(0, 0, 512, 1024);

    const rg2 = ctx.createRadialGradient(380, 740, 20, 380, 740, 340);
    rg2.addColorStop(0, 'rgba(216,180,106,0.45)');
    rg2.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = rg2;
    ctx.fillRect(0, 0, 512, 1024);

    // Dynamic Island / Punch hole
    ctx.fillStyle = '#05070e';
    if (brand === 'Apple') {
      ctx.beginPath();
      ctx.roundRect(184, 24, 144, 38, 19);
      ctx.fill();
    } else {
      ctx.beginPath();
      ctx.arc(256, 36, 12, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.fillStyle = 'rgba(255,255,255,0.95)';
    ctx.textAlign = 'center';
    ctx.font = '800 108px "Segoe UI", sans-serif';
    ctx.fillText('09:41', 256, 225);

    ctx.font = '600 22px "Segoe UI", sans-serif';
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.fillText(brand.toUpperCase() + ' OFFICIAL', 256, 268);

    // Bottom glass pill
    ctx.fillStyle = 'rgba(10,16,32,0.52)';
    ctx.beginPath();
    ctx.roundRect(44, 835, 424, 118, 28);
    ctx.fill();
    ctx.strokeStyle = 'rgba(216,180,106,0.6)';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = '#ffffff';
    ctx.font = '700 24px "Segoe UI", sans-serif';
    ctx.fillText(name.length > 24 ? name.slice(0, 22) + '…' : name, 256, 888);
    ctx.fillStyle = '#d8b46a';
    ctx.font = '700 16px "Segoe UI", sans-serif';
    ctx.fillText('AL GHIFARI SOLUTION • 5G READY', 256, 922);

    // Home indicator
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.beginPath();
    ctx.roundRect(176, 988, 160, 8, 4);
    ctx.fill();
  }

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  return tex;
}

function makeBackTexture(p) {
  const c1 = (p && p.col && p.col[0]) || '#1a233a';
  const c2 = (p && p.col && p.col[1]) || '#4b78ff';
  const brand = (p && p.b) || '';
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 512, 1024);
  g.addColorStop(0, c1);
  g.addColorStop(0.65, c1);
  g.addColorStop(1, c2);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 512, 1024);

  // Subtle satin shimmer
  const rg = ctx.createLinearGradient(0, 0, 512, 512);
  rg.addColorStop(0, 'rgba(255,255,255,0.14)');
  rg.addColorStop(0.5, 'rgba(255,255,255,0)');
  rg.addColorStop(1, 'rgba(0,0,0,0.2)');
  ctx.fillStyle = rg;
  ctx.fillRect(0, 0, 512, 1024);

  ctx.fillStyle = 'rgba(255,255,255,0.68)';
  ctx.font = '800 34px "Segoe UI", sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(brand.toUpperCase(), 256, 670);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function makeTextPlateTexture(text, sub, bg = '#1e2430', fg = '#eaf0ff') {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, 512, 256);
  ctx.fillStyle = fg;
  ctx.textAlign = 'center';
  ctx.font = '800 54px "Segoe UI", sans-serif';
  ctx.fillText(text, 256, 128);
  if (sub) {
    ctx.fillStyle = '#d8b46a';
    ctx.font = '700 24px "Segoe UI", sans-serif';
    ctx.fillText(sub, 256, 178);
  }
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function addCameraLens(parent, x, y, z, r, ringMat, glassMat) {
  const g = new THREE.Group();
  g.position.set(x, y, z);

  const ring = new THREE.Mesh(
    new THREE.CylinderGeometry(r, r * 1.04, 0.036, 28),
    ringMat
  );
  ring.rotation.x = Math.PI / 2;
  g.add(ring);

  const darkRim = new THREE.Mesh(
    new THREE.CylinderGeometry(r * 0.78, r * 0.78, 0.04, 24),
    new THREE.MeshStandardMaterial({ color: 0x090b10, roughness: 0.25, metalness: 0.7 })
  );
  darkRim.rotation.x = Math.PI / 2;
  g.add(darkRim);

  const lens = new THREE.Mesh(
    new THREE.SphereGeometry(r * 0.56, 20, 14, 0, Math.PI * 2, 0, Math.PI * 0.45),
    glassMat
  );
  lens.rotation.x = Math.PI / 2;
  lens.position.z = -0.01;
  g.add(lens);

  parent.add(g);
}

function buildPhone(p) {
  const g = new THREE.Group();
  const c1 = new THREE.Color((p.col && p.col[0]) || '#2b3140');
  const c2 = new THREE.Color((p.col && p.col[1]) || '#8c92a0');
  const brand = (p.b || '').toLowerCase();
  const name = (p.n || '').toLowerCase();

  const frameMat = new THREE.MeshStandardMaterial({
    color: c2.clone().lerp(new THREE.Color('#c8cdd6'), 0.35),
    metalness: 0.88,
    roughness: 0.22
  });
  const backMat = new THREE.MeshPhysicalMaterial({
    map: makeBackTexture(p),
    metalness: 0.18,
    roughness: 0.38,
    clearcoat: 0.7,
    clearcoatRoughness: 0.2
  });
  const bezelMat = new THREE.MeshStandardMaterial({ color: 0x06080e, roughness: 0.25, metalness: 0.3 });
  const scrTex = makeScreenTexture(p, 'phone');
  const scrMat = new THREE.MeshPhysicalMaterial({
    map: scrTex,
    emissive: 0xffffff,
    emissiveMap: scrTex,
    emissiveIntensity: 0.65,
    roughness: 0.08,
    metalness: 0.05,
    clearcoat: 1.0,
    clearcoatRoughness: 0.05
  });
  const lensGlassMat = new THREE.MeshPhysicalMaterial({
    color: 0x0c1b3a,
    metalness: 0.2,
    roughness: 0.05,
    clearcoat: 1.0,
    reflectivity: 1.0
  });
  const ringMat = new THREE.MeshStandardMaterial({
    color: frameMat.color,
    metalness: 0.92,
    roughness: 0.18
  });

  // Main titanium/aluminium frame
  const body = makeExtrudedPlate(0.92, 1.92, 0.13, 0.095, 0.018, frameMat);
  g.add(body);

  // Front glass bezel + glowing OLED screen
  const bezel = makeExtrudedPlate(0.87, 1.87, 0.11, 0.01, 0.003, bezelMat);
  bezel.position.z = 0.048;
  g.add(bezel);

  const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.82, 1.80), scrMat);
  scr.position.z = 0.0545;
  g.add(scr);

  // Back glass panel
  const backPanel = new THREE.Mesh(
    new THREE.ExtrudeGeometry(makeRoundedRectShape(0.86, 1.86, 0.11), { depth: 0.008, bevelEnabled: false }),
    backMat
  );
  backPanel.geometry.center();
  backPanel.rotation.y = Math.PI;
  backPanel.position.z = -0.047;
  g.add(backPanel);

  // Side buttons
  const powerBtn = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.17, 0.025), frameMat);
  powerBtn.position.set(0.468, 0.18, 0);
  g.add(powerBtn);

  const volUp = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.13, 0.024), frameMat);
  volUp.position.set(-0.468, 0.32, 0);
  g.add(volUp);

  const volDn = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.13, 0.024), frameMat);
  volDn.position.set(-0.468, 0.14, 0);
  g.add(volDn);

  // Bottom USB-C port & speaker holes
  const portDark = new THREE.MeshStandardMaterial({ color: 0x050609, roughness: 0.6 });
  const usbc = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.01, 0.036), portDark);
  usbc.position.set(0, -0.96, 0);
  g.add(usbc);
  for (let s = -2; s <= 2; s++) {
    if (s === 0) continue;
    const hole = new THREE.Mesh(new THREE.CylinderGeometry(0.01, 0.01, 0.01, 10), portDark);
    hole.position.set(s * 0.08 + (s > 0 ? 0.06 : -0.06), -0.96, 0);
    g.add(hole);
  }

  // Brand-specific 3D rear camera module
  const camGroup = new THREE.Group();
  if (brand === 'apple') {
    const islandMat = new THREE.MeshPhysicalMaterial({
      color: c1,
      metalness: 0.25,
      roughness: 0.25,
      clearcoat: 0.9
    });
    const island = makeExtrudedPlate(0.38, 0.39, 0.08, 0.026, 0.008, islandMat);
    island.position.set(0.19, 0.65, -0.058);
    camGroup.add(island);
    const isPro = name.includes('pro') || name.includes('16') || name.includes('15');
    if (isPro) {
      addCameraLens(camGroup, 0.27, 0.74, -0.068, 0.072, ringMat, lensGlassMat);
      addCameraLens(camGroup, 0.27, 0.56, -0.068, 0.072, ringMat, lensGlassMat);
      addCameraLens(camGroup, 0.10, 0.65, -0.068, 0.072, ringMat, lensGlassMat);
    } else {
      addCameraLens(camGroup, 0.24, 0.74, -0.068, 0.072, ringMat, lensGlassMat);
      addCameraLens(camGroup, 0.24, 0.56, -0.068, 0.072, ringMat, lensGlassMat);
    }
    const flash = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.026, 0.02, 16), new THREE.MeshStandardMaterial({ color: 0xfef3c7, emissive: 0xfde68a, emissiveIntensity: 0.25 }));
    flash.rotation.x = Math.PI / 2;
    flash.position.set(0.10, 0.76, -0.068);
    camGroup.add(flash);
  } else if (brand === 'samsung') {
    addCameraLens(camGroup, 0.26, 0.76, -0.056, 0.068, ringMat, lensGlassMat);
    addCameraLens(camGroup, 0.26, 0.59, -0.056, 0.068, ringMat, lensGlassMat);
    addCameraLens(camGroup, 0.26, 0.42, -0.056, 0.068, ringMat, lensGlassMat);
    const flash = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.015, 16), new THREE.MeshStandardMaterial({ color: 0xfef3c7 }));
    flash.rotation.x = Math.PI / 2;
    flash.position.set(0.14, 0.68, -0.052);
    camGroup.add(flash);
  } else if (brand === 'google') {
    const visor = makeExtrudedPlate(0.84, 0.21, 0.09, 0.036, 0.01, bezelMat);
    visor.position.set(0, 0.62, -0.062);
    camGroup.add(visor);
    addCameraLens(camGroup, 0.22, 0.62, -0.072, 0.055, ringMat, lensGlassMat);
    addCameraLens(camGroup, 0.06, 0.62, -0.072, 0.052, ringMat, lensGlassMat);
    addCameraLens(camGroup, -0.10, 0.62, -0.072, 0.048, ringMat, lensGlassMat);
  } else if (name.includes('find') || name.includes('x200') || name.includes('14t') || name.includes('14 pro') || name.includes('13 pro') || name.includes('12+') || name.includes('spark 30') || name.includes('reno') === false && (brand === 'vivo' || brand === 'realme' || brand === 'xiaomi')) {
    const circleIsland = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.255, 0.036, 36), bezelMat);
    circleIsland.rotation.x = Math.PI / 2;
    circleIsland.position.set(0, 0.58, -0.058);
    camGroup.add(circleIsland);
    const goldRing = new THREE.Mesh(new THREE.TorusGeometry(0.245, 0.012, 12, 40), new THREE.MeshStandardMaterial({ color: 0xd8b46a, metalness: 0.9, roughness: 0.2 }));
    goldRing.position.set(0, 0.58, -0.074);
    camGroup.add(goldRing);
    addCameraLens(camGroup, -0.09, 0.66, -0.068, 0.054, ringMat, lensGlassMat);
    addCameraLens(camGroup, 0.09, 0.66, -0.068, 0.054, ringMat, lensGlassMat);
    addCameraLens(camGroup, 0, 0.49, -0.068, 0.058, ringMat, lensGlassMat);
  } else {
    const pill = makeExtrudedPlate(0.26, 0.48, 0.11, 0.026, 0.008, bezelMat);
    pill.position.set(0.22, 0.62, -0.056);
    camGroup.add(pill);
    addCameraLens(camGroup, 0.22, 0.72, -0.066, 0.066, ringMat, lensGlassMat);
    addCameraLens(camGroup, 0.22, 0.53, -0.066, 0.066, ringMat, lensGlassMat);
  }

  g.add(camGroup);
  g.rotation.y = -0.35;
  return g;
}

function buildLaptop(p) {
  const g = new THREE.Group();
  const c1 = new THREE.Color((p.col && p.col[0]) || '#252b38');
  const c2 = new THREE.Color((p.col && p.col[1]) || '#4b78ff');
  const brand = (p.b || '').toLowerCase();
  const name = (p.n || '').toLowerCase();
  const isGaming = name.includes('rog') || name.includes('tuf') || name.includes('nitro') || name.includes('predator') || name.includes('omen') || name.includes('victus') || name.includes('legion') || name.includes('loq') || name.includes('raider') || name.includes('katana') || name.includes('cyborg') || name.includes('alienware') || name.includes('g15');

  const alumMat = new THREE.MeshStandardMaterial({ color: c1.clone().lerp(new THREE.Color('#6b7280'), 0.25), metalness: 0.78, roughness: 0.28 });
  const keyMat = new THREE.MeshStandardMaterial({ color: 0x161a24, roughness: 0.55, metalness: 0.15 });
  const backLightMat = new THREE.MeshStandardMaterial({
    color: isGaming ? c2 : 0xe2e8f0,
    emissive: isGaming ? c2 : 0x94a3b8,
    emissiveIntensity: isGaming ? 0.85 : 0.35
  });

  // Laptop Base
  const base = makeExtrudedPlate(2.16, 1.44, 0.06, 0.065, 0.014, alumMat);
  base.rotation.x = Math.PI / 2;
  base.position.set(0, -0.45, 0.18);
  g.add(base);

  // Backlight well + 3D Keyboard grid
  const keyWell = new THREE.Mesh(new THREE.PlaneGeometry(1.86, 0.72), backLightMat);
  keyWell.rotation.x = -Math.PI / 2;
  keyWell.position.set(0, -0.416, 0.02);
  g.add(keyWell);

  const keyGeo = new THREE.BoxGeometry(0.11, 0.015, 0.105);
  for (let r = 0; r < 5; r++) {
    for (let c = 0; c < 13; c++) {
      const k = new THREE.Mesh(keyGeo, keyMat);
      k.position.set(-0.82 + c * 0.136, -0.41, -0.25 + r * 0.13);
      g.add(k);
    }
  }

  // Trackpad
  const tpMat = new THREE.MeshPhysicalMaterial({ color: c1.clone().lerp(new THREE.Color('#9ca3af'), 0.2), metalness: 0.4, roughness: 0.2, clearcoat: 0.6 });
  const tp = new THREE.Mesh(new THREE.BoxGeometry(0.68, 0.008, 0.42), tpMat);
  tp.position.set(0, -0.415, 0.62);
  g.add(tp);

  // Side USB/HDMI ports
  const portDark = new THREE.MeshStandardMaterial({ color: 0x05070c, roughness: 0.6 });
  for (let i = 0; i < 3; i++) {
    const pt = new THREE.Mesh(new THREE.BoxGeometry(0.014, 0.022, 0.08), portDark);
    pt.position.set(-1.082, -0.45, -0.15 + i * 0.18);
    g.add(pt);
    const ptR = new THREE.Mesh(new THREE.BoxGeometry(0.014, 0.022, 0.08), portDark);
    ptR.position.set(1.082, -0.45, -0.15 + i * 0.18);
    g.add(ptR);
  }

  // Hinge bar
  const hinge = new THREE.Mesh(new THREE.CylinderGeometry(0.036, 0.036, 1.56, 20), new THREE.MeshStandardMaterial({ color: 0x111520, metalness: 0.8, roughness: 0.25 }));
  hinge.rotation.z = Math.PI / 2;
  hinge.position.set(0, -0.41, -0.51);
  g.add(hinge);

  // Hinged Lid group (opened ~110 deg)
  const lidGroup = new THREE.Group();
  lidGroup.position.set(0, -0.41, -0.51);
  lidGroup.rotation.x = -0.34; // tilted back cleanly

  const lid = makeExtrudedPlate(2.16, 1.38, 0.06, 0.042, 0.01, alumMat);
  lid.position.set(0, 0.70, 0);
  lidGroup.add(lid);

  const bezel = makeExtrudedPlate(2.08, 1.30, 0.03, 0.01, 0.002, new THREE.MeshStandardMaterial({ color: 0x080b12, roughness: 0.25 }));
  bezel.position.set(0, 0.70, 0.021);
  lidGroup.add(bezel);

  const scrTex = makeScreenTexture(p, 'laptop');
  const scr = new THREE.Mesh(
    new THREE.PlaneGeometry(1.98, 1.21),
    new THREE.MeshPhysicalMaterial({
      map: scrTex,
      emissive: 0xffffff,
      emissiveMap: scrTex,
      emissiveIntensity: 0.62,
      roughness: 0.09,
      clearcoat: 1.0
    })
  );
  scr.position.set(0, 0.70, 0.028);
  lidGroup.add(scr);

  // Back of lid brand badge
  const badgeTex = makeTextPlateTexture((p.b || 'LAPTOP').toUpperCase(), isGaming ? 'GAMING SERIES' : 'OFFICIAL', '#111625', '#d8b46a');
  const lidBadge = new THREE.Mesh(new THREE.PlaneGeometry(0.64, 0.32), new THREE.MeshStandardMaterial({ map: badgeTex, metalness: 0.5, roughness: 0.3 }));
  lidBadge.rotation.y = Math.PI;
  lidBadge.position.set(0, 0.74, -0.023);
  lidGroup.add(lidBadge);

  g.add(lidGroup);
  g.rotation.y = -0.42;
  g.scale.setScalar(0.84);
  return g;
}

function buildHeadphone(p) {
  const g = new THREE.Group();
  const c1 = new THREE.Color((p.col && p.col[0]) || '#1c202a');
  const c2 = new THREE.Color((p.col && p.col[1]) || '#d8b46a');
  const shellMat = new THREE.MeshPhysicalMaterial({ color: c1, roughness: 0.28, metalness: 0.35, clearcoat: 0.5 });
  const padMat = new THREE.MeshStandardMaterial({ color: 0x161920, roughness: 0.82, metalness: 0.05 });
  const accentMat = new THREE.MeshStandardMaterial({ color: c2, metalness: 0.85, roughness: 0.2 });

  // Headband arc
  const band = new THREE.Mesh(new THREE.TorusGeometry(0.68, 0.08, 18, 48, Math.PI * 1.12), shellMat);
  band.rotation.z = -Math.PI * 0.06;
  band.position.y = 0.16;
  g.add(band);

  const cushion = new THREE.Mesh(new THREE.TorusGeometry(0.64, 0.062, 16, 42, Math.PI * 0.8), padMat);
  cushion.rotation.z = Math.PI * 0.1;
  cushion.position.y = 0.16;
  g.add(cushion);

  [-1, 1].forEach((side) => {
    const cupGroup = new THREE.Group();
    cupGroup.position.set(side * 0.66, -0.26, 0);
    cupGroup.rotation.z = side * -0.14;

    const cup = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.33, 0.22, 32), shellMat);
    cup.rotation.z = Math.PI / 2;
    cup.position.x = side * 0.05;
    cupGroup.add(cup);

    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.28, 0.018, 12, 36), accentMat);
    ring.rotation.y = Math.PI / 2;
    ring.position.x = side * 0.162;
    cupGroup.add(ring);

    const pad = new THREE.Mesh(new THREE.TorusGeometry(0.28, 0.09, 16, 36), padMat);
    pad.rotation.y = Math.PI / 2;
    pad.position.x = side * -0.07;
    cupGroup.add(pad);

    g.add(cupGroup);
  });

  g.rotation.y = -0.45;
  return g;
}

function buildTwsCase(p) {
  const g = new THREE.Group();
  const c1 = new THREE.Color((p.col && p.col[0]) || '#f8fafc');
  const caseMat = new THREE.MeshPhysicalMaterial({ color: c1, roughness: 0.14, metalness: 0.05, clearcoat: 1.0, clearcoatRoughness: 0.06 });
  const body = makeExtrudedPlate(1.22, 0.96, 0.32, 0.44, 0.10, caseMat);
  g.add(body);

  // Lid seam
  const seam = new THREE.Mesh(new THREE.BoxGeometry(1.23, 0.016, 0.45), new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.4 }));
  seam.position.y = 0.18;
  g.add(seam);

  // LED green indicator
  const led = new THREE.Mesh(new THREE.SphereGeometry(0.026, 14, 14), new THREE.MeshStandardMaterial({ color: 0x22c55e, emissive: 0x22c55e, emissiveIntensity: 1.5 }));
  led.position.set(0, 0.02, 0.22);
  g.add(led);

  // Back metal hinge
  const hinge = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.08, 0.04), new THREE.MeshStandardMaterial({ color: 0xcbd5e1, metalness: 0.9, roughness: 0.18 }));
  hinge.position.set(0, 0.18, -0.215);
  g.add(hinge);

  g.rotation.y = -0.4;
  return g;
}

function buildMouse(p) {
  const g = new THREE.Group();
  const c1 = new THREE.Color((p.col && p.col[0]) || '#1a1e28');
  const c2 = new THREE.Color((p.col && p.col[1]) || '#00b4d8');
  const shellMat = new THREE.MeshPhysicalMaterial({ color: c1, roughness: 0.3, metalness: 0.2, clearcoat: 0.45 });

  // Sculpted shell
  const hull = new THREE.Mesh(new THREE.SphereGeometry(0.62, 32, 24), shellMat);
  hull.scale.set(0.84, 0.48, 1.48);
  hull.position.set(0, -0.05, 0);
  g.add(hull);

  // Scroll wheel
  const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.07, 24), new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.85, roughness: 0.25 }));
  wheel.rotation.z = Math.PI / 2;
  wheel.position.set(0, 0.19, 0.45);
  g.add(wheel);

  // Glowing DPI LED strip
  const led = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.02, 0.11), new THREE.MeshStandardMaterial({ color: c2, emissive: c2, emissiveIntensity: 1.2 }));
  led.position.set(0, 0.24, 0.25);
  g.add(led);

  // Side thumb buttons
  for (let i = 0; i < 2; i++) {
    const sb = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.055, 0.16), new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.3 }));
    sb.position.set(-0.50, -0.02, 0.05 + i * 0.22);
    g.add(sb);
  }

  g.rotation.set(0.32, -0.55, 0);
  return g;
}

function buildKeyboard(p) {
  const g = new THREE.Group();
  const c1 = new THREE.Color((p.col && p.col[0]) || '#334155');
  const boardMat = new THREE.MeshStandardMaterial({ color: c1, roughness: 0.35, metalness: 0.35 });
  const keyMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.5 });
  const isRound = (p.n || '').toLowerCase().includes('k380');

  const deck = makeExtrudedPlate(2.10, 0.84, 0.08, 0.07, 0.015, boardMat);
  deck.rotation.x = Math.PI / 2;
  g.add(deck);

  for (let r = 0; r < 5; r++) {
    for (let c = 0; c < 13; c++) {
      const kg = isRound ? new THREE.CylinderGeometry(0.052, 0.056, 0.025, 16) : new THREE.BoxGeometry(0.115, 0.025, 0.11);
      const km = new THREE.Mesh(kg, (r === 0 && c < 3) ? new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.4 }) : keyMat);
      km.position.set(-0.88 + c * 0.146, 0.045, -0.28 + r * 0.14);
      g.add(km);
    }
  }
  g.rotation.set(0.55, -0.35, 0);
  g.scale.setScalar(0.88);
  return g;
}

function buildWebcam(p) {
  const g = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0x11151f, roughness: 0.4, metalness: 0.25 });
  const camHead = makeExtrudedPlate(1.56, 0.46, 0.18, 0.36, 0.04, bodyMat);
  camHead.position.y = 0.26;
  g.add(camHead);

  // Ring & lens
  const glowRing = new THREE.Mesh(new THREE.TorusGeometry(0.19, 0.016, 12, 36), new THREE.MeshStandardMaterial({ color: 0xe2e8f0, emissive: 0x94a3b8, emissiveIntensity: 0.4 }));
  glowRing.position.set(0, 0.26, 0.185);
  g.add(glowRing);

  const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.05, 28), new THREE.MeshPhysicalMaterial({ color: 0x0a1c3f, clearcoat: 1.0, roughness: 0.06 }));
  lens.rotation.x = Math.PI / 2;
  lens.position.set(0, 0.26, 0.18);
  g.add(lens);

  // Stand clip
  const stand1 = new THREE.Mesh(new THREE.BoxGeometry(0.68, 0.42, 0.08), bodyMat);
  stand1.position.set(0, -0.14, 0.02);
  stand1.rotation.x = 0.32;
  g.add(stand1);
  const stand2 = new THREE.Mesh(new THREE.BoxGeometry(0.68, 0.08, 0.56), bodyMat);
  stand2.position.set(0, -0.36, -0.16);
  g.add(stand2);

  g.rotation.y = -0.38;
  return g;
}

function buildChargerOrPowerbank(p) {
  const g = new THREE.Group();
  const name = (p.n || '').toLowerCase();
  const c1 = new THREE.Color((p.col && p.col[0]) || '#1e2430');
  const c2 = new THREE.Color((p.col && p.col[1]) || '#64748b');

  if (name.includes('kabel')) {
    const plugMat = new THREE.MeshStandardMaterial({ color: 0xd1d5db, metalness: 0.8, roughness: 0.22 });
    const metalMat = new THREE.MeshStandardMaterial({ color: 0x9ca3af, metalness: 0.92, roughness: 0.16 });
    const cableMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.55 });
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(-0.6, -0.55, 0),
      new THREE.Vector3(-0.6, 0.2, 0.18),
      new THREE.Vector3(0, 0.55, -0.12),
      new THREE.Vector3(0.6, 0.2, 0.18),
      new THREE.Vector3(0.6, -0.55, 0)
    ]);
    const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, 40, 0.045, 16, false), cableMat);
    g.add(tube);
    [-0.6, 0.6].forEach((x) => {
      const head = makeExtrudedPlate(0.18, 0.34, 0.04, 0.11, 0.015, plugMat);
      head.position.set(x, -0.68, 0);
      g.add(head);
      const tip = new THREE.Mesh(new THREE.BoxGeometry(0.10, 0.14, 0.04), metalMat);
      tip.position.set(x, -0.90, 0);
      g.add(tip);
    });
    g.rotation.y = -0.35;
    return g;
  }

  if (name.includes('hub')) {
    const alu = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.86, roughness: 0.24 });
    const hub = makeExtrudedPlate(0.56, 1.56, 0.08, 0.16, 0.02, alu);
    g.add(hub);
    const portDark = new THREE.MeshStandardMaterial({ color: 0x05070c, roughness: 0.5 });
    for (let i = 0; i < 4; i++) {
      const pt = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.14, 0.06), portDark);
      pt.position.set(0.282, 0.42 - i * 0.28, 0);
      g.add(pt);
    }
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(0, 0.78, 0),
      new THREE.Vector3(0, 1.05, 0.1),
      new THREE.Vector3(0.32, 1.12, 0.16)
    ]);
    g.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 20, 0.032, 12, false), new THREE.MeshStandardMaterial({ color: 0x334155 })));
    g.rotation.y = -0.42;
    return g;
  }

  if (name.includes('power bank') || name.includes('maggo')) {
    const bodyMat = new THREE.MeshStandardMaterial({ color: c1, metalness: 0.45, roughness: 0.32 });
    const pb = makeExtrudedPlate(0.96, 1.52, 0.12, 0.26, 0.025, bodyMat);
    g.add(pb);
    const screenTex = makeTextPlateTexture('100%', 'FAST CHARGE', '#070c18', '#4ade80');
    const lcd = new THREE.Mesh(new THREE.PlaneGeometry(0.56, 0.28), new THREE.MeshStandardMaterial({ map: screenTex, emissive: 0xffffff, emissiveMap: screenTex, emissiveIntensity: 0.4 }));
    lcd.position.set(0, 0.42, 0.132);
    g.add(lcd);
    if (name.includes('maggo')) {
      const mag = new THREE.Mesh(new THREE.TorusGeometry(0.26, 0.022, 12, 36), new THREE.MeshStandardMaterial({ color: 0xd8b46a, metalness: 0.88, roughness: 0.2 }));
      mag.position.set(0, -0.15, -0.132);
      g.add(mag);
    }
    g.rotation.y = -0.45;
    return g;
  }

  // Charger GaN Wall Charger
  const watt = (p.n.match(/\d+W/) || ['67W'])[0];
  const ganMat = new THREE.MeshStandardMaterial({ color: c1, roughness: 0.32, metalness: 0.3 });
  const faceMat = new THREE.MeshStandardMaterial({ color: c2.clone().lerp(new THREE.Color('#cbd5e1'), 0.4), roughness: 0.25, metalness: 0.65 });
  const charger = makeExtrudedPlate(0.84, 0.96, 0.14, 0.72, 0.04, ganMat);
  g.add(charger);

  const frontFace = makeExtrudedPlate(0.76, 0.88, 0.11, 0.03, 0.008, faceMat);
  frontFace.position.z = 0.358;
  g.add(frontFace);

  // Port USB-C (blue tongue) & label
  const portDark = new THREE.MeshStandardMaterial({ color: 0x05070c });
  const tongue = new THREE.MeshStandardMaterial({ color: 0x3b82f6, emissive: 0x1d4ed8, emissiveIntensity: 0.35 });
  for (let i = 0; i < 2; i++) {
    const port = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.075, 0.02), portDark);
    port.position.set(0, -0.05 - i * 0.18, 0.372);
    g.add(port);
    const tg = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.02, 0.024), tongue);
    tg.position.set(0, -0.05 - i * 0.18, 0.373);
    g.add(tg);
  }

  const labelTex = makeTextPlateTexture(watt, (p.b || 'ANKER').toUpperCase(), '#1e293b', '#38bdf8');
  const lbl = new THREE.Mesh(new THREE.PlaneGeometry(0.56, 0.28), new THREE.MeshStandardMaterial({ map: labelTex, roughness: 0.3 }));
  lbl.position.set(0, 0.22, 0.376);
  g.add(lbl);

  // Metal AC pins at back
  const pinMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.95, roughness: 0.15 });
  [-0.19, 0.19].forEach((px) => {
    const pin = new THREE.Mesh(new THREE.CylinderGeometry(0.038, 0.038, 0.36, 16), pinMat);
    pin.rotation.x = Math.PI / 2;
    pin.position.set(px, 0, -0.52);
    g.add(pin);
  });

  g.rotation.set(0.18, -0.52, 0);
  return g;
}

function buildWatch(p) {
  const g = new THREE.Group();
  const c1 = new THREE.Color((p.col && p.col[0]) || '#1e293b');
  const caseMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.88, roughness: 0.2 });
  const strapMat = new THREE.MeshStandardMaterial({ color: c1, roughness: 0.72, metalness: 0.05 });

  const caseMesh = makeExtrudedPlate(0.86, 1.02, 0.22, 0.22, 0.04, caseMat);
  g.add(caseMesh);

  const scrTex = makeScreenTexture(p, 'watch');
  const scr = new THREE.Mesh(
    new THREE.PlaneGeometry(0.72, 0.88),
    new THREE.MeshPhysicalMaterial({ map: scrTex, emissive: 0xffffff, emissiveMap: scrTex, emissiveIntensity: 0.65, clearcoat: 1.0, roughness: 0.08 })
  );
  scr.position.z = 0.112;
  g.add(scr);

  // Digital crown
  const crown = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.08, 20), caseMat);
  crown.rotation.z = Math.PI / 2;
  crown.position.set(0.45, 0.15, 0);
  g.add(crown);

  // Straps
  [-1, 1].forEach((dir) => {
    const strap = makeExtrudedPlate(0.46, 0.65, 0.08, 0.07, 0.015, strapMat);
    strap.position.set(0, dir * 0.78, -0.02);
    strap.rotation.x = dir * 0.15;
    g.add(strap);
  });

  g.rotation.y = -0.35;
  return g;
}

export function buildDeviceMesh(p) {
  const name = (p && p.n ? p.n : '').toLowerCase();
  const type = p && p.t ? p.t : 'phone';
  let root;
  if (type === 'laptop') root = buildLaptop(p);
  else if (type === 'watch') root = buildWatch(p);
  else if (type === 'buds') {
    root = (name.includes('q30') || name.includes('space one') || name.includes('zone vibe') || name.includes('headset'))
      ? buildHeadphone(p)
      : buildTwsCase(p);
  } else if (type === 'mouse') {
    if (name.includes('keyboard') || name.includes('k380') || name.includes('mx keys')) root = buildKeyboard(p);
    else if (name.includes('webcam') || name.includes('c922')) root = buildWebcam(p);
    else root = buildMouse(p);
  } else if (type === 'plug') {
    root = buildChargerOrPowerbank(p);
  } else {
    root = buildPhone(p);
  }
  return root;
}

function disposeObject(obj) {
  if (!obj) return;
  obj.traverse((child) => {
    if (child.geometry) child.geometry.dispose();
    if (child.material) {
      const mats = Array.isArray(child.material) ? child.material : [child.material];
      mats.forEach((m) => {
        if (m.map) m.map.dispose();
        if (m.emissiveMap) m.emissiveMap.dispose();
        m.dispose();
      });
    }
  });
}

// ---------- Hero 3D Stage (Persistent single WebGLRenderer) ----------
const heroState = {
  renderer: null,
  scene: null,
  camera: null,
  controls: null,
  group: null,
  raf: null,
  visible: true,
  container: null,
  clock: new THREE.Clock(),
  pmrem: null
};

function heroLoop() {
  if (!heroState.renderer || !heroState.visible) {
    heroState.raf = null;
    return;
  }
  heroState.raf = requestAnimationFrame(heroLoop);
  const t = heroState.clock.getElapsedTime();
  if (heroState.group) {
    heroState.group.position.y = Math.sin(t * 1.8) * 0.05;
  }
  heroState.controls.update();
  heroState.renderer.render(heroState.scene, heroState.camera);
}

function initHero(container, product) {
  if (heroState.renderer) {
    setHeroProduct(product);
    return;
  }
  heroState.container = container;
  container.innerHTML = '';

  const w = Math.max(200, container.clientWidth || 280);
  const h = Math.max(200, container.clientHeight || 280);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(w, h);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.18;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

  const keyLight = new THREE.DirectionalLight(0xffffff, 1.5);
  keyLight.position.set(3, 5, 4);
  scene.add(keyLight);

  const rimBlue = new THREE.PointLight(0x4b78ff, 3.2, 8);
  rimBlue.position.set(-2.5, 1.2, -2);
  scene.add(rimBlue);

  const rimGold = new THREE.PointLight(0xd8b46a, 2.4, 8);
  rimGold.position.set(2.5, -1.0, -2);
  scene.add(rimGold);

  const camera = new THREE.PerspectiveCamera(36, w / h, 0.1, 30);
  camera.position.set(0.3, 0.25, 3.6);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.enableZoom = false;
  controls.enablePan = false;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 2.4;

  heroState.renderer = renderer;
  heroState.scene = scene;
  heroState.camera = camera;
  heroState.controls = controls;
  heroState.pmrem = pmrem;

  setHeroProduct(product);

  if ('IntersectionObserver' in window) {
    new IntersectionObserver((entries) => {
      heroState.visible = entries[0].isIntersecting;
      if (heroState.visible && !heroState.raf) heroLoop();
    }, { threshold: 0.05 }).observe(container);
  }
  window.addEventListener('resize', () => {
    if (!heroState.renderer || !heroState.container) return;
    const nw = Math.max(160, heroState.container.clientWidth || 260);
    const nh = Math.max(160, heroState.container.clientHeight || 260);
    heroState.camera.aspect = nw / nh;
    heroState.camera.updateProjectionMatrix();
    heroState.renderer.setSize(nw, nh);
  });

  heroLoop();
}

function setHeroProduct(product) {
  if (!heroState.scene) return;
  if (heroState.group) {
    heroState.scene.remove(heroState.group);
    disposeObject(heroState.group);
  }
  const mesh = buildDeviceMesh(product);
  heroState.group = mesh;
  heroState.scene.add(mesh);
  if (heroState.visible && !heroState.raf) heroLoop();
}

// ---------- Modal Studio 3D Viewer ----------
const modalState = {
  renderer: null,
  scene: null,
  camera: null,
  controls: null,
  group: null,
  raf: null,
  auto: true,
  pmrem: null,
  lights: {},
  container: null,
  onResize: null
};

function modalLoop() {
  if (!modalState.renderer) {
    modalState.raf = null;
    return;
  }
  modalState.raf = requestAnimationFrame(modalLoop);
  modalState.controls.update();
  modalState.renderer.render(modalState.scene, modalState.camera);
}

function mountModal(container, product) {
  unmountModal();
  if (!container) return;
  modalState.container = container;
  container.innerHTML = '';

  const w = Math.max(260, container.clientWidth || 480);
  const h = Math.max(240, container.clientHeight || 340);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(w, h);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.22;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

  const key = new THREE.DirectionalLight(0xffffff, 1.45);
  key.position.set(3, 5, 4);
  scene.add(key);

  const fill = new THREE.DirectionalLight(0xcbd5e1, 0.7);
  fill.position.set(-4, 2, 3);
  scene.add(fill);

  const rim1 = new THREE.PointLight(0x4b78ff, 3.6, 10);
  rim1.position.set(-2.6, 1.2, -2.5);
  scene.add(rim1);

  const rim2 = new THREE.PointLight(0xd8b46a, 2.8, 10);
  rim2.position.set(2.6, -1.0, -2.5);
  scene.add(rim2);

  const camera = new THREE.PerspectiveCamera(35, w / h, 0.1, 30);
  camera.position.set(0.35, 0.3, 3.5);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.07;
  controls.enablePan = false;
  controls.minDistance = 1.85;
  controls.maxDistance = 6.2;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 2.6;

  modalState.renderer = renderer;
  modalState.scene = scene;
  modalState.camera = camera;
  modalState.controls = controls;
  modalState.pmrem = pmrem;
  modalState.auto = true;
  modalState.lights = { key, fill, rim1, rim2 };

  const mesh = buildDeviceMesh(product);
  modalState.group = mesh;
  scene.add(mesh);

  setLighting('dark');

  modalState.onResize = () => {
    if (!modalState.renderer || !modalState.container) return;
    const nw = Math.max(240, modalState.container.clientWidth || 440);
    const nh = Math.max(220, modalState.container.clientHeight || 320);
    modalState.camera.aspect = nw / nh;
    modalState.camera.updateProjectionMatrix();
    modalState.renderer.setSize(nw, nh);
  };
  window.addEventListener('resize', modalState.onResize);

  modalLoop();
}

function setLighting(preset) {
  if (!modalState.scene || !modalState.container) return;
  const { key, fill, rim1, rim2 } = modalState.lights;
  const wrap = modalState.container.parentElement;
  if (preset === 'light') {
    if (wrap) wrap.style.background = 'radial-gradient(circle at 50% 42%, #ffffff 0%, #dce6f5 100%)';
    if (key) key.intensity = 1.65;
    if (fill) fill.intensity = 1.1;
    if (rim1) { rim1.color.setHex(0xffffff); rim1.intensity = 1.2; }
    if (rim2) { rim2.color.setHex(0x93c5fd); rim2.intensity = 1.2; }
  } else if (preset === 'gold') {
    if (wrap) wrap.style.background = 'radial-gradient(circle at 50% 45%, #2b2212 0%, #090d1a 100%)';
    if (key) key.intensity = 1.35;
    if (fill) fill.intensity = 0.65;
    if (rim1) { rim1.color.setHex(0xd8b46a); rim1.intensity = 5.0; }
    if (rim2) { rim2.color.setHex(0xff9f43); rim2.intensity = 3.8; }
  } else {
    if (wrap) wrap.style.background = 'radial-gradient(circle at 50% 45%, #192956 0%, #091022 100%)';
    if (key) key.intensity = 1.45;
    if (fill) fill.intensity = 0.7;
    if (rim1) { rim1.color.setHex(0x4b78ff); rim1.intensity = 3.8; }
    if (rim2) { rim2.color.setHex(0xd8b46a); rim2.intensity = 2.8; }
  }
}

function toggleAuto(force) {
  if (!modalState.controls) return false;
  modalState.auto = typeof force === 'boolean' ? force : !modalState.auto;
  modalState.controls.autoRotate = modalState.auto;
  return modalState.auto;
}

function resetView() {
  if (!modalState.camera || !modalState.controls) return;
  modalState.camera.position.set(0.35, 0.3, 3.5);
  modalState.controls.target.set(0, 0, 0);
  modalState.controls.update();
}

function zoom(dir) {
  if (!modalState.camera || !modalState.controls) return;
  const offset = modalState.camera.position.clone().sub(modalState.controls.target);
  const factor = dir > 0 ? 0.84 : 1.18;
  offset.multiplyScalar(factor);
  const len = offset.length();
  if (len >= modalState.controls.minDistance && len <= modalState.controls.maxDistance) {
    modalState.camera.position.copy(modalState.controls.target).add(offset);
    modalState.controls.update();
  }
}

function unmountModal() {
  if (modalState.raf) {
    cancelAnimationFrame(modalState.raf);
    modalState.raf = null;
  }
  if (modalState.onResize) {
    window.removeEventListener('resize', modalState.onResize);
    modalState.onResize = null;
  }
  if (modalState.group && modalState.scene) {
    modalState.scene.remove(modalState.group);
    disposeObject(modalState.group);
  }
  if (modalState.controls) modalState.controls.dispose();
  if (modalState.scene && modalState.scene.environment) modalState.scene.environment.dispose();
  if (modalState.pmrem) modalState.pmrem.dispose();
  if (modalState.renderer) {
    modalState.renderer.dispose();
    if (modalState.renderer.domElement && modalState.renderer.domElement.parentNode) {
      modalState.renderer.domElement.parentNode.removeChild(modalState.renderer.domElement);
    }
  }
  modalState.renderer = null;
  modalState.scene = null;
  modalState.camera = null;
  modalState.controls = null;
  modalState.group = null;
  modalState.container = null;
}

window.AGS3D = {
  initHero,
  setHeroProduct,
  mountModal,
  unmountModal,
  setLighting,
  toggleAuto,
  resetView,
  zoom
};

if (typeof window.__ags3dReady === 'function') {
  window.__ags3dReady();
}
