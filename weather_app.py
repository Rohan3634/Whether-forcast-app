import tkinter as tk
from tkinter import ttk, messagebox
import requests

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Weather")
        self.root.geometry("450x400")
        self.root.configure(bg="#f0f4f8")
        
        # Apply modern UI styling
        self.style = ttk.Style()
        self.style.theme_use('vista')
        
        # UI Header Component
        self.header_label = tk.Label(
            root, text="🌤️ Weather Forecast", 
            font=("Segoe UI", 18, "bold"), bg="#f0f4f8", fg="#2c3e50"
        )
        self.header_label.pack(pady=15)
        
        # Manual Input Frame
        self.input_frame = tk.Frame(root, bg="#f0f4f8")
        self.input_frame.pack(pady=5)
        
        self.city_entry = ttk.Entry(self.input_frame, font=("Segoe UI", 11), width=22)
        self.city_entry.insert(0, "Detecting location...")
        self.city_entry.pack(side=tk.LEFT, padx=5)
        
        self.search_btn = ttk.Button(self.input_frame, text="Search City", command=self.fetch_manual_weather)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        # Weather Display Card
        self.card = tk.Frame(root, bg="white", bd=0, highlightbackground="#dcdde1", highlightthickness=1)
        self.card.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        self.loc_label = tk.Label(self.card, text="Locating...", font=("Segoe UI", 14, "bold"), bg="white", fg="#34495e")
        self.loc_label.pack(pady=(15, 5))
        
        self.temp_label = tk.Label(self.card, text="--°C", font=("Segoe UI", 36, "bold"), bg="white", fg="#2980b9")
        self.temp_label.pack(pady=5)
        
        self.desc_label = tk.Label(self.card, text="Gathering data...", font=("Segoe UI", 11, "italic"), bg="white", fg="#7f8c8d")
        self.desc_label.pack(pady=5)
        
        # Extra Stats Container
        self.stats_frame = tk.Frame(self.card, bg="white")
        self.stats_frame.pack(pady=10, fill=tk.X)
        
        self.wind_label = tk.Label(self.stats_frame, text="Wind: -- km/h", font=("Segoe UI", 10), bg="white", fg="#57606f")
        self.wind_label.pack(side=tk.LEFT, expand=True)
        
        self.humid_label = tk.Label(self.stats_frame, text="Humidity: --%", font=("Segoe UI", 10), bg="white", fg="#57606f")
        self.humid_label.pack(side=tk.RIGHT, expand=True)

        # Map weather codes from Open-Meteo API to human phrases
        self.weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle", 
            53: "Moderate drizzle", 55: "Dense drizzle", 61: "Slight rain", 
            63: "Moderate rain", 65: "Heavy rain", 71: "Slight snow fall", 
            73: "Moderate snow fall", 75: "Heavy snow fall", 95: "Thunderstorm"
        }
        
        # Automatically detect location on startup
        self.root.after(100, self.auto_detect_location)

    def auto_detect_location(self):
        """Finds user coordinates using IP address geolocation."""
        try:
            geo_response = requests.get("http://ip-api.com/json/", timeout=5).json()
            if geo_response.get("status") == "success":
                lat = geo_response.get("lat")
                lon = geo_response.get("lon")
                city = geo_response.get("city")
                region = geo_response.get("regionName")
                
                self.city_entry.delete(0, tk.END)
                self.city_entry.insert(0, f"{city}, {region}")
                self.get_weather_by_coords(lat, lon, f"{city}, {region}")
            else:
                self.handle_detection_failure()
        except Exception:
            self.handle_detection_failure()

    def handle_detection_failure(self):
        self.city_entry.delete(0, tk.END)
        self.city_entry.focus()
        self.loc_label.config(text="Enter a city above")
        self.desc_label.config(text="Auto-location unavailble")

    def get_weather_by_coords(self, lat, lon, location_name):
        """Hits the keyless Open-Meteo API to fetch telemetry data."""
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            weather_data = requests.get(url, timeout=5).json()
            
            current = weather_data["current"]
            temp = round(current["temperature_2m"])
            humidity = current["relative_humidity_2m"]
            wind = current["wind_speed_10m"]
            code = current["weather_code"]
            
            description = self.weather_codes.get(code, "Unknown conditions")
            
            # Refresh GUI elements safely
            self.loc_label.config(text=location_name)
            self.temp_label.config(text=f"{temp}°C")
            self.desc_label.config(text=description)
            self.wind_label.config(text=f"💨 Wind: {wind} km/h")
            self.humid_label.config(text=f"💧 Humidity: {humidity}%")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve weather metrics: {str(e)}")

    def fetch_manual_weather(self):
        """Geocodes text inputs using Open-Meteo's geocoding endpoint if manual lookup is requested."""
        query = self.city_entry.get().strip()
        if not query or query == "Detecting location...":
            return
            
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=1&language=en&format=json"
            geo_res = requests.get(geo_url, timeout=5).json()
            
            if "results" in geo_res and len(geo_res["results"]) > 0:
                result = geo_res["results"][0]
                lat = result["latitude"]
                lon = result["longitude"]
                name = result["name"]
                country = result.get("country", "")
                
                display_name = f"{name}, {country}" if country else name
                self.get_weather_by_coords(lat, lon, display_name)
            else:
                messagebox.showwarning("Not Found", f"Could not pinpoint '{query}'. Check spelling.")
        except Exception as e:
            messagebox.showerror("Network Error", f"Could not reach server: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()