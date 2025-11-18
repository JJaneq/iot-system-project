export async function getLastRoomData() {
    try {
        // const response = await fetch('http://manager:3000/api/lastdata')
        // TESTOWO BO SIEC DOCKERA NIE DZIALA
        // const response = await fetch('http://localhost:3000/api/lastdata')
        console.log(response)
        if (!response.ok) throw new Error("Błąd pobierania danych");
        return await response.json();
    } catch (err) {
        console.error("API error:", err);
        return null;
    }
}