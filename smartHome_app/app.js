import { getLastRoomData } from "./api_client.js";
/**
 * Przełącza stan wizualny światła (ON/OFF) i aktualizuje status tekstowy.
 * @param {string} room - Nazwa pokoju ('room1' lub 'room2').
 */
function toggleLight(room) {
    const lightElementId = `${room}-light`;
    const statusElementId = `${room}-status`;

    const lightElement = document.getElementById(lightElementId);
    const statusElement = document.getElementById(statusElementId);
    const button = document.getElementById(`light${room.slice(-1)}-btn`);

    // Prosta symulacja: przełączanie klas
    const isLightOn = lightElement.classList.contains('light-on');

    if (!isLightOn) {
        // Włącz światło
        lightElement.classList.remove('light-off');
        lightElement.classList.add('light-on');
        statusElement.textContent = 'Status: Światło WŁĄCZONE.';
        button.style.backgroundColor = '#f59e0b'; // Złoty kolor po włączeniu
    } else {
        // Wyłącz światło
        lightElement.classList.remove('light-on');
        lightElement.classList.add('light-off');
        statusElement.textContent = 'Status: Światło WYŁĄCZONE.';
        button.style.backgroundColor = '#9ca3af'; // Szary kolor po wyłączeniu
    }
}

/**
 * Aktualizuje wartość suwaka w panelu i w wizualizacji SVG (tylko temperatura).
 * @param {string} sliderId - ID suwaka ('temp1-slider', 'humidity2-slider', etc.).
 * @param {string} valueDisplayId - ID elementu <span> z wartością numeryczną.
 * @param {string | null} svgDisplayId - ID elementu <text> w SVG (lub null, jeśli nie dotyczy).
 */
function updateValue(sliderId, valueDisplayId, svgDisplayId) {
    const slider = document.getElementById(sliderId);
    const valueDisplay = document.getElementById(valueDisplayId);
    
    const value = slider.value;
    valueDisplay.textContent = value;

    // Aktualizuj wartość w SVG (jeśli dotyczy, np. dla temperatury)
    if (svgDisplayId) {
        const svgDisplay = document.getElementById(svgDisplayId);
        if (svgDisplay) {
            const unit = (sliderId.includes('temp')) ? '°C' : '%';
            const label = (sliderId.includes('temp')) ? 'T' : 'W';
            svgDisplay.textContent = `${label}: ${value}${unit}`;
        }
    }
}


// --- INICJALIZACJA I PODPIĘCIE ZDARZEŃ ---

document.addEventListener('DOMContentLoaded', async () => {
    // --- POBRANIE DANYCH Z BACKENDU NA START ---
    const lastData = await getLastRoomData();
    console.log("Dane z backendu na starcie:", lastData);

    // --- POKÓJ 1 ---
    
    // Oświetlenie
    document.getElementById('light1-btn').addEventListener('click', () => {
        console.log("KLikam przycisk 1")
        toggleLight('room1');
    });

    // Temperatura
    const temp1Slider = document.getElementById('temp1-slider');
    temp1Slider.addEventListener('input', () => {
        updateValue('temp1-slider', 'temp1-value', 'room1-temp-display');
    });
    // Wymuszenie aktualizacji przy starcie
    temp1Slider.dispatchEvent(new Event('input')); 

    // Wilgotność
    document.getElementById('humidity1-slider').addEventListener('input', () => {
        updateValue('humidity1-slider', 'humidity1-value','room1-humidity-display');
    });

    // Ruch
    // document.getElementById('motion1-btn').addEventListener('click', () => {
    //     simulateMotion('room1');
    // });

    // --- POKÓJ 2 ---
    
    // Oświetlenie
    document.getElementById('light2-btn').addEventListener('click', () => {
        console.log("KLikam przycisk 2")
        toggleLight('room2');
    });

    // Temperatura
    const temp2Slider = document.getElementById('temp2-slider');
    temp2Slider.addEventListener('input', () => {
        updateValue('temp2-slider', 'temp2-value', 'room2-temp-display');
    });
    // Wymuszenie aktualizacji przy starcie
    temp2Slider.dispatchEvent(new Event('input'));
    
    // Wilgotność
    document.getElementById('humidity2-slider').addEventListener('input', () => {
        updateValue('humidity2-slider', 'humidity2-value', 'room2-humidity-display');
    });
    
    // Ruch
    // document.getElementById('motion1-btn').addEventListener('click', () => {
    //     simulateMotion('room1');
    // });

    // Opcjonalnie: kliknięcie na SVG włącza/wyłącza światło w danym pokoju
    document.querySelectorAll('.room-area').forEach(room => {
        room.addEventListener('click', (e) => {
            const roomName = e.target.dataset.room;
            toggleLight(roomName);
        });
    });

    const modeButtons1T = document.querySelectorAll('.mode-btn-1T');
    const modeButtons1H = document.querySelectorAll('.mode-btn-1H');
    const modeButtons2T = document.querySelectorAll('.mode-btn-2T');
    const modeButtons2H = document.querySelectorAll('.mode-btn-2H');

    modeButtons1T.forEach(btn => {
        btn.addEventListener('click', () => {
            modeButtons1T.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const mode = btn.id.replace('mode-', '');
            console.log("Wybrany tryb:", mode);
        });
    });
    modeButtons1H.forEach(btn => {
        btn.addEventListener('click', () => {
            modeButtons1H.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const mode = btn.id.replace('mode-', '');
            console.log("Wybrany tryb:", mode);
        });
    });
        modeButtons2T.forEach(btn => {
        btn.addEventListener('click', () => {
            modeButtons2T.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const mode = btn.id.replace('mode-', '');
            console.log("Wybrany tryb:", mode);
        });
    });
    modeButtons2H.forEach(btn => {
        btn.addEventListener('click', () => {
            modeButtons2H.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const mode = btn.id.replace('mode-', '');
            console.log("Wybrany tryb:", mode);
        });
    });

     
});