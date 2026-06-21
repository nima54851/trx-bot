// ======================================
// TRX Energy Bot — 前端交互逻辑
// ======================================

// API 在 GitHub Pages 上不可用，使用演示模式
const DEMO_MODE = window.location.hostname === 'nima54851.github.io';
const API_BASE = window.location.origin;
let selectedEnergy = 50000;
let selectedDays = 1;
const PRICE_PER_DAY = 0.5; // TRX per 1000 energy per day

// ─── 分区切换 ───────────────────────────
function showSection(name) {
    document.querySelectorAll('.main').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));

    const section = document.getElementById(`section-${name}`);
    if (section) {
        section.classList.remove('hidden');
        event?.target?.classList?.add('active');
    }

    if (name === 'pricing') loadPricingTable();
    return false;
}

// ─── 能量选择 ───────────────────────────
function selectEnergy(btn) {
    document.querySelectorAll('.energy-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    selectedEnergy = parseInt(btn.dataset.energy);
    document.getElementById('custom-energy').value = '';
    updatePreview();
}

function onCustomEnergy(input) {
    const val = parseInt(input.value);
    if (val >= 5000 && val <= 500000) {
        selectedEnergy = val;
        document.querySelectorAll('.energy-btn').forEach(b => b.classList.remove('selected'));
        updatePreview();
    }
}

// ─── 天数选择 ───────────────────────────
function selectDays(btn) {
    document.querySelectorAll('.day-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    selectedDays = parseInt(btn.dataset.days);
    updatePreview();
}

// ─── 价格预览 ───────────────────────────
function updatePreview() {
    const total = (selectedEnergy * selectedDays * PRICE_PER_DAY / 1000).toFixed(4);
    document.getElementById('preview-energy').textContent = selectedEnergy.toLocaleString();
    document.getElementById('preview-days').textContent = `${selectedDays} 天`;
    document.getElementById('preview-total').textContent = `${total} TRX`;
}

// ─── 创建订单 ───────────────────────────
async function createOrder() {
    const address = document.getElementById('trx-address').value.trim();

    // 简单验证
    if (!address || address.length !== 34 || !address.startsWith('T')) {
        alert('请输入有效的 TRON 主网地址（34位，以T开头）');
        return;
    }

    const btn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnLoading = document.getElementById('btn-loading');

    btn.disabled = true;
    btnText.classList.add('hidden');
    btnLoading.classList.remove('hidden');

    try {
        // 演示模式：直接显示结果
        const demoData = {
          order_id: 'LE' + Date.now(),
          deposit_address: 'TN3W4H6rK2ce4vX9YnFQHwKENnHjoxb3m9',
          trx_amount: selectedEnergy * selectedDays * 0.5 / 1000,
          status: 'pending'
        };
        showOrderStatus(demoData); return; // skip real API
      } /* else { const resp = await fetch(`${API_BASE}/api/orders/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: 0, // 匿名下单
                trx_address: address,
                energy_amount: selectedEnergy,
                rent_days: selectedDays,
                username: null
            })
        });

        const data = await resp.json();

        if (resp.ok) {
            showOrderStatus(data);
        } else {
            alert(`创建订单失败：${data.detail || resp.statusText}`);
        }
    } catch (e) {
        alert('网络错误，请稍后再试');
        console.error(e);
    } finally {
        btn.disabled = false;
        btnText.classList.remove('hidden');
        btnLoading.classList.add('hidden');
    }
}

// ─── 展示订单状态 ───────────────────────────
function showOrderStatus(data) {
    const statusEl = document.getElementById('order-status');
    const statusBadge = document.getElementById('os-status');

    document.getElementById('os-order-id').textContent = data.order_id;
    document.getElementById('os-energy').textContent = selectedEnergy.toLocaleString();
    document.getElementById('os-days').textContent = `${selectedDays} 天`;
    document.getElementById('os-status').textContent = data.status;
    document.getElementById('pay-address').textContent = data.deposit_address;
    document.getElementById('pay-amount').textContent = data.trx_amount;

    statusEl.classList.remove('hidden');
    statusEl.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // 状态颜色
    statusBadge.className = 'status-badge ' + data.status;

    // 自动轮询检查
    startPolling(data.order_id);
}

// ─── 轮询检查订单状态 ───────────────────────────
let pollingTimer = null;
function startPolling(orderId) {
    if (pollingTimer) clearInterval(pollingTimer);
    pollingTimer = setInterval(async () => {
        await checkOrderById(orderId);
    }, 15000); // 每15秒检查一次
}

// ─── 检查订单 ───────────────────────────
async function checkOrderById(orderId) {
    try {
        const resp = await fetch(`${API_BASE}/api/orders/${orderId}`);
        if (resp.ok) {
            const data = await resp.json();
            const statusBadge = document.getElementById('os-status');
            statusBadge.textContent = data.status;
            statusBadge.className = 'status-badge ' + data.status;

            if (data.status === 'paid' || data.status === 'rented') {
                clearInterval(pollingTimer);
                document.getElementById('pay-section').innerHTML =
                    `<div style="color:var(--success);font-size:1.2rem;text-align:center;padding:20px;">
                        ✅ 支付已确认！能量正在处理中...
                    </div>`;
            }
        }
    } catch (e) { /* silent */ }
}

async function checkOrder() {
    const orderId = document.getElementById('os-order-id').textContent;
    if (orderId && orderId !== '-') {
        await checkOrderById(orderId);
    }
}

// ─── 价格表 ───────────────────────────
async function loadPricingTable() {
    const tbody = document.getElementById('pricing-tbody');
    if (tbody.children.length > 0) return;

    const energies = [5000, 10000, 50000, 100000, 200000, 500000];
    const days = [1, 3, 7, 15, 30];
    const unit = PRICE_PER_DAY;

    let html = '';
    for (const e of energies) {
        html += '<tr>';
        html += `<td><b>${e.toLocaleString()}</b></td>`;
        for (const d of days) {
            const price = (e * d * unit / 1000).toFixed(1);
            html += `<td>${price}</td>`;
        }
        html += '</tr>';
    }
    tbody.innerHTML = html;
}

// ─── 背景动画 ───────────────────────────
function initBg() {
    const canvas = document.getElementById('bg-canvas');
    const ctx = canvas.getContext('2d');
    let w, h, particles;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }

    function initParticles() {
        particles = Array.from({ length: 60 }, () => ({
            x: Math.random() * w,
            y: Math.random() * h,
            r: Math.random() * 1.5 + 0.5,
            vx: (Math.random() - 0.5) * 0.3,
            vy: (Math.random() - 0.5) * 0.3,
        }));
    }

    function draw() {
        ctx.clearRect(0, 0, w, h);
        for (const p of particles) {
            p.x += p.vx; p.y += p.vy;
            if (p.x < 0) p.x = w;
            if (p.x > w) p.x = 0;
            if (p.y < 0) p.y = h;
            if (p.y > h) p.y = 0;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(0,212,170,0.4)';
            ctx.fill();
        }
        requestAnimationFrame(draw);
    }

    resize();
    initParticles();
    draw();
    window.addEventListener('resize', () => { resize(); initParticles(); });
}

// ─── 初始化 ───────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    updatePreview();
    initBg();
    loadPricingTable();
});
