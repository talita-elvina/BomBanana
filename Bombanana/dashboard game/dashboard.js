
const BROKER_URL = "wss://broker.hivemq.com:8884/mqtt";

let client = null;
let projectId = "";

let lastSeen = { A: 0, B: 0 };
let lastOwner = null;
let lastGameStatus = "";
let lastEvent = "";

let countdownStarted = false;
let countdownActive = false;
let countdownRun = 0;

let explosionShown = false;
let gameStarted = false;

const $ = (id) => document.getElementById(id);


// ========================================
// STYLE POPUP DAN FONT TIMER
// ========================================
function setupCountdown() {
  if ($("countdownOverlay")) return;

  const style = document.createElement("style");

  style.textContent = `
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;800;900&display=swap');

    /* Popup countdown dan ledakan */
    #countdownOverlay,
    #explosionOverlay {
      position: fixed;
      inset: 0;
      z-index: 999999;
      display: none;
      align-items: center;
      justify-content: center;
      background: rgba(8, 24, 16, 0.48);
      backdrop-filter: blur(4px);
      padding: 20px;
      box-sizing: border-box;
    }

    #countdownOverlay.show,
    #explosionOverlay.show {
      display: flex !important;
    }

    /* Kartu countdown */
    .countdown-card,
    .explosion-card {
      width: min(90%, 460px);
      padding: 30px 22px;
      text-align: center;
      background: #f7df76;
      color: #173d2b;
      border: 5px solid #173d2b;
      border-radius: 24px;
      box-shadow: 0 10px 0 #0b2418;
      box-sizing: border-box;
      animation: screenPop 0.35s ease-out;
    }

    .countdown-title,
    .explosion-title {
      font-size: clamp(20px, 4vw, 30px);
      font-weight: 900;
      letter-spacing: 2px;
    }

    /* Area angka dan START dibuat tetap di tengah */
    .countdown-number-wrap {
      width: 100%;
      min-height: 160px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      margin: 15px 0;
      overflow: hidden;
    }

    .countdown-number {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      font-family: 'Orbitron', 'Arial Black', sans-serif;
      font-size: clamp(75px, 18vw, 135px);
      font-weight: 900;
      line-height: 1;
      letter-spacing: 0;
      white-space: nowrap;
      margin: 0;
      color: #173d2b;
      animation: screenPop 0.3s ease-out;
    }

    /* START! dibuat lebih kecil agar tidak turun baris */
    .countdown-number.start-text {
      font-family: 'Orbitron', 'Arial Black', sans-serif;
      font-size: clamp(38px, 10vw, 70px);
      letter-spacing: 1px;
      white-space: nowrap;
    }

    .countdown-subtitle,
    .explosion-subtitle {
      font-size: clamp(15px, 3vw, 22px);
      font-weight: 900;
      letter-spacing: 1px;
      text-align: center;
    }

    /* Popup ledakan */
    .explosion-emoji {
      font-size: clamp(85px, 20vw, 145px);
      line-height: 1.2;
      animation: boomEffect 0.4s ease-in-out infinite alternate;
    }

    .final-score {
      margin-top: 20px;
      font-family: 'Orbitron', 'Arial Black', sans-serif;
      font-size: clamp(22px, 5vw, 36px);
      font-weight: 900;
      line-height: 1.4;
    }

    /* Font timer permainan */
    #timeValue {
      font-family: 'Orbitron', 'Arial Black', sans-serif !important;
      font-size: clamp(32px, 5vw, 48px) !important;
      font-weight: 900 !important;
      font-variant-numeric: tabular-nums;
      font-feature-settings: "tnum";
      letter-spacing: 2px;
      line-height: 1.2;
      white-space: nowrap;
      text-shadow: 0 2px 0 rgba(0, 0, 0, 0.08);
    }

    #timeValue span {
      font-family: inherit;
      font-size: 0.38em;
      font-weight: 800;
      letter-spacing: 1px;
    }

    #scoreValue {
      font-family: 'Orbitron', 'Arial Black', sans-serif !important;
      font-weight: 900 !important;
      font-variant-numeric: tabular-nums;
    }

    @keyframes screenPop {
      from {
        transform: scale(0.7);
        opacity: 0;
      }

      to {
        transform: scale(1);
        opacity: 1;
      }
    }

    @keyframes boomEffect {
      from {
        transform: scale(0.85) rotate(-6deg);
      }

      to {
        transform: scale(1.1) rotate(6deg);
      }
    }
  `;

  document.head.appendChild(style);

  const countdown = document.createElement("div");
  countdown.id = "countdownOverlay";

  countdown.innerHTML = `
    <div class="countdown-card">
      <div class="countdown-title">🍌 BOM-BANANA 🍌</div>

      <div class="countdown-number-wrap">
        <div class="countdown-number" id="countdownNumber">3</div>
      </div>

      <div class="countdown-subtitle" id="countdownSubtitle">
        GET READY!
      </div>
    </div>
  `;

  const explosion = document.createElement("div");
  explosion.id = "explosionOverlay";

  explosion.innerHTML = `
    <div class="explosion-card">
      <div class="explosion-title">💣 BOM-BANANA 💣</div>
      <div class="explosion-emoji">💥</div>
      <div class="explosion-title">BOOM!</div>
      <div class="explosion-subtitle">WAKTU HABIS!</div>
      <div class="final-score" id="finalScore">
        SKOR AKHIR: 0
      </div>
    </div>
  `;

  document.body.append(countdown, explosion);
}


