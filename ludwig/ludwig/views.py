from django.shortcuts import render
from django.conf import settings
import os
from ludwig.scripts import generate_plots as gp  # Import our plotting module

def generate_plot(request):
    """
    Renders the plot configuration form on GET requests and processes the form
    on POST to generate a polar scatter plot.
    """
    plot_url = None
    error = None

    if request.method == "POST":
        try:
            harm_number = int(request.POST.get("harm_number", 3))
            phase = request.POST.get("phase", "Phase A")
            night_mode = request.POST.get("night_mode", "off") == "on"
            threshold = request.POST.get("threshold", "")
            threshold = float(threshold) if threshold else None

            # Fetch data from the database and generate the plot.
            df = gp.fetch_data(harm_number, night_mode, threshold)
            gp.generate_and_save_plots(df, phase, harm_number)

            # Construct the plot filename.
            filename = f"polar_scatter_{phase.replace(' ', '_')}_{harm_number}.png"
            # Assume that the plots folder is served as static files under /static/plots/
            plot_url = f"/static/plots/{filename}"
        except Exception as e:
            error = str(e)

    return render(request, "plot_generator.html", {"plot_url": plot_url, "error": error})
