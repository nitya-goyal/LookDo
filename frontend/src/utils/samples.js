/**
 * Generates sample UI screenshot images as Blobs and data URLs
 * for immediate one-click testing of LookDo.
 */

export function createSampleImageBlob(type = 'software-portal') {
  const canvas = document.createElement('canvas');
  canvas.width = 1200;
  canvas.height = 750;
  const ctx = canvas.getContext('2d');

  if (type === 'software-portal') {
    // Background
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Header bar
    ctx.fillStyle = '#1e293b';
    ctx.fillRect(0, 0, canvas.width, 68);

    // App Logo
    ctx.fillStyle = '#38bdf8';
    ctx.font = 'bold 22px Inter, sans-serif';
    ctx.fillText('⚡ DevPortal', 40, 42);

    // Search bar (top 0.04 to 0.09)
    ctx.fillStyle = '#334155';
    ctx.roundRect(300, 16, 540, 36, 8);
    ctx.fill();
    ctx.fillStyle = '#94a3b8';
    ctx.font = '14px Inter, sans-serif';
    ctx.fillText('🔍 Search tools, packages, documentation...', 320, 39);

    // Top Right Settings Gear Icon (top 0.035 - 0.085, left 0.88 - 0.965)
    ctx.fillStyle = '#475569';
    ctx.roundRect(1070, 16, 80, 36, 8);
    ctx.fill();
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 13px Inter, sans-serif';
    ctx.fillText('⚙ Settings', 1080, 39);

    // Hero Section
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 36px Outfit, sans-serif';
    ctx.fillText('Next Generation Developer Suite', 100, 190);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '18px Inter, sans-serif';
    ctx.fillText('Build, test, and deploy applications faster with automated tooling.', 100, 230);

    // Download Button (top 0.46 - 0.55, left 0.35 - 0.65 -> approx y: 345, h: 68, x: 420, w: 360)
    const btnGrad = ctx.createLinearGradient(420, 345, 780, 413);
    btnGrad.addColorStop(0, '#2563eb');
    btnGrad.addColorStop(1, '#0284c7');
    ctx.fillStyle = btnGrad;
    ctx.roundRect(420, 345, 360, 68, 12);
    ctx.fill();

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 20px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('⬇ Download Now (v2.4.0)', 600, 387);
    ctx.textAlign = 'left';

    // Subtext
    ctx.fillStyle = '#64748b';
    ctx.font = '14px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Free & Open Source • macOS, Windows, Linux', 600, 445);
    ctx.textAlign = 'left';

    // Feature Cards
    const cards = [
      { x: 100, title: '⚡ Fast Performance', desc: 'Instant hot-reload and optimized execution.' },
      { x: 460, title: '🔒 Enterprise Security', desc: 'Built-in sandboxing and permission management.' },
      { x: 820, title: '🌐 Cloud Sync', desc: 'Seamlessly access workspace anywhere.' },
    ];

    cards.forEach((card) => {
      ctx.fillStyle = '#1e293b';
      ctx.roundRect(card.x, 520, 280, 160, 12);
      ctx.fill();
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.fillStyle = '#f8fafc';
      ctx.font = 'bold 16px Inter, sans-serif';
      ctx.fillText(card.title, card.x + 20, 560);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '14px Inter, sans-serif';
      ctx.fillText(card.desc, card.x + 20, 595);
    });

  } else {
    // Account / Settings page
    ctx.fillStyle = '#0b1120';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Sidebar
    ctx.fillStyle = '#111827';
    ctx.fillRect(0, 0, 260, canvas.height);

    ctx.fillStyle = '#38bdf8';
    ctx.font = 'bold 20px Inter, sans-serif';
    ctx.fillText('User Console', 30, 48);

    const menuItems = ['Overview', 'Security & Access', 'Billing', 'Integrations'];
    menuItems.forEach((item, idx) => {
      ctx.fillStyle = idx === 1 ? 'rgba(56, 189, 248, 0.15)' : 'transparent';
      ctx.roundRect(20, 90 + idx * 48, 220, 38, 8);
      ctx.fill();

      ctx.fillStyle = idx === 1 ? '#38bdf8' : '#94a3b8';
      ctx.font = idx === 1 ? 'bold 14px Inter, sans-serif' : '14px Inter, sans-serif';
      ctx.fillText(item, 40, 114 + idx * 48);
    });

    // Content Header
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 28px Outfit, sans-serif';
    ctx.fillText('Security Settings', 310, 60);

    // Panel
    ctx.fillStyle = '#1f2937';
    ctx.roundRect(310, 90, 840, 600, 14);
    ctx.fill();

    // Section 1: Password (around top 0.60)
    ctx.fillStyle = '#f3f4f6';
    ctx.font = 'bold 18px Inter, sans-serif';
    ctx.fillText('Password & Authentication', 350, 145);

    ctx.fillStyle = '#9ca3af';
    ctx.font = '14px Inter, sans-serif';
    ctx.fillText('Last modified 3 months ago. Regular password updates ensure account protection.', 350, 175);

    // Change Password link / button (y: ~450/750 = 0.60, x: 216/1200 = 0.18)
    ctx.fillStyle = '#1d4ed8';
    ctx.roundRect(350, 450, 260, 45, 8);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 14px Inter, sans-serif';
    ctx.fillText('🔑 Change Password Now', 380, 478);

    // Right side option (top 0.28, left 0.72)
    ctx.fillStyle = '#374151';
    ctx.roundRect(870, 210, 250, 60, 8);
    ctx.fill();
    ctx.fillStyle = '#60a5fa';
    ctx.font = 'bold 14px Inter, sans-serif';
    ctx.fillText('Two-Factor Authentication', 885, 245);
  }

  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      resolve(new File([blob], `${type}.png`, { type: 'image/png' }));
    }, 'image/png');
  });
}