// ========================================
// RESET TAMPILAN
// ========================================
function resetSensorDisplay() {
  ["A", "B"].forEach((letter) => {
    const accel = $("miniAccel" + letter);
    const gyro = $("miniGyro" + letter);

    if (accel) accel.textContent = "0.0 m/s²";
    if (gyro) gyro.textContent = "0.0 rad/s";
  });

  if ($("scoreValue")) {
    $("scoreValue").textContent = "0";
  }

  if ($("timeValue")) {
    $("timeValue").innerHTML = '30<span> dtk</span>';
  }

  if ($("timeProgress")) {
    $("timeProgress").style.width = "100%";
  }

  if ($("holderName")) {
    $("holderName").textContent = "Menunggu START";
  }

  if ($("laneA")) $("laneA").classList.remove("active");
  if ($("laneB")) $("laneB").classList.remove("active");

  if ($("laneStateA")) $("laneStateA").textContent = "ONLINE";
  if ($("laneStateB")) $("laneStateB").textContent = "ONLINE";

  if ($("arenaMessage")) {
    $("arenaMessage").textContent =
      "Bersiap! Permainan akan segera dimulai.";
  }

  if ($("gameState")) {
    $("gameState").textContent = "BERSIAP";
  }

  if ($("roundNote")) {
    $("roundNote").textContent = "Bersiap memulai permainan";
  }

  if ($("flightZone")) {
    $("flightZone").dataset.holder = "";
  }

  lastOwner = null;
  lastEvent = "";
}


// ========================================
// COUNTDOWN POPUP
// ========================================
function cancelCountdown() {
  countdownRun++;
  countdownStarted = false;
  countdownActive = false;

  if ($("countdownOverlay")) {
    $("countdownOverlay").classList.remove("show");
  }
}


