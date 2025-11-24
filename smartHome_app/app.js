import { getLastRoomData } from "./api_client.js";
import { createWebSocket } from './ws_client.js';

const sensorsStore = new Map();
// Funkcja do aktualizacji UI
function updateUISocket(data) {
    console.log("OTRZYMAŁEM Z SOCKETA", data)
    if (Array.isArray(data)) {
        handleActivatorsUpdate(data);
    }else{
        const sensor = sensorsStore.get(data.uuid);
        if (!sensor) {
            console.warn("Sensor ID not found in store", data.sensor_id);
            return;
        }
        updateUI(sensor.room, sensor.type, data.value);
    }
}

function handleActivatorsUpdate(activatorsArray) {
    console.log(`Otrzymano ${activatorsArray.length} Aktywatorów. Rozpoczynanie aktualizacji.`); 
    
    activatorsArray.forEach(activator => {
        const { type, room_number, status, auto, id } = activator;
        const roomPrefix = `room${room_number}`;
        
        
        // AKTUALIZACJA STATUSU TEKSTOWEGO W INTERFEJSIE
        const statusElement = document.getElementById(`${roomPrefix}-${type}-status`);
        //console.log(`Aktualizowanie statusu dla ${type} w pokoju ${room_number} trybu ${auto}`);
        if (statusElement) {
            let statusText = status==="ON" ? "WŁĄCZONE" : "WYŁĄCZONE";
            let autoText = auto===true ? 'AUTO' : "MANUAL";
            // Lepsze formatowanie tekstu statusu dla trybów
            if (type === 'heater' || type === 'vent') {
                
                statusElement.textContent = `Status: ${autoText} ${type === 'heater' ? 'Ogrzewanie' : 'Wentylacja'} ${statusText}.`;
            } else {
                statusElement.textContent = `Status: ${autoText} ${type === 'light' ? 'Światło' : 'Alarm'} ${statusText}.`;
                if (type === 'light' && status === 'ON' ){
                    const lightElementId = `${roomPrefix}-light`;
                    const lightElement = document.getElementById(lightElementId);
                    lightElement.classList.add('light-on');
                    lightElement.classList.remove('light-off');
                }
                else if (type === 'light' && status === 'OFF' ){
                    const lightElementId = `${roomPrefix}-light`;
                    const lightElement = document.getElementById(lightElementId);
                    lightElement.classList.add('light-off');
                    lightElement.classList.remove('light-on');
                }
            }
        }

    });
}

const ws = createWebSocket(updateUISocket);

/**
 * Przełącza stan wizualny światła (ON/OFF) i aktualizuje status tekstowy.
 * @param {string} room - Nazwa pokoju ('room1' lub 'room2').
 */
function toggleLight(room) {
    const lightElementId = `${room}-light`;
    const lightElement = document.getElementById(lightElementId);
    const button = document.getElementById(`light${room.slice(-1)}-btn`);

    // Prosta symulacja: przełączanie klas
    const isLightOn = lightElement.classList.contains('light-on');
    const room_id = room === 'room1' ? 1 : 2;
    const id = room === 'room1' ? "504895d3-4cf8-4516-ad7f-98daf340304c" : "6966b068-cef5-4d30-b73d-9b9a057e4a64"

    if (!isLightOn) {
        // Włącz światło
        lightElement.classList.add('light-on');
        lightElement.classList.remove('light-off');
        button.style.backgroundColor = '#f59e0b';
        console.log("ON światło w pokoju:", room);
        
        ws.send(JSON.stringify({
            id: id,
            type: "light",
            room_number: room_id,
            status: "ON",
            auto: false
        }));
    } else {
        // Wyłącz światło
        lightElement.classList.remove('light-on');
        lightElement.classList.add('light-off');
        button.style.backgroundColor = '#9ca3af'; // Szary kolor po wyłączeniu
        console.log("OFF światło w pokoju:", room);
        ws.send(JSON.stringify({
            id: id,
            type: "light",
            room_number: room_id,
            status: "OFF",
            auto: true
        }));
    }
}

