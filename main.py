from flask import Flask, render_template, request
import folium
from geopy.geocoders import Nominatim
from itertools import cycle
app = Flask(__name__)
geolocator = Nominatim(user_agent="kierowcy_app")
START_ADDRESS = "ul. Ekologiczna 12, 05-080 Klaudyn"
def geocode_address(address):
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None
def create_routes(addresses, num_drivers):
    # Dodaj start
    addresses = [START_ADDRESS] + addresses
    coords = [geocode_address(a) for a in addresses]
    coords = [c for c in coords if c]
    # Podziel na kierowców cyklicznie
    drivers = [[] for _ in range(num_drivers)]
    driver_cycle = cycle(range(num_drivers))
    for c in coords[1:]:  # pomijamy start
        drivers[next(driver_cycle)].append(c)
    # Dodaj start na początku i końcu każdej trasy
    routes = []
    for d in drivers:
        if d:
            routes.append([coords[0]] + d + [coords[0]])
    return routes
@app.route("/", methods=["GET", "POST"])
def index():
    map_html = None
    if request.method == "POST":
        addresses_text = request.form.get("addresses", "")
        num_drivers = int(request.form.get("num_drivers", 1))
        addresses = [a.strip() for a in addresses_text.split("\n") if a.strip()]
        routes = create_routes(addresses, num_drivers)
        # Stwórz mapę
        m = folium.Map(location=geocode_address(START_ADDRESS), zoom_start=12)
        colors = ["red", "blue", "green", "orange", "purple"]
        for i, route in enumerate(routes):
            folium.PolyLine(route, color=colors[i % len(colors)], weight=5, opacity=0.8).add_to(m)
            for lat, lon in route:
                folium.Marker([lat, lon]).add_to(m)
        map_html = m._repr_html_()
    return f"""
    <html>
    <body>
    <h2>Wpisz adresy (po jednym w linii):</h2>
    <form method="post">
        <textarea name="addresses" rows="10" cols="40"></textarea><br>
        Liczba kierowców: <input type="number" name="num_drivers" value="1" min="1"><br>
        <input type="submit" value="Generuj trasę">
    </form>
    {map_html if map_html else ""}
    </body>
    </html>
    """
if __name__ == "__main__":
    app.run(debug=True)
