import tkinter as tk
import requests

from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime


# ==========================================
# OPENWEATHERMAP API KEY
# ==========================================


API_KEY = "16d25e453fd324b2b754943959ad8bae"


# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()
root.title("Weather App")
root.geometry("600x900")
root.configure(bg="lightblue")


# ==========================================
# TITLE
# ==========================================

title_label = tk.Label(
    root,
    text="Weather App",
    font=("Arial", 24, "bold"),
    bg="lightblue"
)

title_label.pack(pady=20)


# ==========================================
# CITY / ZIP CODE INPUT
# ==========================================

city_label = tk.Label(
    root,
    text="Enter City Name or ZIP Code",
    font=("Arial", 12),
    bg="lightblue"
)

city_label.pack(pady=5)


city_entry = tk.Entry(
    root,
    font=("Arial", 14),
    width=30
)

city_entry.pack(pady=5)


# ==========================================
# CELSIUS / FAHRENHEIT
# ==========================================

unit_var = tk.StringVar(value="C")


unit_frame = tk.Frame(
    root,
    bg="lightblue"
)

unit_frame.pack(pady=10)


celsius_radio = tk.Radiobutton(
    unit_frame,
    text="Celsius (°C)",
    variable=unit_var,
    value="C",
    bg="lightblue"
)

celsius_radio.pack(
    side="left",
    padx=10
)


fahrenheit_radio = tk.Radiobutton(
    unit_frame,
    text="Fahrenheit (°F)",
    variable=unit_var,
    value="F",
    bg="lightblue"
)

fahrenheit_radio.pack(
    side="left",
    padx=10
)


# ==========================================
# GET WEATHER FUNCTION
# ==========================================

