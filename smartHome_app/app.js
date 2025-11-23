import { getLastRoomData } from "./api_client.js";
import { createWebSocket } from './ws_client.js';

const sensorsStore = new Map();
// Funkcja do aktualizacji UI
function updateUISocket(data) {
    console.log("OTRZYMAŁEM Z SOCKETA", data)
    const sensor = sensorsStore.get(data.uuid);

    if (!sensor) {
        console.warn("Sensor ID not found in store", data.sensor_id);
        return;
    }
    updateUI(sensor.room, sensor.type, data.value);
}

const ws = createWebSocket(updateUISocket);

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
    const room_id = room === 'room1' ? 1 : 2;

    if (!isLightOn) {
        // Włącz światło
        lightElement.classList.remove('light-off');
        lightElement.classList.add('light-on');
        statusElement.textContent = 'Status: Światło WŁĄCZONE.';
        button.style.backgroundColor = '#f59e0b';

        ws.send(JSON.stringify({
            id: "504895d3-4cf8-4516-ad7f-98daf340304c",
            type: "light",
            room_number: room_id,
            status: "on",
            auto: false
        }));
    } else {
        // Wyłącz światło
        lightElement.classList.remove('light-on');
        lightElement.classList.add('light-off');
        statusElement.textContent = 'Status: Światło WYŁĄCZONE.';
        button.style.backgroundColor = '#9ca3af'; // Szary kolor po wyłączeniu

        ws.send(JSON.stringify({
            id: "504895d3-4cf8-4516-ad7f-98daf340304c",
            type: "light",
            room_number: room_id,
            status: "off",
            auto: false
        }));
    }
}


function toggleAlarm(room) {
    const alarmElementId = `${room}-light`;
    const alarmElement = document.getElementById(alarmElementId);
    const button = document.getElementById(`alarm${room.slice(-1)}-btn`);
    const isAlarmOn = alarmElement.classList.contains('alarm-on');
    if (!isAlarmOn) {
        button.style.backgroundColor = '#e54712ff';
        alarmElement.classList.add('alarm-on');
        ws.send(JSON.stringify({
            type: "alarm",
            room,
            state: "on"
        }));
    } else {
        button.style.backgroundColor = '#9ca3af';
        alarmElement.classList.remove('alarm-on');
        ws.send(JSON.stringify({
            type: "alarm",
            room,
            state: "off"
        }));
    }
}

function updateUIFromSensors(data) {
    data.forEach(item => {

        sensorsStore.set(item.sensor_id, {
            room: item.room_number,
            type: item.sensor_type
        });
        console.log(sensorsStore)

        updateUI(item.room_number, item.sensor_type, item.value);
    });
}

function updateUI(room, type, value) {
    if (type === "temperature") {
        document.getElementById(`temp${room}-value`).textContent = value.toFixed(1);
        document.getElementById(`room${room}-temp-display`).textContent = `T: ${value.toFixed(1)}°C`;
    }

    if (type === "humidity") {
        document.getElementById(`humidity${room}-value`).textContent = value.toFixed(1);
        document.getElementById(`room${room}-humidity-display`).textContent = `W: ${value.toFixed(1)}%`;
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    // --- POBRANIE DANYCH Z BACKENDU NA START ---
    const lastData = await getLastRoomData();
    console.log("Dane z backendu na starcie:", lastData);
    updateUIFromSensors(lastData);
    
    // --- POKÓJ 1 ---
    
    // Oświetlenie
    document.getElementById('light1-btn').addEventListener('click', () => {
        console.log("KLikam przycisk 1")
        toggleLight('room1');
        
    });
       
    // Alarm
    document.getElementById('alarm1-btn').addEventListener('click', () => {
        console.log("Włączam alarm 1")
        toggleAlarm('room1');
        
    });

    // Alarm2
    document.getElementById('alarm2-btn').addEventListener('click', () => {
        console.log("Włączam alarm 2")
        toggleAlarm('room2');
        
    });
    
    // Oświetlenie
    document.getElementById('light2-btn').addEventListener('click', () => {
        console.log("KLikam przycisk 2")
        toggleLight('room2');
    });


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