function toggleAlarm(room) {
    const alarmElementId = `${room}-light`;
    const alarmElement = document.getElementById(alarmElementId);
    const button = document.getElementById(`alarm${room.slice(-1)}-btn`);
    const isAlarmOn = alarmElement.classList.contains('alarm-on');
    const id = room === 'room1' ? "9e9da477-ac57-4d0b-a802-4d283de67005" : "d8e7200c-9f1c-4e66-a4fc-7b5c322e03ea"
    const room_id = room === 'room1' ? 1 : 2;
    if (!isAlarmOn) {
        button.style.backgroundColor = '#e54712ff';
        alarmElement.classList.add('alarm-on');
        ws.send(JSON.stringify({
            id: id,
            type: "alarm",
            room_number: room_id,
            status: "ON",
            auto: false
        }));
    } else {
        alarmElement.classList.remove('alarm-on');
        button.style.backgroundColor = '#9ca3af';
        ws.send(JSON.stringify({
            id: id,
            type: "alarm",
            room_number: room_id,
            status: "OFF",
            auto: true
        }));
    }
}

// Pobranie z bazy danych id sensorów
function updateUIFromSensors(data) {
    data.forEach(item => {

        sensorsStore.set(item.sensor_id, {
            room: item.room_number,
            type: item.sensor_type
        });

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

    if (type === "movement") {
        console.log("Ruch wykryty w pokoju", room, "Wartość:", value);
        const alarmElementId = `room${room}-light`;
        const alarmElement = document.getElementById(alarmElementId);
        const isAlarmOn = alarmElement.classList.contains('alarm-on');
        if (isAlarmOn && value == 1) {
            console.log("ALARM! Ruch wykryty w pokoju", room);
            alarmElement.classList.add('motion-detected');
            setTimeout(() => {
                alarmElement.classList.remove('motion-detected');
            }, 2000);
        }
    }

}

document.addEventListener('DOMContentLoaded', async () => {
    // --- POBRANIE DANYCH Z BACKENDU NA START ---
    const lastData = await getLastRoomData();
    console.log("Dane z backendu na starcie:", lastData);
    updateUIFromSensors(lastData);
    
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
            sendSocketData('5435887c-d251-4007-9dcd-3618238edd17', 'heater', 1, mode)
        });
    });
    modeButtons1H.forEach(btn => {
        btn.addEventListener('click', () => {
            modeButtons1H.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const mode = btn.id.replace('mode-', '');
            console.log("Wybrany tryb:", mode);
            sendSocketData('3de9c84a-fbda-4e74-a898-7735321bece1', 'vent', 1, mode)
        });
    });
        modeButtons2T.forEach(btn => {
        btn.addEventListener('click', () => {
            modeButtons2T.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const mode = btn.id.replace('mode-', '');
            console.log("Wybrany tryb:", mode);
            sendSocketData('a21b600f-28b5-4c9a-b5cc-e554b2ec9f1f', 'heater', 2, mode)
        });
    });
    modeButtons2H.forEach(btn => {
        btn.addEventListener('click', () => {
            modeButtons2H.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const mode = btn.id.replace('mode-', '');
            console.log("Wybrany tryb:", mode);
            sendSocketData('a3aeaee4-d84e-4ebe-b8c4-db0c6a66eee1', 'vent', 2, mode)
        });
    });

    function sendSocketData (id, type, room_id, mode){
        let status_val = "OFF"
        let auto = false
        if (mode === "auto"){
            auto = true
        }
        if (mode === "on"){
            status_val = "ON"
        }
        if (mode === "off"){
            status_val = "OFF"
        }
        ws.send(JSON.stringify({
            id: id,
            type: type,
            room_number: room_id,
            status: status_val,
            auto: auto
        }));
    }

     
});