function startCountdown() {
  if (countdownStarted) return;

  setupCountdown();

  countdownStarted = true;
  countdownActive = true;

  const thisRun = ++countdownRun;

  const overlay = $("countdownOverlay");
  const number = $("countdownNumber");
  const subtitle = $("countdownSubtitle");

  const steps = [
    ["3", "GET READY!"],
    ["2", "GET READY!"],
    ["1", "ALMOST THERE!"],
    ["START!", "LET THE GAME BEGIN!"]
  ];

  overlay.classList.add("show");

  let index = 0;

  function showStep() {
    if (thisRun !== countdownRun) return;

    const currentText = steps[index][0];

    number.textContent = currentText;
    number.classList.toggle(
      "start-text",
      currentText === "START!"
    );

    subtitle.textContent = steps[index][1];

    number.style.animation = "none";
    void number.offsetWidth;
    number.style.animation = "screenPop 0.3s ease-out";

    if (index < steps.length - 1) {
      index++;
      setTimeout(showStep, 800);
    } else {
      // START! tetap di tengah selama 700 ms,
      // lalu popup hilang otomatis.
      setTimeout(() => {
        if (thisRun !== countdownRun) return;

        overlay.classList.remove("show");
        countdownActive = false;
        countdownStarted = false;

        if ($("arenaMessage")) {
          $("arenaMessage").textContent =
            "Game dimulai! Guncang HP pemegang bom untuk mengoper.";
        }
      }, 700);
    }
  }

  showStep();
}


// ========================================
// POPUP LEDAKAN
// ========================================
function showExplosion(score) {
  setupCountdown();

  if (explosionShown || !gameStarted) return;

  explosionShown = true;
  gameStarted = false;

  cancelCountdown();

  $("countdownOverlay").classList.remove("show");

  $("finalScore").textContent = "SKOR AKHIR: " + score;
  $("explosionOverlay").classList.add("show");

  if ($("arenaMessage")) {
    $("arenaMessage").textContent = "💥 BOOM! Waktu habis!";
  }

  if ($("gameState")) {
    $("gameState").textContent = "SELESAI";
  }

  if ($("holderName")) {
    $("holderName").textContent = "Permainan selesai";
  }

  addLog("💥 BOOM! Permainan selesai. Skor akhir: " + score);

  setTimeout(() => {
    $("explosionOverlay").classList.remove("show");
  }, 3000);
}


// ========================================
// RIWAYAT AKTIVITAS
// ========================================
function addLog(message) {
  const list = $("activityList");

  if (!list || !message) return;

  const empty = list.querySelector(".empty-state");

  if (empty) empty.remove();

  const item = document.createElement("div");
  item.className = "activity-item";

  const time = document.createElement("div");
  time.className = "activity-time";

  time.textContent = new Date().toLocaleTimeString("id-ID", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });

  const text = document.createElement("div");
  text.className = "activity-message";
  text.textContent = message;

  item.append(time, text);
  list.prepend(item);

  while (list.children.length > 25) {
    list.lastElementChild.remove();
  }
}


// ========================================
// STATUS KONEKSI
// ========================================
function setConnection(state, label) {
  if ($("connectionDot")) {
    $("connectionDot").className = state;
  }

  if ($("connectionLabel")) {
    $("connectionLabel").textContent = label;
  }

  if ($("cloudState")) {
    $("cloudState").textContent =
      state === "connected"
        ? "Online"
        : state === "error"
        ? "Error"
        : "Menghubungkan";
  }

  if ($("connectButton")) {
    $("connectButton").innerHTML =
      state === "connected"
        ? "TERHUBUNG ✓"
        : 'SAMBUNGKAN <span>↗</span>';
  }
}


// ========================================
// DATA SENSOR
// ========================================
function magnitude(x, y, z) {
  return Math.sqrt(
    (Number(x) || 0) ** 2 +
    (Number(y) || 0) ** 2 +
    (Number(z) || 0) ** 2
  );
}


function showDevice(letter, payload) {
  lastSeen[letter] = Date.now();

  const state = $("miniState" + letter);
  const accelValue = $("miniAccel" + letter);
  const gyroValue = $("miniGyro" + letter);
  const laneState = $("laneState" + letter);

  if (state) {
    state.textContent = "● HP online";
  }

  if (!countdownActive) {
    const accel = magnitude(payload.ax, payload.ay, payload.az);
    const gyro = magnitude(payload.gx, payload.gy, payload.gz);

    if (accelValue) {
      accelValue.textContent = accel.toFixed(1) + " m/s²";
    }

    if (gyroValue) {
      gyroValue.textContent = gyro.toFixed(1) + " rad/s";
    }
  }

  if (laneState) {
    if (countdownActive) {
      laneState.textContent = "ONLINE";
    } else if ($("flightZone")?.dataset.holder === letter) {
      laneState.textContent = "💣 MEMEGANG";
    } else {
      laneState.textContent = "SIAP MENERIMA";
    }
  }

  if ($("deviceCount")) {
    $("deviceCount").textContent =
      ["A", "B"].filter(
        (x) => lastSeen[x] && Date.now() - lastSeen[x] < 7000
      ).length + " / 2";
  }
}


