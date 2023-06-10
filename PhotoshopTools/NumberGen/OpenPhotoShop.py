import os
from win32com.client import Dispatch

# Initialize Photoshop application
app = Dispatch("Photoshop.Application")

# Open PSD file
# Replace path with local path
doc = app.Open(r"X:\your_workspace\Tools\PhotoshopTools\NumberGen\numbersBase1.psd")

# Loop through numbers 0-9
for i in range(10):
    # Change text layer to current number
    text_layer = doc.ArtLayers[0]
    text_layer.TextItem.Contents = str(i)

    # Export as PNG
    filename = f"N{i}.png"
    #Replace path with local path
    filepath = os.path.join(r"X:\your_workspace\Tools\PhotoshopTools\NumberGen\Numbers", filename)

    # Set up PNGSaveOptions
    png_options = Dispatch("Photoshop.PNGSaveOptions")
    png_options.Compression = 0  # No compression

    # Save the modified document as PNG using SaveAs()
    doc.SaveAs(filepath, png_options, True)

# Close document and quit application
doc.Close(2)  # Use parameter 2 to close without saving
app.Quit()

