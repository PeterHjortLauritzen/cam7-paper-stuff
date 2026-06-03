from PIL import Image
import matplotlib.pyplot as plt

# === UPDATE THESE FILENAMES TO MATCH YOUR DOWNLOADED FILES ===
img_a = Image.open("a.png")   # (a) Default bias
img_b = Image.open("b.png")  # (b) QuadTune prediction
img_c = Image.open("c.png")   # (c) After tuning

# Force same height while preserving aspect ratio (high-quality resize)
target_height = max(img_a.height, img_b.height, img_c.height)
img_a = img_a.resize((int(img_a.width * target_height / img_a.height), target_height), Image.LANCZOS)
img_b = img_b.resize((int(img_b.width * target_height / img_b.height), target_height), Image.LANCZOS)
img_c = img_c.resize((int(img_c.width * target_height / img_c.height), target_height), Image.LANCZOS)

# Create the combined image
total_width = img_a.width + img_b.width + img_c.width
combined = Image.new("RGB", (total_width, target_height), (255, 255, 255))

combined.paste(img_a, (0, 0))
combined.paste(img_b, (img_a.width, 0))
combined.paste(img_c, (img_a.width + img_b.width, 0))

# Save high-resolution versions
combined.save("Quadtune_Global_Bias_Tuning_Comparison.png", dpi=(600, 600), quality=95)
combined.save("Quadtune_Global_Bias_Tuning_Comparison.pdf", dpi=(600, 600))

print("#  Publication-quality figure saved as:")
print("   # CAM7_Global_Bias_Tuning_Comparison.png  (600 dpi)")
print("   # CAM7_Global_Bias_Tuning_Comparison.pdf")