// ========================================
// STATUS PERMAINAN
// ========================================
function showGameStatus(s) {
  const status = s.status || "";
  const previousStatus = lastGameStatus;
  const score = Number(s.score);
  const time = Number(s.time_left);

  if (
    status === "COUNTDOWN" &&
    previousStatus !== "COUNTDOWN"
  ) {
    cancelCountdown();

    $("explosionOverlay")?.classList.remove("show");

    explosionShown = false;
    gameStarted = true;

    resetSensorDisplay();
    startCountdown();

    addLog("Countdown permainan dimulai.");
  }

  if (status === "PLAYING") {
    gameStarted = true;
  }

  if (status === "FINISHED" && gameStarted) {
    showExplosion(Number.isFinite(score) ? score : 0);
  }

  if (
    status === "MENUNGGU" &&
    previousStatus === "FINISHED"
  ) {
    cancelCountdown();

    $("explosionOverlay")?.classList.remove("show");

    explosionShown = false;
    gameStarted = false;

    resetSensorDisplay();

    if ($("gameState")) {
      $("gameState").textContent = "MENUNGGU";
    }

    if ($("holderName")) {
      $("holderName").textContent = "Belum diketahui";
    }

    if ($("arenaMessage")) {
      $("arenaMessage").textContent =
        "Menunggu kedua HP untuk memulai permainan.";
    }

    lastOwner = null;
    lastEvent = "";
  }

  lastGameStatus = status;

  if ($("scoreValue") && Number.isFinite(score)) {
    $("scoreValue").textContent =
      countdownActive ? "0" : score;
  }

  if ($("timeValue") && Number.isFinite(time)) {
    $("timeValue").innerHTML =
      Math.max(0, time) + "<span> dtk</span>";

    if ($("timeProgress")) {
      $("timeProgress").style.width =
        Math.max(0, Math.min(100, (time / 30) * 100)) + "%";
    }

    if ($("roundNote")) {
      $("roundNote").textContent =
        status === "COUNTDOWN"
          ? "Bersiap memulai permainan"
          : status === "FINISHED"
          ? "Waktu permainan habis"
          : status === "PLAYING"
          ? "Permainan sedang berjalan"
          : "Menunggu permainan";
    }
  }

  const owner = s.owner || s.holder;

  if (owner === "A" || owner === "B") {
    if ($("flightZone")) {
      $("flightZone").dataset.holder = owner;
    }

    if (!countdownActive && status === "PLAYING") {
      $("holderName").textContent = "Player " + owner;

      $("laneA").classList.toggle("active", owner === "A");
      $("laneB").classList.toggle("active", owner === "B");

      $("laneStateA").textContent =
        owner === "A" ? "💣 MEMEGANG" : "SIAP MENERIMA";

      $("laneStateB").textContent =
        owner === "B" ? "💣 MEMEGANG" : "SIAP MENERIMA";

      $("arenaMessage").textContent =
        "Bom sedang di Player " + owner +
        " — guncang HP itu untuk mengoper!";
    }

    if (
      lastOwner &&
      lastOwner !== owner &&
      status === "PLAYING" &&
      !countdownActive
    ) {
      const zone = $("flightZone");

      zone.classList.remove("catch");
      void zone.offsetWidth;
      zone.classList.add("catch");

      setTimeout(() => {
        zone.classList.remove("catch");
      }, 750);

      addLog("Bom berhasil dioper ke Player " + owner + "!");
    }

    lastOwner = owner;
  }

  if ($("gameState")) {
    $("gameState").textContent =
      status === "PLAYING"
        ? "BERLANGSUNG"
        : status === "COUNTDOWN"
        ? "BERSIAP"
        : status === "FINISHED"
        ? "SELESAI"
        : status || "MENUNGGU";
  }

  if (s.event && s.event !== lastEvent) {
    addLog(String(s.event));
    lastEvent = s.event;
  }
}