def get_weather():

    city = city_entry.get().strip()


    # --------------------------------------
    # EMPTY INPUT VALIDATION
    # --------------------------------------

    if city == "":
        result_label.config(
            text="Please enter a city name or ZIP code.",
            fg="red"
        )

        icon_label.config(image="")
        icon_label.image = None

        hourly_label.config(text="")
        daily_label.config(text="")

        return


    # --------------------------------------
    # CITY NAME OR ZIP CODE
    # --------------------------------------

    if city.isdigit():

        # ZIP CODE
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?zip={city},IN"
            f"&appid={API_KEY}"
            "&units=metric"
        )

    else:

        # CITY NAME
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}"
            f"&appid={API_KEY}"
            "&units=metric"
        )


    try:

        # ==================================
        # CURRENT WEATHER API
        # ==================================

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()


        # ----------------------------------
        # API ERROR
        # ----------------------------------

        if response.status_code != 200:

            result_label.config(
                text="Error: "
                + data.get(
                    "message",
                    "Unable to get weather information."
                ),
                fg="red"
            )

            icon_label.config(image="")
            icon_label.image = None

            hourly_label.config(text="")
            daily_label.config(text="")

            return


        # ==================================
        # CURRENT WEATHER DATA
        # ==================================

        city_name = data["name"]

        temperature_c = data["main"]["temp"]

        temperature_f = (
            temperature_c * 9 / 5
        ) + 32

        humidity = data["main"]["humidity"]

        condition = data["weather"][0]["description"]

        wind_speed = data["wind"]["speed"]


        # ==================================
        # CELSIUS / FAHRENHEIT
        # ==================================

        if unit_var.get() == "C":

            temperature = temperature_c
            unit = "°C"

        else:

            temperature = temperature_f
            unit = "°F"


        # ==================================
        # CURRENT WEATHER DISPLAY
        # ==================================

        result_label.config(
            text=
            "City: " + city_name
            + "\nTemperature: "
            + str(round(temperature, 2))
            + " "
            + unit
            + "\nHumidity: "
            + str(humidity)
            + "%"
            + "\nCondition: "
            + condition
            + "\nWind Speed: "
            + str(wind_speed)
            + " m/s",
            fg="black"
        )


        # ==================================
        # WEATHER ICON
        # ==================================

        icon_code = data["weather"][0]["icon"]

        icon_url = (
            "https://openweathermap.org/img/wn/"
            f"{icon_code}@2x.png"
        )


        icon_response = requests.get(
            icon_url,
            timeout=10
        )


        if icon_response.status_code == 200:

            icon_image = Image.open(
                BytesIO(icon_response.content)
            )

            icon_photo = ImageTk.PhotoImage(
                icon_image
            )

            icon_label.config(
                image=icon_photo
            )

            icon_label.image = icon_photo


        # ==================================
        # COORDINATES
        # ==================================

        lat = data["coord"]["lat"]

        lon = data["coord"]["lon"]


        # ==================================
        # 5-DAY / 3-HOUR FORECAST API
        # ==================================

        forecast_url = (
            "https://api.openweathermap.org/data/2.5/forecast"
            f"?lat={lat}"
            f"&lon={lon}"
            f"&appid={API_KEY}"
            "&units=metric"
        )


        forecast_response = requests.get(
            forecast_url,
            timeout=10
        )


        forecast_data = forecast_response.json()


        if forecast_response.status_code != 200:

            hourly_label.config(
                text="Unable to get forecast.",
                fg="red"
            )

            daily_label.config(text="")

            return


        # ==================================
        # NEXT 6 HOURS
        # ==================================

        forecast_text = "Next 6 Hours\n"

        forecast_text += "-------------\n"


        # OpenWeatherMap gives forecasts
        # every 3 hours.
        # First 2 entries = next 6 hours.

        for item in forecast_data["list"][:2]:

            forecast_time = datetime.fromtimestamp(
                item["dt"]
            )

            forecast_temp = item["main"]["temp"]


            # --------------------------------
            # UNIT CONVERSION
            # --------------------------------

            if unit_var.get() == "C":

                display_temp = forecast_temp
                display_unit = "°C"

            else:

                display_temp = (
                    forecast_temp * 9 / 5
                ) + 32

                display_unit = "°F"


            forecast_condition = (
                item["weather"][0]["description"]
            )


            forecast_text += (
                forecast_time.strftime("%H:%M")
                + " - "
                + str(round(display_temp, 1))
                + " "
                + display_unit
                + " - "
                + forecast_condition
                + "\n"
            )


        hourly_label.config(
            text=forecast_text,
            fg="black"
        )


        # ==================================
        # 5-DAY FORECAST
        # ==================================

        daily_data = {}


        for item in forecast_data["list"]:

            forecast_date = datetime.fromtimestamp(
                item["dt"]
            ).strftime("%Y-%m-%d")


            forecast_time = datetime.fromtimestamp(
                item["dt"]
            )


            # --------------------------------
            # STORE ONE FORECAST PER DAY
            # CLOSEST TO 12 PM
            # --------------------------------

            if forecast_date not in daily_data:

                daily_data[forecast_date] = item


            elif abs(
                forecast_time.hour - 12
            ) < abs(
                datetime.fromtimestamp(
                    daily_data[forecast_date]["dt"]
                ).hour - 12
            ):

                daily_data[forecast_date] = item


        # ==================================
        # DISPLAY 5-DAY FORECAST
        # ==================================

        daily_text = "5-Day Forecast\n"

        daily_text += "---------------\n"


        count = 0


        for date, item in daily_data.items():

            if count >= 5:
                break


            display_date = datetime.strptime(
                date,
                "%Y-%m-%d"
            ).strftime("%d %b")


            forecast_temp = item["main"]["temp"]


            # --------------------------------
            # UNIT CONVERSION
            # --------------------------------

            if unit_var.get() == "C":

                display_temp = forecast_temp
                display_unit = "°C"

            else:

                display_temp = (
                    forecast_temp * 9 / 5
                ) + 32

                display_unit = "°F"


            forecast_condition = (
                item["weather"][0]["description"]
            )


            daily_text += (
                display_date
                + " - "
                + str(round(display_temp, 1))
                + " "
                + display_unit
                + " - "
                + forecast_condition
                + "\n"
            )


            count += 1


        daily_label.config(
            text=daily_text,
            fg="black"
        )


    # ======================================
    # TIMEOUT ERROR
    # ======================================

    except requests.exceptions.Timeout:

        result_label.config(
            text="Error: Request timed out. Please try again.",
            fg="red"
        )

        icon_label.config(image="")
        icon_label.image = None

        hourly_label.config(text="")
        daily_label.config(text="")


    # ======================================
    # NETWORK ERROR
    # ======================================

    except requests.exceptions.RequestException:

        result_label.config(
            text="Error: Network connection problem.",
            fg="red"
        )

        icon_label.config(image="")
        icon_label.image = None

        hourly_label.config(text="")
        daily_label.config(text="")


    # ======================================
    # UNEXPECTED ERROR
    # ======================================

    except Exception as error:

        result_label.config(
            text="Error: " + str(error),
            fg="red"
        )

        icon_label.config(image="")
        icon_label.image = None

        hourly_label.config(text="")
        daily_label.config(text="")


# ==========================================
# GET WEATHER BUTTON
# ==========================================

get_button = tk.Button(
    root,
    text="Get Weather",
    font=("Arial", 12, "bold"),
    command=get_weather
)

get_button.pack(pady=15)


# ==========================================
# CURRENT WEATHER RESULT
# ==========================================

result_label = tk.Label(
    root,
    text="",
    font=("Arial", 12),
    bg="lightblue",
    justify="left"
)

result_label.pack(pady=10)


# ==========================================
# WEATHER ICON
# ==========================================

icon_label = tk.Label(
    root,
    bg="lightblue"
)

icon_label.pack(pady=10)


# ==========================================
# NEXT 6 HOURS LABEL
# ==========================================

hourly_label = tk.Label(
    root,
    text="",
    font=("Arial", 11),
    bg="lightblue",
    justify="left"
)

hourly_label.pack(pady=10)


# ==========================================
# 5-DAY FORECAST LABEL
# ==========================================

daily_label = tk.Label(
    root,
    text="",
    font=("Arial", 11),
    bg="lightblue",
    justify="left"
)

daily_label.pack(pady=10)


# ==========================================
# START APPLICATION
# ==========================================

root.mainloop()