// ========================================
// KONEKSI MQTT
// ========================================
function connectToProject(id) {
  if (client) {
    try {
      client.end(true);
    } catch (e) {}

    client = null;
  }

  projectId = id.trim();

  if (!projectId) {
    addLog("Project ID belum diisi.");
    return;
  }

  lastGameStatus = "";
  lastOwner = null;
  lastEvent = "";
  explosionShown = false;
  gameStarted = false;
  lastSeen = { A: 0, B: 0 };

  cancelCountdown();

  $("explosionOverlay")?.classList.remove("show");

  resetSensorDisplay();

  setConnection("", "Menghubungkan...");
  addLog("Mencoba koneksi ke proyek " + projectId + ".");

  client = mqtt.connect(BROKER_URL, {
    clientId: "bbdash_" + Math.random().toString(16).slice(2, 10),
    clean: true,
    connectTimeout: 10000,
    reconnectPeriod: 3000,
    keepalive: 30
  });

  client.on("connect", () => {
    setConnection("connected", "Terhubung ke MQTT");

    client.subscribe(
      [
        `${projectId}/phone/+`,
        `${projectId}/game/status`,
        `${projectId}/game/state`
      ],
      { qos: 1 },
      (err) => {
        if (err) {
          addLog("Gagal berlangganan topik MQTT.");
        } else {
          addLog(
            "Dashboard terhubung. Menunggu data dari HP dan game."
          );
        }
      }
    );
  });

  client.on("reconnect", () => {
    setConnection("", "Menyambungkan ulang...");
  });

  client.on("offline", () => {
    setConnection("error", "Offline");
  });

  client.on("error", (err) => {
    setConnection("error", "Koneksi bermasalah");
    addLog("MQTT error: " + (err.message || err));
  });

  client.on("message", (topic, message) => {
    let payload;

    try {
      payload = JSON.parse(message.toString());
    } catch (e) {
      return;
    }

    if (
      topic === `${projectId}/game/status` ||
      topic === `${projectId}/game/state`
    ) {
      showGameStatus(payload);
      return;
    }

    const match = topic.match(/\/phone\/([AB])$/);

    if (match && payload) {
      showDevice(match[1], payload);
    }
  });
}


// ========================================
// TOMBOL DASHBOARD
// ========================================
if ($("connectForm")) {
  $("connectForm").addEventListener("submit", (e) => {
    e.preventDefault();
    connectToProject($("projectId").value);
  });
}

if ($("connectButton")) {
  $("connectButton").addEventListener("click", (e) => {
    e.preventDefault();
    connectToProject($("projectId").value);
  });
}

if ($("clearLog")) {
  $("clearLog").addEventListener("click", () => {
    $("activityList").innerHTML =
      '<div class="empty-state">Riwayat dibersihkan. Event baru akan muncul di sini.</div>';
  });
}


// ========================================
// MONITOR HP ONLINE / OFFLINE
// ========================================
setInterval(() => {
  ["A", "B"].forEach((letter) => {
    if (
      lastSeen[letter] &&
      Date.now() - lastSeen[letter] > 7000
    ) {
      if ($("miniState" + letter)) {
        $("miniState" + letter).textContent = "● HP offline";
      }

      if ($("laneState" + letter)) {
        $("laneState" + letter).textContent = "OFFLINE";
      }
    }
  });

  if ($("deviceCount")) {
    $("deviceCount").textContent =
      ["A", "B"].filter(
        (letter) =>
          lastSeen[letter] &&
          Date.now() - lastSeen[letter] < 7000
      ).length + " / 2";
  }
}, 2000);
